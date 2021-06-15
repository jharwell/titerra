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
Command line parsing and validation classes for the SILICON project.
"""

# Core packages
import typing as tp

# 3rd party packages

# Project packages
import projects.titan as titan


class Cmdline(titan.cmdline.Cmdline):
    """
    Defines SILICON extensions to the core command line arguments defined in
    :class:`~core.cmdline.CoreCmdline`.
    """

    def __init__(self, bootstrap, stages, for_sphinx):
        super().scaffold_cli(bootstrap)

        if not for_sphinx:
            super().init_cli(stages, for_sphinx)

        if -1 in stages and for_sphinx:
            self.init_multistage(for_sphinx)

        if 1 in stages and for_sphinx:
            self.init_stage1(for_sphinx)

    def init_multistage(self, for_sphinx: bool):
        super().init_multistage(for_sphinx)

        self.multistage.add_argument("--controller",
                                     metavar="{depth0}.<controller>",
                                     help="""

                                     Which controller footbot robots will use in the construction experiment. All robots
                                     use the same controller (homogeneous swarms).

                                     Valid controllers:

                                     - depth0.{DPOB}

                                     Head over to the :xref:`SILICON` docs for the descriptions of these controllers.

                                     Use=stage{1,2,3,4}; can be omitted otherwise.
                                     """)

    def init_stage1(self, for_sphinx: bool):
        super().init_stage1(for_sphinx)

        construct = self.parser.add_argument_group('Stage1: Construction',
                                                   'Construction target options for stage1')

        construct.add_argument("--ct-specs",
                               metavar="<type>.AxBxC@D,E",
                               help="""

                               A list of construction targets within a scenario to direct the swarm to build, separated
                               by spaces. See :ref:`ln-silicon-vars-construct-targets` for a full description.

                               """ + self.stage_usage_doc([1]),
                               nargs='+')

        construct.add_argument("--ct-orientations",
                               choices=['0', 'PI/2', 'PI', '3PI/2'],
                               help="""

                               Space separated list of the orientations for the targets specified in ``--ct-specs``,
                               defining the X-axis for each target.

                               """ + self.stage_usage_doc([1]),
                               nargs='+')

    @staticmethod
    def cmdopts_update(cli_args, cmdopts: tp.Dict[str, str]):
        """
        Updates the core cmdopts dictionary with (key,value) pairs from the SILICON-specific cmdline
        options.

        """
        titan.cmdline.Cmdline.cmdopts_update(cli_args, cmdopts)
        # Stage1
        updates = {
            'controller': cli_args.controller,
            'ct_specs': cli_args.ct_specs,
            'ct_orientations': cli_args.ct_orientations
        }
        cmdopts.update(updates)


class CmdlineValidator(titan.cmdline.CmdlineValidator):
    def __call__(self, args) -> None:
        super().__call__(args)

        assert args.ct_specs is not None,\
            "FATAL: --ct-specs is required for SILICON"

        assert args.ct_orientations is not None,\
            "FATAL: --ct-orientations is required for SILICON"


def sphinx_cmdline_multistage():
    return Cmdline(None, [-1], True).parser


def sphinx_cmdline_stage1():
    return Cmdline(None, [1], True).parser
