# Copyright 2020 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

"""Intra- and inter-experiment models for the time a robots spends avoiding
interference and the rate at which a robot experiences interference.

"""
# Core packages
import pathlib
import copy
import typing as tp

# 3rd party packages
import implements
import pandas as pd
import sierra.core.models.interface
from sierra.core import types, utils, storage, config

# Project packages
import titerra.variables.batch_criteria as bc


def available_models(category: str):
    if category == 'intra':
        return ['IntraExp_WallInterferenceRate_1Robot',
                'IntraExp_RobotInterferenceRate_NRobots',
                'IntraExp_RobotInterferenceTime_NRobots']
    elif category == 'inter':
        return ['InterExp_RobotInterferenceRate_NRobots',
                'InterExp_RobotInterferenceTime_NRobots']
    else:
        return None

################################################################################
# Intra-experiment models
################################################################################


@implements.implements(sierra.core.models.interface.IConcreteIntraExpModel1D)
class IntraExp_WallInterferenceRate_1Robot():
    r"""
    Models the steady state interference rate of a CRW swarm of size 1. Robots are in 1 of 4 states
    via their FSM: exploring, homing, or avoiding collision while exploring/homing, which we model
    as a queueing network, in which robots enter the interference queue when sense a nearby wall,
    and exit it sometime later. We know:

    - The average amount of time a robot spends in the interference queue from empirical data.
    - The average number of robots in the interference queue from empirical data.

    From this, we can use Little's Law to compute the arrival rate for the queue, which is the
    interference rate for the swarm.

    This model has a `:meth:`kernel()` function which computes the calculation, enabling this
    model to be used as a building block without necessarily needing to be :meth:`run()`.

    Only :method:`run()`s for swarms with :math:`\mathcal{N}=1`.

    .. IMPORTANT::
       :method:`run`() currently reads the following from experimental data:

       - :math:`\tau_{av}^1`
       - :math:`\tau_{ca}^1`

    From :xref:`Harwell2022a-ode`.

    """
    @staticmethod
    def kernel(N_av1: tp.Union[pd.DataFrame, float],
               tau_av1: tp.Union[pd.DataFrame, float]) -> tp.Union[pd.DataFrame, float]:
        r"""Perform the interference rate calculation using Little's Law, modeling CRW
        robots entering/exiting an interference avoidance state using a two
        state queueing network: robots are either experiencing interference or
        are doing something else.

        .. math::
           \alpha_{r}^1 = \frac{\tau_{av}}{\mathcal{N}_{av}(t)}

        Args:

            N_av1: Number of robots in the swarm which are experiencing
            interference at time :math:`t`: :math:`\mathcal{N}_{av}(t)`.

            tau_av1: Average time each robot spends in the interference state
                     beginning at time :math:`t`: :math:`\tau_{av}^1`.

        Returns:

            Estimate of the steady state rate of robots entering the
            interference queue, :math:`\alpha_{ca}^1`.

        """
        # All robots can enter the avoidance queue, so we don't need to modify
        # lambda according to the # of contributing robots.
        return N_av1 / tau_av1

    @staticmethod
    def calc_kernel_args(exp_stat_root: pathlib.Path) -> tp.Dict[str,
                                                                 pd.DataFrame]:
        reader = storage.DataFrameReader('storage.csv')
        fsm_counts_df = reader(exp_stat_root / ('fsm-interference-counts' +
                                                config.kStats['mean'].exts['mean']))
        return {
            'N_av1': fsm_counts_df['cum_avg_exp_interference'],
            'tau_av1': fsm_counts_df['cum_avg_interference_duration']
        }

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_exp(self,
                    criteria: bc.IConcreteBatchCriteria,
                    cmdopts: types.Cmdopts,
                    exp_num: int) -> bool:
        return criteria.populations(cmdopts)[i] == 1

    def target_csv_stems(self) -> tp.List[str]:
        return ['fsm-interference-counts']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Interference Rate']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            exp_num: int,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        reader = storage.DataFrameReader('storage.csv')
        stat_root = pathlib.Path(cmdopts['exp_stat_root'])

        fsm_df = reader(stat_root / ('fsm-interference-counts' +
                                     config.kStats['mean'].exts['mean']))

        # We calculate 1 data point for each interval
        res_df = pd.DataFrame(columns=['model'], index=fsm_df.index)

        # Calculate kernel arguments
        kargs = self.calc_kernel_args(pathlib.Path(cmdopts['exp_stat_root']))

        # Run kernel on our results
        res_df['model'] = self.kernel(**kargs)

        # All done!
        return [res_df]


