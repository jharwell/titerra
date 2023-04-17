# Copyright 2019 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
#
"""
Command line parsing and validation for the :xref:`FORDYCA` project, when using
:term:`ROS`.
"""

# Core packages
import typing as tp
import argparse

# 3rd party packages
from sierra.core import types, ros1

# Project packages
from titerra.projects.common import cmdline


class Cmdline(cmdline.CommonCmdline):
    """
    Defines FORDYCA extensions to the core command line arguments defined in
    :class:`~sierra.core.cmdline.CoreCmdline` for running ROS1 on real robots.
    """

    def __init__(self, parents: tp.List[argparse.ArgumentParser],
                 stages: tp.List[int]) -> None:
        super().scaffold_cli(parents)

        super().init_cli(stages, )

    def init_multistage(self):
        super().init_multistage()

        self.multistage.add_argument("--scenario",
                                     metavar="Foraging.AxBxC",
                                     help="""

                                    The scenario to use. A,B,C are the scenario
                                    X,Y,Z dimensions respectively (which can be
                                    any postive INTEGER values). All dimensions
                                    are required.

                                     """ + self.stage_usage_doc([1, 2, 3, 4]))
        self.multistage.add_argument("--controller",
                                     metavar="{d0}.<controller>",
                                     choices=['d0.CRW'],
                                     help="""

                                 Which controller robots will use in the
                                 foraging experiment. All robots use the same
                                 controller (homogeneous swarms).

                                 Head over to the :xref:`FORDYCA` docs for the
                                 descriptions of these controllers.

                                     """ + self.stage_usage_doc([1, 2, 3, 4, 5],
                                                                "Only required for stage 5 if ``--scenario-comp`` is passed."))

    @staticmethod
    def cmdopts_update(cli_args, cmdopts: types.Cmdopts):
        """Updates the core cmdopts dictionary with (key,value) pairs from the
        FORDYCA-specific cmdline options.

        """
        cmdline.ROSCmdline.cmdopts_update(cli_args, cmdopts)

        # Stage1
        updates = {
            'controller': cli_args.controller
        }
        cmdopts.update(updates)


class CmdlineValidator(ros1.cmdline.ROSCmdlineValidator):
    pass


def sphinx_cmdline_multistage():
    return Cmdline(None, [-1]).parser
