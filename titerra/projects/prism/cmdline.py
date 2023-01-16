# Copyright 2019 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
#
"""
Command line parsing and validation classes for the PRISM project.
"""

# Core packages
import typing as tp
import argparse

# 3rd party packages

# Project packages
import titerra.projects.common as common
import sierra.core.cmdline as sacmd


class Cmdline(common.cmdline.CommonCmdline):
    """
    Defines PRISM extensions to the core command line arguments defined in
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

                                     Which controller footbot robots will use in
                                     the construction experiment. All robots use
                                     the same controller (homogeneous swarms).

                                     Valid controllers:

                                     - FCRW_BST

                                     Head over to the :xref:`PRISM` docs for the
                                     descriptions of these controllers.  """ + self.stage_usage_doc([1, 2, 3, 4]),)

    def init_stage1(self, for_sphinx: bool):
        super().init_stage1(for_sphinx)

        construct = self.parser.add_argument_group('Stage1: Construction',
                                                   'Construction target options for stage1')

        self.add_ct_args(construct)

    @staticmethod
    def add_ct_args(group) -> None:

        group.add_argument("--ct-specs",
                           metavar="<type>.AxBxC@D,E,F",
                           help="""

                           A list of construction target specifications within a
                           scenario to direct the swarm to build, separated by
                           spaces. See :ref:`ln-prism-bc-ct-specs` for a full
                           description.

                               """ + sacmd.BaseCmdline.stage_usage_doc([1]),
                           nargs='+')

        group.add_argument("--ct-orientations",
                           choices=['0', 'PI/2', 'PI', '3PI/2'],
                           help="""

                           Space separated list of the orientations for the
                           targets specified in ``--ct-specs``, defining the
                           X-axis for each target.

                               """ + sacmd.BaseCmdline.stage_usage_doc([1]),
                           nargs='+')

        group.add_argument("--ct-paradigm",
                           choices=['semantic', 'edge', 'vertex'],
                           help="""

                           The representation to use for blocks for ALL
                           generated graphs. Valid values are:

                           - ``semantic`` - Blocks are represented as a single
                             vertex with the following semantic information
                             attached: XYZ coordinates, block type, Z-rotation,
                             and color. Block extent information can be
                             recovered by processing the information attached to
                             each vertex.

                           - ``edge`` - Blocks are represented as a pair of
                             vertices (one at each endpoint) connected by an
                             edge. Each vertex has its XYZ location and color
                             attached to it.

                           - ``vertex`` - Blocks are representated as a set of
                             vertices along their orientation axis. Each vertex
                             has its XYZ location and color attached to it.

                           """,
                           default='semantic')

    @staticmethod
    def cmdopts_update(cli_args, cmdopts: tp.Dict[str, str]):
        """Updates the core cmdopts dictionary with (key,value) pairs from the
        PRISM-specific cmdline options.

        """
        common.cmdline.CommonCmdline.cmdopts_update(cli_args, cmdopts)
        # Stage1
        updates = {
            'controller': cli_args.controller,
            'ct_specs': cli_args.ct_specs,
            'ct_orientations': cli_args.ct_orientations,
            'ct_paradigm': cli_args.ct_paradigm
        }
        cmdopts.update(updates)


class CmdlineValidator(sacmd.CoreCmdlineValidator):
    def __call__(self, args) -> None:
        super().__call__(args)

        assert args.ct_specs is not None,\
            "--ct-specs is required for PRISM"

        assert args.ct_orientations is not None,\
            "--ct-orientations is required for PRISM"


def sphinx_cmdline_multistage():
    return Cmdline(None, [-1], True).parser


def sphinx_cmdline_stage1():
    return Cmdline(None, [1], True).parser
