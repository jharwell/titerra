# Copyright 2021 John Harwell, All rights reserved.
#
#  This file is part of SIERRA.
#
#  SIERRA is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  SIERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  SIERRA.  If not, see <http://www.gnu.org/licenses/

# Core packages
import argparse

# 3rd party packages
import sierra.core.logging

# Project packages
from titerra.projects.prism.cmdline import Cmdline
import titerra.projects.prism.variables.ct_set as ctset


class GMTGeneratorCmdline():
    def __init__(self) -> None:

        self.parser = argparse.ArgumentParser(prog='gmt_generator')
        Cmdline.add_ct_args(self.parser, self.parser)

        self.parser.add_argument("-o", "--output-file", nargs='+')


class GMTGenerator():
    """
    Graph Manipulation Target (GMT) generator for generating targets outside of a SIERRA/TITERRA
    context for development/debugging.

    """

    def __init__(self) -> None:
        sierra.core.logging.initialize("TRACE")

    def __call__(self, args) -> None:
        target_set = ctset.factory(args.ct_specs,
                                   args.ct_orientations,
                                   "")
        for i in range(0, len(target_set.targets)):
            graph = target_set.targets[i].gen_graphml()
            opath = args.output_file[i]
            target_set.targets[i].write_graphml(graph, opath)


def main() -> None:
    cmdline = GMTGeneratorCmdline()
    args = cmdline.parser.parse_args()

    GMTGenerator()(args)


if __name__ == '__main__':
    main()
