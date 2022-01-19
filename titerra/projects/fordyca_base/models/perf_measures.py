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
Inter-experiment models for some of the performance measures the SIERRA core
supports.
"""
# Core packages
import os
import typing as tp
import copy

# 3rd party packages
import implements
import pandas as pd
import sierra.core.models.interface
import sierra.core.utils
import sierra.core.config
import sierra.core.variables.batch_criteria as bc
from sierra.core.vector import Vector3D
from sierra.core import types
import sierra.core.stat_kernels

# Project packages
import titerra.projects.common.perf_measures.common as pmcommon
from titerra.projects.common.perf_measures.scalability import SteadyStateParallelFractionUnivar
from titerra.projects.common.perf_measures.self_organization import SteadyStateFLMarginalUnivar

import titerra.projects.fordyca_base.models.representation as rep
from titerra.projects.fordyca_base.models.density import BlockAcqDensity
from titerra.projects.fordyca_base.models.dist_measure import DistanceMeasure2D
from titerra.projects.fordyca_base.models.blocks import IntraExp_BlockAcqRate_NRobots


def available_models(category: str):
    if category == 'intra':
        return []
    elif category == 'inter':
        return ['InterExp_RawPerf_NRobots',
                'InterExp_Scalability_NRobots',
                'InterExp_SelfOrg_NRobots']
    else:
        return None

################################################################################
# Intra-experiment models
################################################################################


################################################################################
# Inter-experiment models
################################################################################


@implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_RawPerf_NRobots():
    r"""
    Models the raw performances achieved by a swarm of :math:`\mathcal{N}` CRW robots.
    """

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['PM-ss-raw']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Blocks Transported']

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
            sierra.core.utils.dir_create_checked(
                cmdopts2['exp_model_root'], exist_ok=True)

            # Model only targets a single graph
            intra_df = IntraExp_BlockAcqRate_NRobots(self.main_config,
                                                     self.config).run(criteria,
                                                                      i,
                                                                      cmdopts2)[0]
            res_df[exp] = intra_df['model'].iloc[-1]

        # All done!
        return [res_df]


@implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_Scalability_NRobots():
    r"""
    Models the scalability achieved by a swarm of :math:`\mathcal{N}` CRW robots via parallel
    fraction.
    """

    @staticmethod
    def kernel(criteria: bc.IConcreteBatchCriteria,
               cmdopts: types.Cmdopts,
               perf_df: pd.DataFrame) -> pd.DataFrame:
        return SteadyStateParallelFractionUnivar.df_kernel(criteria, cmdopts, perf_df)

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['PM-ss-scalability-parallel-frac']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Parallel Fraction']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        perf_df = InterExp_RawPerf_NRobots(self.main_config, self.config).run(criteria,
                                                                              cmdopts)[0]

        perf_dfs_mock = _mock_distribution_gen(
            criteria, self.main_config, cmdopts, perf_df)

        sc_dfs = self.kernel(criteria, cmdopts, perf_dfs_mock)

        dist_dfs = sierra.core.stat_kernels.mean.from_pm(sc_dfs)
        joined = pmcommon.univar_distribution_prepare_join(cmdopts,
                                                           criteria,
                                                           dist_dfs,
                                                           True)
        # All done!
        return [joined[sierra.core.config.kStatsExtensions['mean']]]


@implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_SelfOrg_NRobots():
    r"""
    Models the emergent self-organization achieved by a swarm of :math:`\mathcal{N}` CRW robots via
    marginal fractional losses.
    """

    @staticmethod
    def kernel(criteria: bc.IConcreteBatchCriteria,
               cmdopts: types.Cmdopts,
               perf_dfs: tp.Dict[str, pd.DataFrame],
               N_av: tp.Dict[str, pd.DataFrame]) -> pd.DataFrame:
        plostN = pmcommon.SteadyStatePerfLostInteractiveSwarmUnivar.df_kernel(criteria,
                                                                              cmdopts,
                                                                              N_av,
                                                                              perf_dfs)
        fl = pmcommon.SteadyStateFLUnivar.df_kernel(criteria, perf_dfs, plostN)
        return SteadyStateFLMarginalUnivar.df_kernel(criteria, cmdopts, fl)

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['PM-ss-self-org-mfl']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Emergent Self-Organization']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        perf_df = InterExp_RawPerf_NRobots(self.main_config, self.config).run(criteria,
                                                                              cmdopts)[0]

        perf_dfs_mock = _mock_distribution_gen(
            criteria, self.main_config, cmdopts, perf_df)

        # Just needed to extract simulation names/n_sims
        interference_leaf = self.main_config['sierra']['perf']['intra_interference_csv'].split('.')[
            0]
        interference_col = self.main_config['sierra']['perf']['intra_interference_col']

        interference_dfs = pmcommon.gather_collated_sim_dfs(cmdopts,
                                                            criteria,
                                                            interference_leaf,
                                                            interference_col)

        so_dfs = self.kernel(criteria, cmdopts, perf_dfs_mock, interference_dfs)

        dist_dfs = sierra.core.stat_kernels.mean.from_pm(so_dfs)
        joined = pmcommon.univar_distribution_prepare_join(cmdopts,
                                                           criteria,
                                                           dist_dfs,
                                                           True)
        # All done!
        return [joined[sierra.core.config.kStatsExtensions['mean']]]


def _mock_distribution_gen(criteria: bc.IConcreteBatchCriteria,
                           main_config: types.YAMLDict,
                           cmdopts: types.Cmdopts,
                           prediction: pd.DataFrame) -> tp.Dict[str, pd.DataFrame]:
    """
    The TITAN performance measures expect a distribution of simulation data as
    input, in the form of a dictionary of (experiment name, dataframe)
    pairs. The dataframe must have temporal columns for each simulation (i.e.,
    no truncating to steady state yet). To generate predictions of *steady
    state* performance measures, we generate a mock distribution of the
    necessary shape here.

    """
    exp_dirs = sierra.core.utils.exp_range_calc(cmdopts, '', criteria)

    # Just needed to extract simulation names/n_sims
    interference_leaf = main_config['sierra']['perf']['intra_interference_csv'].split('.')[
        0]
    interference_col = main_config['sierra']['perf']['intra_interference_col']

    interference_dfs = pmcommon.gather_collated_sim_dfs(cmdopts,
                                                        criteria,
                                                        interference_leaf,
                                                        interference_col)

    dfs_mock = {}
    exps = list(interference_dfs.keys())
    sims = interference_dfs[exps[0]].columns

    for d in exp_dirs:
        dfs_mock[d] = pd.DataFrame(index=range(
            len(interference_dfs[exps[0]][sims[0]])))

    for d in exp_dirs:
        for s in sims:
            dfs_mock[d][s] = prediction.loc[prediction.index[-1], d]

    return dfs_mock
