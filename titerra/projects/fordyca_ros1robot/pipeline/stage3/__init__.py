# Copyright 2021 John Harwell, All rights reserved.
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

# Core packages
import sys

# 3rd party packages

# Common TITAN packages to lift into 'fordyca_ros1robot.pipeline.stage3' namespace for use in
# the SIERRA project for FORDYCA.
from titerra.projects.common.pipeline.stage3 import run_collator

# Do the lifts
sys.modules['fordyca_ros1robot.pipeline.stage3.run_collator'] = run_collator
