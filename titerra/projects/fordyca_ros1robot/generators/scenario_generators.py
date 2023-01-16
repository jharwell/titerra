# Copyright 2018 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages

# 3rd party packages

# Project packages
from titerra.projects.common.generators import ros1robot


class SSGenerator(ros1robot.ForagingScenarioGenerator):
    pass


class DSGenerator(ros1robot.ForagingScenarioGenerator):
    pass


class RNGenerator(ros1robot.ForagingScenarioGenerator):
    pass


class PLGenerator(ros1robot.ForagingScenarioGenerator):
    pass


def gen_generator_name(scenario_name: str) -> str:
    return ros1robot.gen_generator_name(scenario_name)
