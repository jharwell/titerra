# Copyright 2020 John Harwell, All rights reserved.
#
#  This file is part of SIERRA.
#
#  SIERRA is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  SIERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  SIERRA.  If not, see <http://www.gnu.org/licenses/
"""
Free block acquisition and block collection models for the FORDYCA project.
"""

# Core packages
import os
import copy
import typing as tp
import math

# 3rd party packages
import implements
import pandas as pd

# Project packages
import sierra.core.models.interface
from sierra.core.experiment.spec import ExperimentSpec
import titerra.projects.fordyca_base.models.representation as rep
import sierra.core.variables.batch_criteria as bc
from sierra.core.vector import Vector3D
from sierra.core.xml import XMLAttrChangeSet
from sierra.core import types, storage, utils
import sierra.plugins.platform.argos.variables.exp_setup as ts

from titerra.projects.fordyca_base.models.density import BlockAcqDensity
from titerra.projects.fordyca_base.models.dist_measure import DistanceMeasure2D
import titerra.projects.fordyca_base.models.diffusion as diffusion


def available_models(category: str):
    if category == 'intra':
        return ['IntraExp_AcqRate_NRobots', 'IntraExp_BlockCollectionRate_NRobots']
    elif category == 'inter':
        return ['InterExp_BlockCollectionRate_NRobots',
                'InterExp_AcqRate_NRobots']
    else:
        return None

################################################################################
# Intra-experiment models
################################################################################


@implements.implements(sierra.core.models.interface.IConcreteIntraExpModel1D)
class IntraExp_BlockAcqRate_NRobots():
    """
    Models the steady state block acquisition rate of a swarm of N CRW robots.

    .. IMPORTANT::

       This model does not have a kernel() function which computes the
       calculation, because it does not require ANY experimental data, and can
       be computed from first principles, so it is always OK to :method:`run()`
       it.

    From :xref:`Harwell2021b`.

    """
    @staticmethod
    def _kernel(N: float,
                wander_speed: float,
                ticks_per_sec: int,
                avg_acq_dist: float,
                scenario: str) -> float:
        """
        Calculates the CRW Diffusion constant in :xref:`Harwell2021b` for
        bounded arena geometry, inspired by the results in :xref:`Codling2010`.
        """
        D = diffusion.crwD_for_searching(N=N,
                                         wander_speed=wander_speed,
                                         ticks_per_sec=ticks_per_sec,
                                         scenario=scenario)

        diff_time = avg_acq_dist ** 2 / (2 * D)

        # Inverse of diffusion time from nest to expected acquisition location
        # is alpha_b
        return 1.0 / diff_time

    def __init__(self,
                 main_config: types.YAMLDict,
                 config: types.YAMLDict) -> None:
        self.main_config = main_config
        self.config = config

    def run_for_exp(self, criteria: bc.IConcreteBatchCriteria, cmdopts: types.Cmdopts, i: int) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['block-manip-events-free-pickup']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Block Acquisition Rate']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            exp_num: int,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        result_opath = os.path.join(cmdopts['exp_stat_root'])

        # We calculate per-sim, rather than using the averaged block cluster
        # results, because for power law distributions different simulations
        # have different cluster locations, which affects the distribution via
        # locality.
        #
        # For all other block distributions, we can operate on the averaged
        # results, because the position of block clusters is the same in all
        # simulations.
        if 'PL' in cmdopts['scenario']:
            result_opaths = [os.path.join(cmdopts['exp_output_root'],
                                          d,
                                          self.main_config['sierra']['run']['run_metrics_leaf'])
                             for d in os.listdir(cmdopts['exp_output_root'])]
        else:
            result_opaths = [os.path.join(cmdopts['exp_stat_root'])]

        nest = rep.Nest(cmdopts, criteria, exp_num)

        dist = 0.0
        for result in result_opaths:
            dist += ExpectedAcqDist()(cmdopts, result, nest)

        # Average our results
        avg_acq_dist = dist / len(result_opaths)
        n_robots = criteria.populations(cmdopts)[exp_num]

        spec = ExperimentSpec(criteria, exp_num, cmdopts)
        exp_def = XMLAttrChangeSet.unpickle(spec.exp_def_fpath)
        time_params = ts.ExpSetup.extract_time_params(exp_def)

        alpha_b = self._kernel(N=n_robots,
                               wander_speed=float(
                                   self.config['wander_mean_speed']),
                               ticks_per_sec=time_params['n_ticks_per_sec'],
                               avg_acq_dist=avg_acq_dist,
                               scenario=cmdopts['scenario'])

        rate_df = storage.DataFrameReader('storage.csv')(
            os.path.join(result_opath, 'block-manipulation.csv'))

        # We calculate 1 data point for each interval
        res_df = pd.DataFrame(columns=['model'], index=rate_df.index)
        res_df['model'] = alpha_b

        # All done!
        return [res_df]


