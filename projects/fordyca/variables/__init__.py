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

# TITAN packages to lift into 'fordyca.variables' namespace
from projects.titan.variables import arena as arena
from projects.titan.variables import block_density as block_density
from projects.titan.variables import block_distribution as block_distribution
from projects.titan.variables import block_motion_dynamics as block_motion_dynamics
from projects.titan.variables import block_quantity as block_quantity
from projects.titan.variables import nest as nest
from projects.titan.variables import oracle as oracle
from projects.titan.variables import population_size as population_size
from projects.titan.variables import ta_policy_set as ta_policy_set
from projects.titan.variables import temporal_variance as temporal_variance
from projects.titan.variables import temporal_variance_parser as temporal_variance_parser
from projects.titan.variables import time_setup as time_setup

# Do the lifts
sys.modules['projects.fordyca.variables.arena'] = arena
sys.modules['projects.fordyca.variables.block_density'] = block_density
sys.modules['projects.fordyca.variables.block_distribution'] = block_distribution
sys.modules['projects.fordyca.variables.block_motion_dynamics'] = block_motion_dynamics
sys.modules['projects.fordyca.variables.block_quantity'] = block_quantity
sys.modules['projects.fordyca.variables.nest'] = nest
sys.modules['projects.fordyca.variables.oracle'] = oracle
sys.modules['projects.fordyca.variables.population_size'] = population_size
sys.modules['projects.fordyca.variables.ta_policy_set'] = ta_policy_set
sys.modules['projects.fordyca.variables.temporal_variance'] = temporal_variance
sys.modules['projects.fordyca.variables.temporal_variance_parser'] = temporal_variance_parser
sys.modules['projects.fordyca.variables.time_setup'] = time_setup
