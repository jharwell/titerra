# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
"""Classes for the task allocation policy batch criteria. See
:ref:`ln-bc-ta-policy-set` for usage documentation.

"""


# Core packages
import re
import typing as tp
import pathlib

# 3rd party packages
import implements
from sierra.plugins.platform.argos.variables.population_size import PopulationSize
from sierra.core.experiment import xml
from sierra.core import types

# Project packages
import titerra.variables.batch_criteria as bc


@implements.implements(bc.IConcreteBatchCriteria)
@implements.implements(bc.IPMQueryableBatchCriteria)
class TAPolicySet(bc.UnivarBatchCriteria):
    """
    A univariate range specifiying the set of task allocation policies (and
    possibly swarm size) to use to define the batched experiment. This class is
    a base class which should (almost) never be used on its own. Instead, the
    ``factory()`` function should be used to dynamically create derived classes
    expressing the user's desired policies and swarm size.

    Attributes:
        policies: List of policies to enable for a specific simulation.
        population: Swarm size to use for a specific simulation.

    """
    kPolicies = ['random', 'stoch_nbhd1',
                 'strict_greedy', 'epsilon_greedy', 'UCB1']

    def __init__(self, cli_arg: str,
                 main_config: types.YAMLDict,
                 batch_input_root: pathlib.Path,
                 policies: list,
                 population: tp.Optional[int]) -> None:
        bc.UnivarBatchCriteria.__init__(
            self, cli_arg, main_config, batch_input_root)
        self.policies = policies
        self.population = population
        self.attr_changes = []

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        if not self.attr_changes:
            # Swarm size is optional. It can be (1) controlled via this
            # variable, (2) controlled by another variable in a bivariate batch
            # criteria, (3) not controlled at all. For (2), (3), the swarm size
            # can be None.
            if self.population is not None:
                size_chgs = PopulationSize(self.cli_arg,
                                           self.main_config,
                                           self.batch_input_root,
                                           [self.population]).gen_attr_changelist()[0]
            else:
                size_chgs = xml.AttrChangeSet()

            self.attr_changes = [xml.AttrChangeSet(xml.AttrChange(".//task_alloc",
                                                                  "policy",
                                                                  "{0}".format(p))) for p in self.policies]

            for chgset in self.attr_changes:
                chgset |= size_chgs

        return self.attr_changes

    def gen_exp_names(self, cmdopts: types.Cmdopts) -> tp.List[str]:
        changes = self.gen_attr_changelist()
        return ['exp' + str(x) for x in range(0, len(changes))]

    def graph_xticks(self,
                     cmdopts: types.Cmdopts,
                     exp_names: tp.Optional[tp.List[str]] = None) -> tp.List[float]:
        if exp_names is not None:
            dirs = exp_names
        else:
            dirs = self.gen_exp_names(cmdopts)

        return [float(i) for i in range(1, len(dirs) + 1)]

    def graph_xticklabels(self,
                          cmdopts: types.Cmdopts,
                          exp_names: tp.Optional[tp.List[str]] = None) -> tp.List[str]:
        return ['Random', 'STOCH-N1', 'MAT-OPT', r'$\epsilon$-greedy', 'UCB1']

    def graph_xlabel(self, cmdopts: types.Cmdopts) -> str:
        return "Task Allocation Policy"

    def pm_query(self, pm: str) -> bool:
        return pm in ['raw']

    def inter_exp_graphs_exclude_exp0(self) -> bool:
        return False


class Parser():
    """
    Enforces the cmdline definition of the :class:`TAPolicySet` batch criteria
    defined in :ref:`ln-bc-ta-policy-set`.

    """

    def __call__(self, cli_arg: str) -> dict:
        """
        Returns:
            Dictionary with keys:
                population: Swarm size to use (optional)

        """
        ret = {}

        # Parse task allocation policy set
        assert cli_arg.split('.')[1] == 'all', \
            "Bad type specification in criteria '{0}'. Only 'all' supported.".format(
                cli_arg)

        # Parse swarm size
        if len(cli_arg.split('.')) == 3:
            swarm_size = cli_arg.split('.')[2]
            res = re.search(r"Z[0-9]+", swarm_size)
            assert res is not None,\
                "Bad swarm size specification in criteria '{0}'".format(
                    cli_arg)
            ret['population'] = int(res.group(0)[1:])

        return ret


def factory(cli_arg: str,
            main_config: types.YAMLDict,
            cmdopts: types.Cmdopts,
            **kwargs):
    """Factory to create :class:`TAPolicySet` derived classes from the command line
    definition of batch criteria.
    """
    attr = Parser()(cli_arg)

    def __init__(self) -> None:
        TAPolicySet.__init__(self,
                             cli_arg,
                             main_config,
                             cmdopts['batch_input_root'],
                             TAPolicySet.kPolicies,
                             attr.get('population', None))

    return type(cli_arg,
                (TAPolicySet,),
                {"__init__": __init__})


__api__ = [
    'TAPolicySet'
]
