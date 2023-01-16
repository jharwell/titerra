# Copyright 2020 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

"""
Inter-experiment models for some of the performance measures the SIERRA core
supports.
"""
# Core packages
import pathlib
import typing as tp
import copy

# 3rd party packages
import implements
import pandas as pd
from sierra.core import types, utils, config, models, stat_kernels

# Project packages
import titerra.projects.common.perf_measures.common as pmcommon
from titerra.projects.common.perf_measures.scalability import SteadyStateParallelFractionUnivar
from titerra.projects.common.perf_measures.self_organization import SteadyStateFLMarginalUnivar

from titerra.projects.fordyca_base.models.blocks import IntraExp_BlockAcqRate_NRobots
import titerra.variables.batch_criteria as bc


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


@implements.implements(models.interface.IConcreteInterExpModel1D)
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

            utils.dir_create_checked(cmdopts2['exp_model_root'],
                                     exist_ok=True)

            # Model only targets a single graph
            intra_df = IntraExp_BlockAcqRate_NRobots(self.main_config,
                                                     self.config).run(criteria,
                                                                      i,
                                                                      cmdopts2)[0]
            res_df[exp] = intra_df['model'].iloc[-1]

        # All done!
        return [res_df]


@implements.implements(models.interface.IConcreteInterExpModel1D)
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

        dist_dfs = stat_kernels.mean.from_pm(sc_dfs)
        joined = pmcommon.univar_distribution_prepare_join(cmdopts,
                                                           criteria,
                                                           dist_dfs,
                                                           True)
        # All done!
        return [joined[config.kStats['mean'].exts['mean']]]


@implements.implements(models.interface.IConcreteInterExpModel1D)
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

        dist_dfs = stat_kernels.mean.from_pm(so_dfs)
        joined = pmcommon.univar_distribution_prepare_join(cmdopts,
                                                           criteria,
                                                           dist_dfs,
                                                           True)
        # All done!
        return [joined[config.kStats['mean'].exts['mean']]]


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
    exp_dirs = utils.exp_range_calc(cmdopts,
                                    cmdopts['batch_stat_collate_root'],
                                    criteria)
    exp_names = [d.name for d in exp_dirs]

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

    for d in exp_names:
        dfs_mock[d] = pd.DataFrame(index=range(
            len(interference_dfs[exps[0]][sims[0]])))

    for d in exp_names:
        for s in sims:
            dfs_mock[d][s] = prediction.loc[prediction.index[-1], d]

    return dfs_mock
