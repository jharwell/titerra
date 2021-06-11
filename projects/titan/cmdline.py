# Copyright 2021 John Harwell, All rights reserved.
#
#  This file is part of TITERRA.
#
#  TITERRA is free software: you can redistribute it and/or modify it under the terms of the GNU
#  General Public License as published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  TITERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  TITERRA.  If not, see <http://www.gnu.org/licenses/
#
"""
Command line parsing and validation for the :xref:`TITAN` project.
"""

# Core packages
import typing as tp

# 3rd party packages

# Project packages
import sierra


class Cmdline(sierra.core.cmdline.CoreCmdline):
    """
    Defines TITAN extensions to the core command line arguments defined in
    :class:`~sierra.core.cmdline.CoreCmdline`.
    """

    def init_multistage(self, for_sphinx: bool):
        super().init_multistage(for_sphinx)

        self.multistage.add_argument("--scenario",
                                     metavar="<block dist>.AxBxC",
                                     help="""

                                     Which scenario the swarm comprised of robots running the controller specified via
                                     ``--controller`` should be run in.

                                     A scenario is defined as: block distribution type + arena dimensions. This is
                                     somewhat tied to foraging and other similar applications for the moment, but this
                                     may be modified in a future version of TITERRA.

                                     Valid block distribution types:

                                     - ``RN`` - Random
                                     - ``SS`` - Single source
                                     - ``DS`` - Dual source
                                     - ``QS`` - Quad source
                                     - ``PL`` - Power law

                                     A,B,C are the scenario X,Y,Z dimensions respectively (which can be any postive
                                     INTEGER values). All dimensions are required.

                                 """ + self.stage_usage_doc([1, 2, 3, 4]))

    @staticmethod
    def cmdopts_update(cli_args, cmdopts: tp.Dict[str, str]):
        """
        Updates the core cmdopts dictionary with (key,value) pairs from the FORDYCA-specific cmdline options.
        """
        # Stage1
        updates = {
            'scenario': cli_args.scenario,
        }
        cmdopts.update(updates)


class CmdlineValidator(sierra.core.cmdline.CoreCmdlineValidator):
    pass
