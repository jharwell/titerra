# Copyright 2018 John Harwell, All rights reserved.
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

# Core packages

# 3rd party packages

# Project packages
from titerra.projects.common.generators import ros1gazebo


class SSGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


class DSGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


class RNGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


class PLGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


def gen_generator_name(scenario_name: str) -> str:
    return ros1gazebo.gen_generator_name(scenario_name)
