# Copyright 2021 John Harwell, All rights reserved.
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
import sys

# 3rd party packages

# TITAN packages to lift into 'fordyca.generators' namespace
from projects.titan.generators import scenario_generator_parser
from projects.titan.generators import exp_generators

# Do the lifts
sys.modules['projects.fordyca.generators.scenario_generator_parser'] = scenario_generator_parser
sys.modules['projects.fordyca.generators.exp_generators'] = exp_generators
