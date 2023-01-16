# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import sys

# 3rd party packages

# Common TITAN packages to lift into 'fordyca.generators' namespace for use in the the
# SIERRA project for FORDYCA.
from titerra.projects.common.generators import scenario_generator_parser
from titerra.projects.common.generators import ros1robot

# Do the lifts
sys.modules['fordyca_ros1robot.generators.scenario_generator_parser'] = scenario_generator_parser
sys.modules['fordyca_ros1robot.generators.exp_generators'] = ros1robot
