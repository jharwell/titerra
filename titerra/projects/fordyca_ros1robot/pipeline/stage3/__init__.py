# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import sys

# 3rd party packages

# Common TITAN packages to lift into 'fordyca_ros1robot.pipeline.stage3' namespace for use in
# the SIERRA project for FORDYCA.
from titerra.projects.common.pipeline.stage3 import run_collator

# Do the lifts
sys.modules['fordyca_ros1robot.pipeline.stage3.run_collator'] = run_collator
