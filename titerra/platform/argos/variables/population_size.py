# Copyright 2021 John Harwell, All rights reserved.
#
# SPDX-License-Identifier: MIT
"""
Classes for the population size batch criteria. See
:ref:`ln-bc-population-size` for usage documentation.

"""

# Core packages
import typing as tp

# 3rd party packages
import implements
from sierra.plugins.platform.argos.variables import population_size
from sierra.core.variables.population_size import Parser
from sierra.core.experiment import xml
from sierra.core import types

# Project packages
from titerra.variables import batch_criteria as bc


@implements.implements(bc.IConcreteBatchCriteria)
@implements.implements(bc.IPMQueryableBatchCriteria)
class PopulationSizeWithDynamics(population_size.PopulationSize):
    """
    A univariate range of swarm sizes used to define batched experiments. This
    class is a base class which should (almost) never be used on its
    own. Instead, the ``factory()`` function should be used to dynamically
    create derived classes expressing the user's desired size distribution.

    """

    @staticmethod
    def gen_attr_changelist_from_list(sizes: tp.List[int]) -> tp.List[xml.AttrChangeSet]:
        """
        We give the maximum population size due to population dynamics a value
        of 4N, where N is the initial quantity of robots for the simulation, in
        order to provide buffer so that the queueing theoretic predictions of
        long-run population size are accurate.

        """
        chgsets = population_size.PopulationSize.gen_attr_changelist_from_list(
            sizes)
        for i, chgset in enumerate(chgsets):
            chgset |= xml.AttrChangeSet(xml.AttrChange(".//population_dynamics",
                                                       "max_size",
                                                       str(4 * sizes[i])))
        return chgsets

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        """
        Generate list of sets of changes for swarm sizes to define a batch
        experiment.

        """
        if not self.attr_changes:
            self.attr_changes = PopulationSizeWithDynamics.gen_attr_changelist_from_list(
                self.size_list)
        return self.attr_changes

    def pm_query(self, pm: str) -> bool:
        return pm in ['raw', 'scalability', 'self-org']


def factory(cli_arg: str,
            main_config: types.YAMLDict,
            cmdopts: types.Cmdopts,
            **kwargs) -> PopulationSizeWithDynamics:
    """
    Factory to create :class:`PopulationSize` derived classes from the command
    line definition.

    """
    parser = Parser()
    max_sizes = parser.to_sizes(parser(cli_arg))

    def __init__(self) -> None:

        PopulationSizeWithDynamics.__init__(self,
                                            cli_arg,
                                            main_config,
                                            cmdopts['batch_input_root'],
                                            max_sizes)

    return type(cli_arg,  # type: ignore
                (PopulationSizeWithDynamics,),
                {"__init__": __init__})


__api__ = [
    'PopulationSizeWithDynamics'
]