@implements.implements(sierra.core.models.interface.IConcreteIntraExpModel1D)
class IntraExp_BlockCollectionRate_NRobots():
    """
    Models the steady state block collection rate :math:`L_{b}` of the swarm of CRW robots using
    Little's law and :class:`IntraExp_BlockAcqRate_NRobots`. Makes the following assumptions:

    - The reported homing time includes a non-negative penalty :math:`\mu_{b}` assessed in the nest
      which robots must serve before collection can complete. This models physical time taken to
      actually drop the block, and other environmental factors.

    - At most 1 robot can drop an object per-timestep (i.e. an M/M/1 queue).
    """

    @staticmethod
    def kernel(alpha_bN: tp.Union[pd.DataFrame, float],
               mu_bN: tp.Union[pd.DataFrame, float]) -> tp.Union[pd.DataFrame, float]:
        r"""
        Perform the block collection rate calculation using Little's Law. We want to find the
        average # of customers being served--this is the rate of robots leaving the homing queue as
        they deposit their blocks in the nest.

        .. math::
           L_{b} = \frac{\alpha_b}{\mu_b}

        where :math:`L_s` is the average number of customers being served each timestep :math:`t`.

        Args:
            alpha_bN: Rate of robots in the swarm encountering blocks at time :math:`t`:
                      :math:`\alpha_{b}`.

            mu_bN: The average penalty in timesteps that a robot from a swarm of size
                   :math:`\mathcal{N}` dropping an object in the nest at time :math:`t` will be
                   subjected to before collection occurs.

        Returns:
            Estimate of the steady state rate of block collection, :math:`L_{b}`.

        """
        return alpha_bN / mu_bN

    @staticmethod
    def calc_kernel_args(criteria:  bc.IConcreteBatchCriteria,
                         exp_num: int,
                         cmdopts: types.Cmdopts,
                         main_config: types.YAMLDict,
                         config: types.YAMLDict):
        block_manip_df = storage.DataFrameReader('storage.csv')(os.path.join(cmdopts['exp_stat_root'],
                                                                             'block-manipulation.csv'))

        # Calculate acquisition rate
        alpha_bN = IntraExp_BlockAcqRate_NRobots(main_config, config).run(criteria,
                                                                          exp_num,
                                                                          cmdopts)[0]

        # FIXME: In the future, this will be another model, rather than being read from experimental
        # data.
        mu_bN = block_manip_df['cum_avg_free_drop_penalty']

        return {
            'alpha_bN': alpha_bN,
            'mu_bN': mu_bN
        }

    def __init__(self,
                 main_config: types.YAMLDict,
                 config: types.Cmdopts) -> None:
        self.main_config = main_config
        self.config = config

    def run_for_exp(self,
                    criteria: bc.IConcreteBatchCriteria,
                    cmdopts: types.Cmdopts,
                    i: int) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['block-manip-events-free-drop']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Block Collection Rate']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            exp_num: int,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:
        rate_df = storage.DataFrameReader('storage.csv')(os.path.join(cmdopts['exp_stat_root'],
                                                                      'block-manipulation.csv'))

        # We calculate 1 data point for each interval
        res_df = pd.DataFrame(columns=['model'], index=rate_df.index)
        kargs = self.calc_kernel_args(
            criteria, exp_num, cmdopts, self.main_config, self.config)
        res_df['model'] = self.kernel(**kargs)

        # All done!
        return [res_df]

################################################################################
# Inter-experiment models
################################################################################


@implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_BlockAcqRate_NRobots():
    """
    Models the steady state block acquisition rate of the swarm, assuming purely reactive robots.
    That is, one model datapoint is computed for each experiment within the batch.

    .. IMPORTANT::
       This model does not have a kernel() function which computes the calculation, because
       it is a summary model, built on simpler intra-experiment models.
    """

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['block-manip-free-pickup-events-cum-avg']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Block Acquisition Rate']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        dirs = criteria.gen_exp_dirnames(cmdopts)
        res_df = pd.DataFrame(columns=dirs, index=[0])

        for i, exp in enumerate(dirs):

            # Setup cmdopts for intra-experiment model
            cmdopts2 = copy.deepcopy(cmdopts)

            cmdopts2["exp0_output_root"] = os.path.join(
                cmdopts["batch_output_root"], dirs[0])
            cmdopts2["exp0_stat_root"] = os.path.join(
                cmdopts["batch_stat_root"], dirs[0])

            cmdopts2["exp_input_root"] = os.path.join(
                cmdopts['batch_input_root'], exp)
            cmdopts2["exp_output_root"] = os.path.join(
                cmdopts['batch_output_root'], exp)
            cmdopts2["exp_graph_root"] = os.path.join(
                cmdopts['batch_graph_root'], exp)
            cmdopts2["exp_stat_root"] = os.path.join(
                cmdopts["batch_stat_root"], exp)
            cmdopts2["exp_model_root"] = os.path.join(
                cmdopts['batch_model_root'], exp)
            utils.dir_create_checked(
                cmdopts2['exp_model_root'], exist_ok=True)

            # Model only targets a single graph
            intra_df = IntraExp_BlockAcqRate_NRobots(self.main_config,
                                                     self.config).run(criteria,
                                                                      i,
                                                                      cmdopts2)[0]
            res_df[exp] = intra_df.loc[intra_df.index[-1], 'model']

        # All done!
        return [res_df]


@implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_BlockCollectionRate_NRobots():
    """
    Models the steady state block collection rate of the CRW swarm.

    .. IMPORTANT::
       This model does not have a kernel() function which computes the calculation, because
       it is a summary model, built on simpler intra-experiment models.

    """

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['blocks-transported-cum-avg']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Block Collection Rate']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        dirs = criteria.gen_exp_dirnames(cmdopts)
        res_df = pd.DataFrame(columns=dirs, index=[0])

        for i, exp in enumerate(dirs):

            # Setup cmdopts for intra-experiment model
            cmdopts2 = copy.deepcopy(cmdopts)

            cmdopts2["exp0_output_root"] = os.path.join(
                cmdopts["batch_output_root"], dirs[0])
            cmdopts2["exp0_stat_root"] = os.path.join(
                cmdopts["batch_stat_root"], dirs[0])

            cmdopts2["exp_input_root"] = os.path.join(
                cmdopts['batch_input_root'], exp)
            cmdopts2["exp_output_root"] = os.path.join(
                cmdopts['batch_output_root'], exp)
            cmdopts2["exp_graph_root"] = os.path.join(
                cmdopts['batch_graph_root'], exp)
            cmdopts2["exp_stat_root"] = os.path.join(
                cmdopts["batch_stat_root"], exp)
            cmdopts2["exp_model_root"] = os.path.join(
                cmdopts['batch_model_root'], exp)
            utils.dir_create_checked(
                cmdopts2['exp_model_root'], exist_ok=True)

            # Model only targets a single graph
            intra_df = IntraExp_BlockCollectionRate_NRobots(self.main_config,
                                                            self.config).run(criteria,
                                                                             i,
                                                                             cmdopts2)[0]
            res_df[exp] = intra_df.loc[intra_df.index[-1], 'model']

        # All done!
        return [res_df]

################################################################################
# Helper Classes
################################################################################


class ExpectedAcqDist():
    def __call__(self, cmdopts: types.Cmdopts, result_opath: str, nest: rep.Nest) -> float:

        # Get clusters in the arena
        clusters = rep.BlockClusterSet(cmdopts, nest, result_opath)

        # Integrate to find average distance from nest to all clusters, weighted by acquisition
        # density.
        dist = 0.0
        for cluster in clusters:
            dist += self._nest_to_cluster(cluster, nest, cmdopts['scenario'])

        return dist / len(clusters)

    def _nest_to_cluster(self,
                         cluster: rep.BlockCluster,
                         nest: rep.Nest,
                         scenario: str) -> float:
        dist_measure = DistanceMeasure2D(scenario, nest=nest)

        density = BlockAcqDensity(
            nest=nest, cluster=cluster, dist_measure=dist_measure)

        # Compute expected value of X coordinate of average distance from nest to acquisition
        # location.
        ll = cluster.extent.ll
        ur = cluster.extent.ur
        evx = density.evx_for_region(ll=ll, ur=ur)

        # Compute expected value of Y coordinate of average distance from nest to acquisition
        # location.
        evy = density.evy_for_region(ll=ll, ur=ur)

        # Compute expected distance from nest to block acquisitions
        return dist_measure.to_nest(Vector3D(evx, evy))
