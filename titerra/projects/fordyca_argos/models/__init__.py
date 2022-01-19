# Copyright 2020 John Harwell, All rights reserved.
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
import importlib
import sys
# 3rd party packages

# Common FORDYCA models to lift into the ARGoS project.
from titerra.projects.fordyca_base.models import blocks
from titerra.projects.fordyca_base.models import density
from titerra.projects.fordyca_base.models import diffusion
from titerra.projects.fordyca_base.models import dist_measure
from titerra.projects.fordyca_base.models import homing_time
from titerra.projects.fordyca_base.models import interference
from titerra.projects.fordyca_base.models import model_error
from titerra.projects.fordyca_base.models import perf_measures
from titerra.projects.fordyca_base.models import representation
from titerra.projects.fordyca_base.models import AURO2022

# Do the lifts
sys.modules['fordyca_argos.models.blocks'] = blocks
sys.modules['fordyca_argos.models.density'] = density
sys.modules['fordyca_argos.models.diffusion'] = diffusion
sys.modules['fordyca_argos.models.dist_measure'] = dist_measure
sys.modules['fordyca_argos.models.homing_time'] = homing_time
sys.modules['fordyca_argos.models.interference'] = interference
sys.modules['fordyca_argos.models.model_error'] = model_error
sys.modules['fordyca_argos.models.perf_measures'] = perf_measures
sys.modules['fordyca_argos.models.representation'] = representation
sys.modules['fordyca_argos.models.AURO_2022'] = AURO2022
