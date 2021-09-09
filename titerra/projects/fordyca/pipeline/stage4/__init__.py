# Copyright 2021 John Harwell, All rights reserved.
#
#  This file is part of TITAN.
#
#  TITAN is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  TITAN is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  TITAN.  If not, see <http://www.gnu.org/licenses/

# Core packages
import sys

# 3rd party packages

# Project packages


# TITAN packages to lift into 'fordyca.pipeline.stage4' namespace
from projects.titan.pipeline.stage4 import inter_exp_graph_generator

# Do the lifts
sys.modules['projects.fordyca.pipeline.stage4.inter_exp_graph_generator'] = inter_exp_graph_generator
