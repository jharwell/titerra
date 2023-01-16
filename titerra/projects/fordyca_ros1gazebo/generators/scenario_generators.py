# Copyright 2018 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages

# 3rd party packages

# Project packages
from titerra.projects.common.generators import ros1gazebo


class SSGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


class DSGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


class RNGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


class PLGenerator(ros1gazebo.ForagingScenarioGenerator):
    pass


def gen_generator_name(scenario_name: str) -> str:
    return ros1gazebo.gen_generator_name(scenario_name)
