# Copyright 2019 John Harwell, All rights reserved.
#
#  This file is part of SIERRA.
#
#  SIERRA is free software: you can redistribute it and/or modify it under the terms of the GNU
#  General Public License as published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  SIERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  SIERRA.  If not, see <http://www.gnu.org/licenses/
#
"""
Command line parsing and validation for the :xref:`FORDYCA` project.
"""

# Core packages
import typing as tp

# 3rd party packages

# Project packages
import projects.titan as titan


class Cmdline(titan.cmdline.Cmdline):
    """
    Defines FORDYCA extensions to the core command line arguments defined in
    :class:`~sierra.core.cmdline.CoreCmdline`.
    """

    def __init__(self, bootstrap, stages: tp.List[int], for_sphinx: bool) -> None:
        super().__init__(bootstrap, stages, for_sphinx)

        if -1 in stages:
            self.__init_multistage()

        if 1 in stages:
            self.__init_stage1()

    def __init_multistage(self):
        self.multistage.add_argument("--controller",
                                     metavar="{d0, d1, d2}.<controller>",
                                     choices=['d0.CRW',
                                              'd0.DPO',
                                              'd0.ODPO',
                                              'd0.MDPO',
                                              'd0.OMDPO',
                                              'd1.BITD_DPO',
                                              'd1.BITD_ODPO',
                                              'd1.BITD_OMDPO',
                                              'd2.BIRTD_DPO',
                                              'd2.BIRTD_ODPO',
                                              'd2.BIRTD_OMDPO'],
                                     help="""

                                 Which controller robots will use in the foraging experiment. All robots use the
                                 same controller (homogeneous swarms).

                                 Head over to the :xref:`FORDYCA` docs for the descriptions of these controllers.


                                 """ + self.stage_usage_doc([1, 2, 3, 4, 5],
                                                            "Only required for stage 5 if ``--scenario-comp`` is passed."))

    def __init_stage1(self):
        self.stage1.add_argument("--static-cache-blocks",
                                 help="""

                                 # of blocks used when the static cache is respawned (d1 controllers only).


                                 """ + self.stage_usage_doc([1]),
                                 default=None)

        self.stage1.add_argument("--n-blocks",
                                 help="""

                                 # blocks that should be used in the simulation (evenly split between cube and
                                 ramp). Can The be used to override batch criteria, or to supplement experiments that do
                                 not set it so that manual modification of input file is unneccesary.

                                 """ + self.stage_usage_doc([1]),
                                 type=int,
                                 default=None)

    @staticmethod
    def cmdopts_update(cli_args, cmdopts: tp.Dict[str, str]):
        """
        Updates the core cmdopts dictionary with (key,value) pairs from the FORDYCA-specific cmdline options.
        """
        # Stage1
        updates = {
            'controller': cli_args.controller,
            'static_cache_blocks': cli_args.static_cache_blocks,
            'n_blocks': cli_args.n_blocks
        }
        cmdopts.update(updates)


class CmdlineValidator(titan.cmdline.CmdlineValidator):
    pass


def sphinx_cmdline_multistage():
    return Cmdline(None, [-1], True).parser


def sphinx_cmdline_stage1():
    return Cmdline(None, [1], True).parser