@implements.implements(sierra.core.models.interface.IConcreteIntraExpModel1D)
class IntraExp_RobotInterferenceRate_NRobots():
    r"""Models the steady state inter-robot interference rate of a swarm of
    :math:`\mathcal{N}` CRW robots. Robots are in 1 of 4 states via their FSM:
    exploring, homing, or avoiding collision while avoiding/homing, which we
    model as a queueing network, in which robots enter the interference queue
    when sense a nearby they sense a nearby wall, and exit it sometime later. We
    know:

    - The average amount of time a robot spends in the interference queue from
      empirical data.

    - The average number of robots in the interference queue from empirical
      data.

    From this, we can use Little's Law to compute the arrival rate for the
    queue, which is the interference rate for the swarm.

    This model has a `:meth:`kernel()` function which computes the calculation,
    enabling this model to be used as a building block without necessarily
    needing to be :meth:`run()`.

    .. IMPORTANT::
       :method:`run`() currently reads the following from experimental data:

       - :math:`\tau_{av}^N`
       - :math:`\tau_{ca}^N`

    From :xref:`Harwell2022a-ode`.

    """
    @staticmethod
    def kernel(N_av1: tp.Union[pd.DataFrame, float],
               tau_av1: tp.Union[pd.DataFrame, float],
               N_avN: tp.Union[pd.DataFrame, float],
               tau_avN: tp.Union[pd.DataFrame, float]):
        r"""Perform the interference rate calculation using Little's Law, modeling CRW
        robots entering/exiting an interference avoidance state using a two
        state queueing network: robots are either experiencing interference or
        are doing something else.

        For 1 robot, the rate is the rate of a single robot experiencing
        interference near arena walls; we want the rate of robots encountering
        other robots, so we correct for this with a linear factor.

        .. math::
           \alpha_{ca}^N = \frac{\tau_{av}}{\mathcal{N}_{av}(t)} - \alpha_{ca}^1\mathcal{N}_{av}(t)

        Args:

            N_av1: Fraction of robots in a swarm of size 1 which are
                   experiencing interference at time :math:`t`:
                   :math:`\mathcal{N}_{av}(t)`.

            tau_av1: Average time each robot in a swarm of size 1 spends in the
                     interference queue beginning at time :math:`t`:
                     :math:`\tau_{av}^1`.

            N_avN: Number of robots in a swarm of size :math:`\mathcal{N}` which
                   are experiencing interference at time :math:`t`:
                   :math:`\mathcal{N}_{av}(t)`.

            tau_avN: Average time each robot in a swarm of size
                     :math:`\mathcal{N}` spends in the interference state
                     beginning at time :math:`t`: :math:`\tau_{av}`.

        Returns:

            Estimate of the steady state rate of robots from a swarm of
            :math:`\mathcal{N}` robots entering the interference queue,
            :math:`\alpha_{ca}^N`.

        """
        alpha_ca1 = IntraExp_WallInterferenceRate_1Robot.kernel(
            N_av1=N_av1, tau_av1=tau_av1)

        # All robots can enter the avoidance queue, so we don't need to modify
        # lambda according to the # of contributing robots.
        return N_avN / tau_avN - alpha_ca1 * N_avN

    @staticmethod
    def calc_kernel_args(criteria: bc.IConcreteBatchCriteria,
                         exp_num: int,
                         cmdopts: types.Cmdopts) -> tp.Dict[str, pd.DataFrame]:
        # Calculate kernel args for the 1 robot case
        result0_stat_root = pathlib.Path(cmdopts['exp0_stat_root'])
        kargs = IntraExp_WallInterferenceRate_1Robot.calc_kernel_args(
            result0_stat_root)

        # Add additional args for N robot case
        resultN_stat_root = pathlib.Path(cmdopts['exp_stat_root'])
        ipath = resultN_stat_root / ('fsm-interference-counts' +
                                     config.kStats['mean'].exts['mean'])
        reader = storage.DataFrameReader('storage.csv')
        fsm_countsN_df = reader(ipath)

        kargs['N_avN'] = fsm_countsN_df['cum_avg_exp_interference']
        kargs['tau_avN'] = fsm_countsN_df['cum_avg_interference_duration']

        return kargs

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_exp(self,
                    criteria: bc.IConcreteBatchCriteria,
                    cmdopts: types.Cmdopts,
                    exp_num: int) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['fsm-interference-counts']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Interference Rate']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            exp_num: int,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        reader = storage.DataFrameReader('storage.csv')

        stat_root = pathlib.Path(cmdopts['exp_stat_root'])
        ipath = stat_root / ('fsm-interference-counts' +
                             config.kStats['mean'].exts['mean'])
        fsm_df = reader(ipath)

        # We calculate 1 data point for each interval
        res_df = pd.DataFrame(columns=['model'], index=fsm_df.index)

        # Calculate kernel arguments
        kargs = self.calc_kernel_args(criteria, exp_num, cmdopts)

        # Run kernel on our results
        res_df['model'] = self.kernel(**kargs)

        # All done!
        return [res_df]


