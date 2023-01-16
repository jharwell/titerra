# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import sys

# 3rd party packages

# Common TITAN packages to lift into 'prism.generators' namespace
from projects.common.generators import scenario_generator_parser
from projects.common.generators import exp_generators

# Do the lifts
sys.modules['projects.prism.generators.scenario_generator_parser'] = scenario_generator_parser
sys.modules['projects.prism.generators.exp_generators'] = exp_generators
