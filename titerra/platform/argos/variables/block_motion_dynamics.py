# Copyright 2021 John Harwell, All rights reserved.
#
# SPDX-License-Identifier: MIT
"""
Classes for the block motion batch criteria. See
:ref:`ln-bc-block-motion-dynamics` for usage documentation.
"""

# Core packages
import typing as tp
import pathlib

# 3rd party packages
import implements
import sierra.core.utils
from sierra.core.experiment import xml
from sierra.core import types, config

# Project packages
import titerra.projects.common.variables.dynamics_parser as dp
from titerra.variables import batch_criteria as bc


@implements.implements(bc.IConcreteBatchCriteria)
@implements.implements(bc.IPMQueryableBatchCriteria)
class BlockMotionDynamics(bc.UnivarBatchCriteria):
    """A univariate range of block motion dynamics used to define batched
    experiments. This class is a base class which should (almost) never be used
    on its own. Instead, the ``factory()`` function should be used to
    dynamically create derived classes expressing the user's desired dynamics
    distribution.

    Attributes:

        dynamics_type: The type of motion dynamics.

        dynamics: List of tuples specifying XML changes for each variation of
                   motion dynamics.

    """

    def __init__(self,
                 cli_arg: str,
                 main_config: types.YAMLDict,
                 batch_input_root: pathlib.Path,
                 dynamics_type: str,
                 dynamics: tp.List[tp.Tuple[str, int]]) -> None:
        bc.UnivarBatchCriteria.__init__(
            self, cli_arg, main_config, batch_input_root)
        # For now, only a single dynamics type
        self.dynamics_type = dynamics_type
        self.dynamics = dynamics

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        """
        Generate list of sets of changes for population dynamics.
        """
        return self.dynamics

    def gen_exp_names(self, cmdopts: types.Cmdopts) -> list:
        changes = self.gen_attr_changelist()
        return ['exp' + str(x) for x in range(0, len(changes))]

    def graph_xticks(self,
                     cmdopts: types.Cmdopts,
                     exp_names: tp.Optional[tp.List[str]] = None) -> tp.List[float]:
        if exp_names is None:
            exp_names = self.gen_exp_names(cmdopts)

        ticks = []

        for d in exp_names:
            path = self.batch_input_root / d / config.kPickleLeaf
            exp_def = xml.AttrChangeSet.unpickle(path)
            ticks.append(BlockMotionDynamics.calc_xtick(exp_def))

        return ticks

    def graph_xticklabels(self,
                          cmdopts: types.Cmdopts,
                          exp_names: tp.Optional[tp.List[str]] = None) -> tp.List[str]:
        return list(map(str, self.graph_xticks(cmdopts, exp_names)))

    def graph_xlabel(self, cmdopts: types.Cmdopts) -> str:
        labels = {'RW': 'Random Walk Probability'}
        return labels[self.dynamics_type]

    def pm_query(self, pm: str) -> bool:
        return pm in ['raw']

    def inter_exp_graphs_exclude_exp0(self) -> bool:
        return False

    @staticmethod
    def calc_xtick(exp_def):
        policy = None
        for path, attr, value in exp_def:
            if 'arena_map/blocks/motion' in path:
                if attr == 'policy':
                    policy = value

        for path, attr, value in exp_def:
            if 'arena_map/blocks/motion' in path:
                if policy == 'random_walk' and attr == 'random_walk_prob':
                    return float(value)

        return None


class BlockMotionDynamicsParser(dp.DynamicsParser):
    """
    Enforces the cmdline definition of the :class:`BlockMotionDynamics` batch criteria defined in
    :ref:`ln-bc-block-motion-dynamics`
    """

    def specs_dict(self):
        return {'RW': 'random_walk_prob'}


def factory(cli_arg: str,
            main_config: tp.Dict[str, str],
            cmdopts: types.Cmdopts,
            **kwargs) -> BlockMotionDynamics:
    """
    Factory to create :class:`BlockMotionDynamics` derived classes from the command line definition.

    """
    attr = BlockMotionDynamicsParser()(cli_arg)
    policy_xml_parents = {
        'RW': xml.AttrChange('.//arena_map/blocks/motion', 'policy', 'random_walk')
    }
    dynamics_type = attr['dynamics_types'][0]
    policy_xml = policy_xml_parents[dynamics_type]

    def gen_dynamics():
        # ideal conditions = no dynamics
        dynamics = [xml.AttrChangeSet(*{policy_xml,
                                        xml.AttrChange('.//arena_map/blocks/motion',
                                                       d[0],
                                                       "0.0")}) for d in attr['dynamics']]

        for x in range(0, attr['cardinality'] - 1):
            expx = [xml.AttrChangeSet(*{policy_xml,
                                        xml.AttrChange('.//arena_map/blocks/motion',
                                                       d[0],
                                                       str("%3.9f" % (d[1] + d[1] * x * float(attr['factor']))))}) for d in attr['dynamics']]
            dynamics.extend(expx)

        return dynamics

    def __init__(self) -> None:
        BlockMotionDynamics.__init__(self,
                                     cli_arg,
                                     main_config,
                                     cmdopts['batch_input_root'],
                                     dynamics_type,
                                     gen_dynamics())

    return type(cli_arg,  # type: ignore
                (BlockMotionDynamics,),
                {"__init__": __init__})


__api__ = [
    'BlockMotionDynamics'


]