@implements.implements(sierra.core.models.interface.IConcreteIntraExpModel1D)
class IntraExp_RobotInterferenceTime_NRobots():
    r"""Models the steady state time a robot in a swarm of size :math:`\mathcal{N}`
    spends avoiding interference from other robots.  Uses Little's Law and
    :class:`IntraExpInterferenceRateNRobots`to perform the calculation.

    This model has a `:meth:`kernel()` function which computes the calculation,
    enabling this model to be used as a building block without necessarily
    needing to be :meth:`run()`.

    From :xref:`Harwell2021`.

    """
    @staticmethod
    def kernel(N_av1: tp.Union[pd.DataFrame, float],
               tau_av1: tp.Union[pd.DataFrame, float],
               N_avN: tp.Union[pd.DataFrame, float],
               tau_avN: tp.Union[pd.DataFrame, float],
               N: int) -> tp.Union[pd.DataFrame, float]:
        r"""Perform the interference time calculation.

        .. math::
           \tau_{av} = \big[\alpha_{r} + \alpha_{r}^1\mathcal{N}\big]\mathcal{N}_{av}(t).

        Args:

            N_av1: Fraction of robots in a swarm of size 1 which are
                   experiencing interference at time :math:`t`:
                   :math:`\mathcal{N}_{av}(t)`.

            tau_av1: Average time each robot in a swarm of size 1 spends in the
                     interference state beginning at time :math:`t`:
                     :math:`\tau_{av}^1`.

            N_avN: Number of robots in a swarm of size :math:`\mathcal{N}` which
                   are experiencing interference at time :math:`t`:
                   :math:`\mathcal{N}_{av}(t)`.

            tau_avN: Average time each robot in a swarm of size
                     :math:`\mathcal{N}` spends in the interference state
                     beginning at time :math:`t`: :math:`\tau_{av}`.

        Returns:

            Estimate of the steady state time robots from a swarm of
            :math:`\mathcal{N}` spend in the interference queue,
            :math:`\tau_{av}^N`.

        """
        alpha_ca1 = IntraExp_WallInterferenceRate_1Robot.kernel(
            N_av1=N_av1, tau_av1=tau_av1)
        alpha_caN = IntraExp_RobotInterferenceRate_NRobots.kernel(N_av1=N_av1,
                                                                  tau_av1=tau_av1,
                                                                  N_avN=N_avN,
                                                                  tau_avN=tau_avN)
        # All robots can enter the avoidance queue, so we don't need to modify
        # lambda according to the # of contributing robots.
        if N == 1:
            return N_av1 / alpha_ca1
        else:
            return N_avN / (alpha_caN) - alpha_ca1 * N_avN

    @staticmethod
    def calc_kernel_args(criteria: bc.IConcreteBatchCriteria,
                         exp_num: int,
                         cmdopts: types.Cmdopts) -> tp.Dict[str, pd.DataFrame]:
        kargs = IntraExp_RobotInterferenceRate_NRobots.calc_kernel_args(
            criteria, exp_num, cmdopts)
        kargs['N'] = criteria.populations(cmdopts)[exp_num]
        return kargs

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_exp(self,
                    criteria: bc.IConcreteBatchCriteria,
                    cmdopts: types.Cmdopts,
                    exp_num: int) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['fsm-interference-duration']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Interference Time']

    def __repr__(self) -> str:
        return self.__class__.__name__

    def run(self,
            criteria: bc.IConcreteBatchCriteria,
            exp_num: int,
            cmdopts: types.Cmdopts) -> tp.List[pd.DataFrame]:

        reader = storage.DataFrameReader('storage.csv')
        stat_root = pathlib.Path(cmdopts['exp_stat_root'])
        ipath = stat_root / ('fsm-interference-counts' +
                             config.kStats['mean'].exts['mean'])
        fsm_df = reader(ipath)

        # We calculate 1 data point for each interval
        res_df = pd.DataFrame(columns=['model'], index=fsm_df.index)

        # Calculate kernel arguments
        kargs = self.calc_kernel_args(criteria, exp_num, cmdopts)

        # Run kernel on our results
        res_df['model'] = self.kernel(**kargs)

        # All done!
        return [res_df]

