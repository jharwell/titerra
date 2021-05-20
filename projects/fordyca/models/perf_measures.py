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
Inter-experiment models for some of the performance measures the SIERRA core supports.
"""
# Core packages
import os
import typing as tp
import copy
import math

# 3rd party packages
import implements
import pandas as pd

# Project packages
import sierra.core.models.interface
import sierra.core.utils
import sierra.core.variables.batch_criteria as bc
from sierra.core.vector import Vector3D
from sierra.core.perf_measures.scalability import SteadyStateParallelFractionUnivar
from sierra.core.perf_measures.self_organization import SteadyStateFLMarginalUnivar
import sierra.core.perf_measures.common as cpmcommon

import projects.fordyca.models.representation as rep
from projects.fordyca.models.density import BlockAcqDensity
from projects.fordyca.models.dist_measure import DistanceMeasure2D
from projects.fordyca.models.blocks import IntraExp_BlockAcqRate_NRobots


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

    def __init__(self, main_config: tp.Dict[str, tp.Any], config: tp.Dict[str, tp.Any]):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: tp.Dict[str, tp.Any]) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['PM-raw']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Blocks Transported']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: tp.Dict[str, tp.Any]) -> tp.List[pd.DataFrame]:

        dirs = criteria.gen_exp_dirnames(cmdopts)
        res_df = pd.DataFrame(columns=dirs, index=[0])

        for i, exp in enumerate(dirs):

            # Setup cmdopts for intra-experiment model
            cmdopts2 = copy.deepcopy(cmdopts)

            cmdopts2["exp0_output_root"] = os.path.join(cmdopts["batch_output_root"], dirs[0])
            cmdopts2["exp0_stat_root"] = os.path.join(cmdopts["batch_stat_root"], dirs[0])

            cmdopts2["exp_input_root"] = os.path.join(cmdopts['batch_input_root'], exp)
            cmdopts2["exp_output_root"] = os.path.join(cmdopts['batch_output_root'], exp)
            cmdopts2["exp_graph_root"] = os.path.join(cmdopts['batch_graph_root'], exp)
            cmdopts2["exp_stat_root"] = os.path.join(cmdopts["batch_stat_root"], exp)
            cmdopts2["exp_model_root"] = os.path.join(cmdopts['batch_model_root'], exp)
            sierra.core.utils.dir_create_checked(cmdopts2['exp_model_root'], exist_ok=True)

            # Model only targets a single graph
            intra_df = IntraExp_BlockAcqRate_NRobots(self.main_config,
                                                     self.config).run(criteria,
                                                                      i,
                                                                      cmdopts2)[0]

            res_df[exp] = intra_df.loc[intra_df.index[-1], 'model']

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
               cmdopts: tp.Dict[str, tp.Any],
               perf_df: pd.DataFrame) -> pd.DataFrame:
        return SteadyStateParallelFractionUnivar.df_kernel(criteria, cmdopts, perf_df)

    def __init__(self, main_config: tp.Dict[str, tp.Any], config: tp.Dict[str, tp.Any]):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: tp.Dict[str, tp.Any]) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['PM-scalability-parallel-frac']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Parallel Fraction']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: tp.Dict[str, tp.Any]) -> tp.List[pd.DataFrame]:

        perf_df = InterExp_RawPerf_NRobots(self.main_config, self.config).run(criteria,
                                                                              cmdopts)[0]

        sc_df = self.kernel(criteria, cmdopts, perf_df)

        # All done!
        return [sc_df]


@implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_SelfOrg_NRobots():
    r"""
    Models the emergent self-organization achieved by a swarm of :math:`\mathcal{N}` CRW robots via
    marginal fractional losses.
    """

    @staticmethod
    def kernel(criteria: bc.IConcreteBatchCriteria,
               cmdopts: tp.Dict[str, tp.Any],
               perf_df: pd.DataFrame,
               N_av: pd.DataFrame) -> pd.DataFrame:
        plostN = cpmcommon.SteadyStatePerfLostInteractiveSwarmUnivar.df_kernel(criteria,
                                                                               cmdopts,
                                                                               N_av,
                                                                               perf_df)
        fl = cpmcommon.SteadyStateFLUnivar.df_kernel(criteria, perf_df, plostN)
        return SteadyStateFLMarginalUnivar.df_kernel(criteria, cmdopts, fl)

    def __init__(self, main_config: tp.Dict[str, tp.Any], config: tp.Dict[str, tp.Any]):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self, criteria: bc.IConcreteBatchCriteria, cmdopts: tp.Dict[str, tp.Any]) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['PM-self-org-mfl']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Emergent Self-Organization']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            cmdopts: tp.Dict[str, tp.Any]) -> tp.List[pd.DataFrame]:

        perf_df = InterExp_RawPerf_NRobots(self.main_config, self.config).run(criteria,
                                                                              cmdopts)[0]

        int_count_ipath = os.path.join(cmdopts["batch_stat_collate_root"],
                                       self.main_config['perf']['interference_count_csv'])
        interference_df = sierra.core.utils.pd_csv_read(int_count_ipath)
        so_df = self.kernel(criteria, cmdopts, perf_df, interference_df)

        # All done!
        return [so_df]
