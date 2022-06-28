# Copyright 2022 John Harwell, All rights reserved.
#
#  This file is part of TITERRA.
#
#  TITERRA is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  TITERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  TITERRA.  If not, see <http://www.gnu.org/licenses/
#
"""
Classes for the variable population density batch criteria for use in the TITAN
project.
"""

# Core packages

# 3rd party packages
import implements
import numpy as np
from sierra.core import types, utils
from sierra.core.vector import Vector3D
from sierra.plugins.platform.argos.variables import population_variable_density as pvd
from sierra.core.variables import variable_density as vd

# Project packages
import titerra.variables.batch_criteria as bc


@implements.implements(bc.IPMQueryableBatchCriteria)
class PopulationVariableDensity(pvd.PopulationVariableDensity):
    """Extends :class:`~pvd.PopulationVariableDensity` with performance measure
    bits.

    """

    def __init__(self, *args, **kwargs) -> None:
        pvd.PopulationVariableDensity.__init__(self, *args, **kwargs)

    def pm_query(self, pm: str) -> bool:
        return pm in ['raw', 'scalability', 'self-org']


def factory(cli_arg: str,
            main_config: types.YAMLDict,
            cmdopts: types.Cmdopts,
            **kwargs) -> PopulationVariableDensity:
    """
    Factory to create :class:`PopulationVariableDensity` derived classes from
    the command line definition.
    """
    attr = vd.Parser()(cli_arg)
    kw = utils.gen_scenario_spec(cmdopts, **kwargs)

    extent = utils.ArenaExtent(Vector3D(kw['arena_x'],
                                        kw['arena_y'],
                                        kw['arena_z']))

    densities = [x for x in np.linspace(attr['density_min'],
                                        attr['density_max'],
                                        num=attr['cardinality'])]

    def __init__(self) -> None:
        PopulationVariableDensity.__init__(self,
                                           cli_arg,
                                           main_config,
                                           cmdopts['batch_input_root'],
                                           densities,
                                           extent)

    return type(cli_arg,  # type: ignore
                (PopulationVariableDensity,),
                {"__init__": __init__})


__api__ = [
    'PopulationVariableDensity'
]