################################################################################
# Inter-experiment models
################################################################################


@ implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_RobotInterferenceRate_NRobots():
    r"""Models the rate at which a swarm experiences inter-robot interference during
    foraging across all experiments in the batch. That is, one model datapoint
    is computed for each experiment within the batch.

    .. IMPORTANT:: This model does not have a kernel() function which computes
       the calculation, because it is a summary model, built on simpler
       intra-experiment models.

    """

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self,
                      criteria: bc.IConcreteBatchCriteria,
                      cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['interference-entered-cum-avg']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Interference Rate']

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

            # Model only targets one graph
            rateN = IntraExp_RobotInterferenceRate_NRobots(self.main_config,
                                                           self.config)
            intra_df = rateN.run(criteria, i, cmdopts2)[0]
            res_df[exp] = intra_df.loc[intra_df.index[-1], 'model']

        return [res_df]


@ implements.implements(sierra.core.models.interface.IConcreteInterExpModel1D)
class InterExp_RobotInterferenceTime_NRobots():
    r"""Models the steady state average time robots from a swarm of size
    :math:`\mathcal{N}` spend in the interference queue during foraging across
    all experiments in the batch. That is, one model datapoint is computed for
    each experiment within the batch.

    .. IMPORTANT:: This model does not have a kernel() function which computes
       the calculation, because it is a summary model, built on simpler
       intra-experiment models.

    """

    def __init__(self, main_config: types.YAMLDict, config: types.YAMLDict):
        self.main_config = main_config
        self.config = config

    def run_for_batch(self,
                      criteria: bc.IConcreteBatchCriteria,
                      cmdopts: types.Cmdopts) -> bool:
        return True

    def target_csv_stems(self) -> tp.List[str]:
        return ['interference-duration-cum-avg']

    def legend_names(self) -> tp.List[str]:
        return ['Predicted Interference Time']

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

            # Model only targets one graph
            timeN = IntraExp_RobotInterferenceTime_NRobots(self.main_config,
                                                           self.config)
            intra_df = timeN.run(criteria, i, cmdopts2)[0]
            res_df[exp] = intra_df.loc[intra_df.index[-1], 'model']

        return [res_df]
