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
Intra- and inter-experiment models for the time it takes a single robot to
return to the nest after picking up an object.

"""
# Core packages
import pathlib
import typing as tp
import copy

# 3rd party packages
import implements
import pandas as pd
import sierra.core.models.interface
import sierra.plugins.platform.argos.variables.exp_setup as ts
from sierra.core.vector import Vector3D
from sierra.core.experiment.spec import ExperimentSpec
from sierra.core.experiment import xml
from sierra.core import types, utils, storage, config

# Project packages
import titerra.projects.fordyca_base.models.representation as rep
from titerra.projects.fordyca_base.models.density import BlockAcqDensity
from titerra.projects.fordyca_base.models.dist_measure import DistanceMeasure2D
from titerra.projects.fordyca_base.models.interference import IntraExp_RobotInterferenceRate_NRobots, IntraExp_RobotInterferenceTime_NRobots
from titerra.projects.fordyca_base.models.blocks import ExpectedAcqDist
import titerra.variables.batch_criteria as bc


def available_models(category: str):
    if category == 'intra':
        return ['IntraExp_HomingTime_1Robot']
    elif category == 'inter':
        return ['InterExp_HomingTime_1Robot',
                'InterExp_HomingTime_NRobots']
    else:
        return None


################################################################################
# Intra-experiment models
################################################################################

@implements.implements(sierra.core.models.interface.IConcreteIntraExpModel1D)
class IntraExp_HomingTime_1Robot():
    r"""Models the time it takes a robot in a swarm of size 1 to return to the nest
    after it has picked up an object during foraging during a single experiment
    within a batch.

    Only runs for swarms with :math:`\mathcal{N}=1`.

    .. IMPORTANT::
       This model does not have a kernel() function which computes the
       calculation, because it does not require ANY experimental data, and can
       be computed from first principles, so it is always OK to :method:`run()`
       it.

    From :xref:`Harwell2022a-ode`.

    """

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_exp(self,
                    criteria: bc.IConcreteBatchCriteria,
                    cmdopts: types.Cmdopts,
                    exp_num: int) -> bool:
        return criteria.populations(cmdopts)[i] == 1

    def target_csv_stems(self) -> tp.List[str]:
        return ['block-transport-time']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Homing Time']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            exp_num: int,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        # Calculate nest extent
        nest = rep.Nest(cmdopts, criteria, exp_num)

        # We calculate per-sim, rather than using the averaged block cluster
        # results, because for power law distributions different simulations
        # have different cluster locations, which affects the distribution via
        # locality.
        reader = storage.DataFrameReader('storage.csv')
        output_root = pathlib.Path(cmdopts['exp_output_root'])
        result_opaths = [output_root / d / self.main_config['sierra']['run']['run_metrics_leaf']
                         for d in output_root.iterdir()]

        cluster_df = reader(result_opaths[0] / ('block-clusters' +
                                                config.kStorageExt['csv']))

        # We calculate 1 data point for each interval
        res_df = pd.DataFrame(columns=['model'], index=cluster_df.index)
        res_df['model'] = 0.0

        for result in result_opaths:
            self._calc_for_result(criteria, exp_num, cmdopts, result, nest, res_df)

        # Average our results
        res_df['model'] /= len(result_opaths)

        # All done!
        return [res_df]

    def _calc_for_result(self,
                         criteria: bc.IConcreteBatchCriteria,
                         exp_num: int,
                         cmdopts: types.Cmdopts,
                         result_opath: pathlib.Path,
                         nest: rep.Nest,
                         res_df: pd.DataFrame):

        avg_dist = ExpectedAcqDist()(cmdopts, result_opath, nest)

        # After getting the average distance to ANY block in ANY cluster in the
        # arena, we can compute the average time, in SECONDS, that robots spend
        # returning to the nest.
        avg_homing_sec = avg_dist / float(self.config['homing_mean_speed'])

        spec = ExperimentSpec(criteria, exp_num, cmdopts)
        exp_def = xml.AttrChangeSet.unpickle(spec.exp_def_fpath)
        time_params = ts.ExpSetup.extract_time_params(exp_def)

        # Convert seconds to timesteps for displaying on graphs
        avg_homing_ts = avg_homing_sec * time_params['n_ticks_per_sec']

        # All done!
        res_df['model'] += avg_homing_ts


@implements.implements(sierra.core.models.interface.IConcreteIntraExpModel1D)
class IntraExp_HomingTime_NRobots():
    r"""Models the time it takes a robot in a swarm of :math:`\mathcal{N}` CRW
    robots to return to the nest after it has picked up an object during
    foraging during a single experiment within a batch.

    From :xref:`Harwell2022a-ode`.

    """
    @staticmethod
    def kernel(tau_h1: tp.Union[pd.DataFrame, float],
               alpha_caN: tp.Union[pd.DataFrame, float],
               tau_avN: tp.Union[pd.DataFrame, float],
               N: int) -> tp.Union[pd.DataFrame, float]:
        r"""Perform the homing time calculation.

        .. math::
           \tau_h^N = \tau_{h}^1\big[1 + \frac{\alpha_{ca}^1\tau_{av}}{\mathcal{N}}\big]

        Args:

            tau_h1: Homing time of robots in the swarm at time :math:`t`: :math:`\tau_{h}^1`.

            alpha_caNN: Robot encounter rate of robots in the swarm at time
                        :math:`t`: :math:`\alpha_{ca}^N`.

            tau_avN: Average time each robot spends in the interference state
                     beginning at time :math:`t`: :math:`\tau_{av}^N`.

            N: The number of robots in the swarm.

        Returns:

            Estimate of the steady state homing time for a swarm of
            :math:`\mathcal{N}` robots, :math:`\tau_h^N`.

        """
        return tau_h1 * (1.0 + alpha_caN * tau_avN / N)

    @staticmethod
    def calc_kernel_args(criteria: bc.IConcreteBatchCriteria,
                         exp_num: int,
                         cmdopts: types.Cmdopts,
                         main_config: types.YAMLDict,
                         model_config: types.YAMLDict) -> dict:
        homing1 = IntraExp_HomingTime_1Robot(main_config, model_config)
        tau_h1 = homing1.run(criteria, exp_num, cmdopts)[0]

        av_rateN = IntraExp_RobotInterferenceRate_NRobots(
            main_config, model_config)
        alpha_caN = av_rateN.run(criteria, exp_num, cmdopts)[0]

        av_timeN = IntraExp_RobotInterferenceTime_NRobots(
            main_config, model_config)
        tau_avN = av_timeN.run(criteria, exp_num, cmdopts)[0]

        N = criteria.populations(cmdopts)[exp_num]

        return {
            'tau_h1': tau_h1,
            'alpha_caN': alpha_caN,
            'tau_avN': tau_avN,
            'N': N
        }

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_exp(self,
                    criteria: bc.IConcreteBatchCriteria,
                    cmdopts: types.Cmdopts,
                    exp_num: int) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['block-transport-time']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Homing Time']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            exp_num: int,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        reader = storage.DataFrameReader('storage.csv')
        ipath = pathlib.Path(cmdopts['exp_stat_root'],
                             'block-clusters' + config.kStats['mean'].exts['mean'])
        cluster_df = reader(ipath)

        # We calculate 1 data point for each interval
        res_df = pd.DataFrame(columns=['model'], index=cluster_df.index)
        kargs = self.calc_kernel_args(
            criteria, exp_num, cmdopts, self.main_config, self.config)
        res_df['model'] = self.kernel(**kargs)

        # All done!
        return [res_df]


################################################################################
# Inter-experiment models
################################################################################

@implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_HomingTime_NRobots():
    r"""Models the time it takes a robot to return to the nest after it has picked
    up an object during foraging across all experiments in the batch.

    .. IMPORTANT:: This model does not have a kernel() function which computes
       the calculation, because it is a summary model, built on simpler
       intra-experiment models.

    From :xref:`Harwell2022a-ode`.

    """

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict) -> None:
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['block-transport-time-cum-avg']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Homing Time']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:
        dirs = criteria.gen_exp_names(cmdopts)
        res_df = pd.DataFrame(columns=dirs, index=[0])

        batch_input_root = pathlib.Path(cmdopts['batch_input_root'])
        batch_output_root = pathlib.Path(cmdopts['batch_output_root'])
        batch_model_root = pathlib.Path(cmdopts['batch_model_root'])
        batch_graph_root = pathlib.Path(cmdopts['batch_graph_root'])
        batch_stat_root = pathlib.Path(cmdopts['batch_stat_root'])

        for i, exp in enumerate(dirs):
            # Setup cmdopts for intra-experiment model
            cmdopts2 = copy.deepcopy(cmdopts)
            cmdopts2["exp0_output_root"] = str(batch_output_root / dirs[0])
            cmdopts2["exp0_stat_root"] = str(batch_stat_root / dirs[0])

            cmdopts2["exp_input_root"] = str(batch_input_root / exp)
            cmdopts2["exp_output_root"] = str(batch_output_root / exp)
            cmdopts2["exp_graph_root"] = str(batch_graph_root / exp)
            cmdopts2["exp_stat_root"] = str(batch_stat_root / exp)
            cmdopts2["exp_model_root"] = str(batch_model_root / exp)

            utils.dir_create_checked(cmdopts2['exp_model_root'], exist_ok=True)

            # Model only targets a single graph
            intra_df = IntraExp_HomingTime_NRobots(self.main_config,
                                                   self.config).run(criteria,
                                                                    i,
                                                                    cmdopts2)[0]
            # Last datapoint is the closest to the steady state value
            # (presumably) so we select it
            # to use as our prediction for the experiment within the batch.
            res_df[exp] = intra_df.loc[intra_df.index[-1], 'model']

        return [res_df]
