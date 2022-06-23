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
from sierra.plugins.platform.argos.variables import population_variable_density as pvd
from sierra.plugins.platform.argos.variables.population_variable_density import factory

# Project packages
import titerra.variables.batch_criteria as bc


@implements.implements(bc.IPMQueryableBatchCriteria)
class PopulationVariableDensity(pvd.PopulationVariableDensity):
    """Extends :class:`~pvd.PopulationVariableDensity` with performance measure
    bits.

    """

    def __init__(self, *args, **kwargs) -> None:
        pvd.PopulationVariableDensity(*args, **kwargs)

    def pm_query(self, pm: str) -> bool:
        return pm in ['raw', 'scalability', 'self-org']


__api__ = [
    'PopulationVariableDensity'
]
