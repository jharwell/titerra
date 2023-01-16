# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
#

# Core packages
import re
import logging
import typing as tp

# 3rd party packages
from sierra.core import types

# Project packages


class ScenarioGeneratorParser:
    """
    Parse the scenario specification from cmdline arguments; used later to
    create generator classes to make modifications to template input files.

    Format for pair is <scenario>.AxBxC

    <scenario> can be one of [SS,DS,QS,PL,RN]. A,B,C are the scenario
    dimensions.

    The Z dimension (C) is not optional (even for 2D simulations), due to how
    ARGoS handles LEDs internally.

    Returns:
        Parsed scenario specification, unless missing from the command line
        altogether; this can occur if the user is only running stage [4,5], and
        is not an error. In that case, None is returned.

    """

    def __init__(self) -> None:
        self.scenario = None
        self.logger = logging.getLogger(__name__)

    def to_scenario_name(self, args) -> tp.Optional[str]:
        """
        Parse the scenario generator from cmdline arguments into a string.
        """
        # Stage 5
        if args.scenario is None:
            return None

        # Scenario specified on cmdline
        self.logger.info("Parse scenario generator from cmdline specification '%s'",
                         args.scenario)

        res1 = re.search('[SDQPR][SSSLN]', args.scenario)
        assert res1 is not None,\
            "Bad block distribution specification in '{0}'".format(
                args.scenario)
        res2 = re.search('[0-9]+x[0-9]+x[0-9]+', args.scenario)

        assert res2 is not None,\
            "Bad arena_dim specification in '{0}'".format(args.scenario)

        self.scenario = res1.group(0) + "." + res2.group(0)
        return self.scenario

    def to_dict(self, scenario: str) -> types.CLIArgSpec:
        """
        Given a string (presumably a result of an earlier cmdline parse), parse it
        into a dictionary of components: arena_x, arena_y, arena_z, scenario_tag

        """
        x, y, z = scenario.split('+')[0].split('.')[1].split('x')
        dist_type = scenario.split('.')[0]

        return {
            'arena_x': int(x),
            'arena_y': int(y),
            'arena_z': int(z),
            'scenario_tag': dist_type
        }
