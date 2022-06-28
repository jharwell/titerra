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

# Common TITAN packages to lift into 'fordyca_argos.variables' namespace for use
# in the SIERRA project for FORDYCA.
from titerra.variables import batch_criteria
from titerra.platform.argos.variables import arena
from titerra.platform.argos.variables import block_density
from titerra.platform.argos.variables import block_distribution
from titerra.platform.argos.variables import block_motion_dynamics
from titerra.platform.argos.variables import block_quantity
from titerra.platform.argos.variables import nest
from titerra.platform.argos.variables import population_size
from titerra.platform.argos.variables import population_constant_density
from titerra.platform.argos.variables import population_variable_density
from titerra.platform.argos.variables import saa_noise
from titerra.projects.common.variables import oracle
from titerra.projects.common.variables import ta_policy_set
from titerra.projects.common.variables import temporal_variance
from titerra.projects.common.variables import temporal_variance_parser
from titerra.projects.common.variables import exp_setup

# Do the lifts
sys.modules['fordyca_argos.variables.batch_criteria'] = batch_criteria
sys.modules['fordyca_argos.variables.arena'] = arena
sys.modules['fordyca_argos.variables.block_density'] = block_density
sys.modules['fordyca_argos.variables.block_distribution'] = block_distribution
sys.modules['fordyca_argos.variables.block_motion_dynamics'] = block_motion_dynamics
sys.modules['fordyca_argos.variables.block_quantity'] = block_quantity
sys.modules['fordyca_argos.variables.nest'] = nest
sys.modules['fordyca_argos.variables.saa_noise'] = saa_noise
sys.modules['fordyca_argos.variables.oracle'] = oracle
sys.modules['fordyca_argos.variables.population_size'] = population_size
sys.modules['fordyca_argos.variables.population_constant_density'] = population_constant_density
sys.modules['fordyca_argos.variables.population_variable_density'] = population_variable_density
sys.modules['fordyca_argos.variables.ta_policy_set'] = ta_policy_set
sys.modules['fordyca_argos.variables.temporal_variance'] = temporal_variance
sys.modules['fordyca_argos.variables.temporal_variance_parser'] = temporal_variance_parser
sys.modules['fordyca_argos.variables.exp_setup'] = exp_setup
