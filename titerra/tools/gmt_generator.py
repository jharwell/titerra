# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
"""
Standalone tool for generating Graph Manipulation Targets (GMTs).

So that you don't need to have setup SIERRA or the TITERRA plugin to generate
stuff.
"""
# Core packages
import argparse
import logging  # type: ignore
import pathlib
import os

# 3rd party packages
import networkx as nx

# Project packages
import sierra.core.logging
from sierra.core.vector import Vector3D

from titerra.projects.prism.cmdline import Cmdline
import titerra.projects.prism.variables.ct_set as ctset
from titerra.projects.prism.variables.orientation import Orientation


class GMTGeneratorCmdline():
    """
    Holds all command line arguments for the GMT generator.
    """

    def __init__(self) -> None:

        self.parser = argparse.ArgumentParser(prog='gmt_generator')
        Cmdline.add_ct_args(self.parser)

        self.parser.add_argument("-f", "--output-file", nargs='+')
        self.parser.add_argument("--for-paper",
                                 help="""Generate the necessary graphs and
                                 modify them so that they can be subsequently
                                 visualized and dropped into the paper.
                                 """,
                                 action='store_true')
        self.parser.add_argument("-d", "--output-dir",
                                 help="""Output directory for graphs""")


class GMTGenerator():
    """
    Graph Manipulation Target (GMT) generator for generating targets outside of
    a SIERRA/TITERRA context for development/debugging.
    """

    def __init__(self) -> None:
        sierra.core.logging.initialize("TRACE")
        self.logger = logging.getLogger(__name__)

    def __call__(self, args) -> None:
        if args.for_paper:
            PaperFigureGenerator()(args)
        else:
            target_set = ctset.factory(args.ct_specs,
                                       args.ct_orientations,
                                       args.ct_paradigm,
                                       "")
            for i, _ in enumerate(target_set.targets):
                opath = pathlib.Path(args.output_dir, args.output_file[i])
                opath.mkdir(exist_ok=True)
                self.logger.info("Processing target '%s' -> '%s'",
                                 args.ct_specs[i],
                                 opath)
                graph = target_set.targets[i].gen_graph()
                target_set.targets[i].write_graphml(graph, opath)


class PaperFigureGenerator():
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def __call__(self, args) -> None:
        os.makedirs(args.output_dir, exist_ok=True)

        # Blocks
        self._blocks(args)

        # Coherent graphs
        self._coherent_cube(args)
        self._coherent_pyramid(args)
        self._coherent_cube_horizontal_hole(args)

        # Shells
        self._shells(args)

        # Incoherent graphs
        self._incoherent_cube_overhangs(args)

        # Complex example to show off the model
        self._levee(args)

    def _blocks(self, args: argparse.Namespace) -> None:
        stem = pathlib.Path(args.output_dir)

        # Cube block
        target = ctset.factory(["ct_specs.prism.beam1.1x1x1@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = target.gen_graph()
        target.write_graphml(graph, stem / "beam1.graphml")

        # Beam2 block
        target = ctset.factory(["ct_specs.prism.beam2.2x1x1@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = target.gen_graph()
        target.write_graphml(graph, stem / "beam2.graphml")

        # Beam3 block
        target = ctset.factory(["ct_specs.prism.beam3.3x1x1@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = target.gen_graph()
        target.write_graphml(graph, stem / "beam3.graphml")

    def _coherent_cube(self, args: argparse.Namespace) -> None:
        stem = pathlib.Path(args.output_dir)

        self.logger.info("Processing coherent cube")
        target = ctset.factory(["ct_specs.prism.beam1.3x3x3@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = target.gen_graph()
        target.write_graphml(graph,
                             stem / "coherent-cube.graphml")

    def _coherent_pyramid(self, args: argparse.Namespace) -> None:
        stem = pathlib.Path(args.output_dir)
        self.logger.info("Processing coherent pyramid")

        target = ctset.factory(["ct_specs.pyramid.beam1.7x7x4@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = target.gen_graph()
        target.write_graphml(graph,
                             stem / "coherent-pyramid.graphml")

    def _coherent_cube_horizontal_hole(self, args: argparse.Namespace) -> None:
        self.logger.info("Processing coherent cube (horizontal hole)")
        target = ctset.factory(["ct_specs.prism.mixed_beam.3x3x3@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = nx.Graph()

        # Base layer is all cube blocks
        for j in range(0, 3):
            for i in range(0, 3):
                target.graph_block_add(graph,
                                       'beam1',
                                       Vector3D(i, j, 0),
                                       Orientation("0"))

        # Second layer is 2 beam blocks along X separated by 1 unit (this is the
        # hole)
        target.graph_block_add(graph,
                               'beam3',
                               Vector3D(0, 0, 1),
                               Orientation("PI/2"))
        target.graph_block_add(graph,
                               'beam3',
                               Vector3D(2, 0, 1),
                               Orientation("PI/2"))

        # Top layer is 3 beam blocks along Y
        for j in range(0, 3):
            target.graph_block_add(graph,
                                   'beam3',
                                   Vector3D(0, j, 2),
                                   Orientation("0"))

        stem = pathlib.Path(args.output_dir)
        target.write_graphml(graph,
                             stem / "coherent-cube-horizontal-hole.graphml")

    def _shells(self, args: argparse.Namespace) -> None:
        self.logger.info("Processing shell")

        target = ctset.factory(["ct_specs.pyramid.beam1.5x3x4@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = nx.Graph()
        for i in range(1, 4):
            for j in range(1, 2):
                target.graph_block_add(graph,
                                       'beam1',
                                       Vector3D(i, j, 1),
                                       Orientation("0"))
        target.graph_block_add(graph,
                               'beam1',
                               Vector3D(2, 1, 2),
                               Orientation("0"))

        stem = pathlib.Path(args.output_dir)
        with_virtual_shell = target.graph_virtual_shell_add(graph)
        target.write_graphml(with_virtual_shell,
                             stem / "podium-virtual-shell.graphml")

        with_complement_shell = target.graph_complement_shell_add(graph)
        target.write_graphml(with_complement_shell,
                             stem / "podium-complement-shell.graphml")

    def _incoherent_cube_overhangs(self, args: argparse.Namespace) -> None:
        self.logger.info("Processing incoherent cube (overhangs)")
        target = ctset.factory(["ct_specs.prism.beam1.3x2x2@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = nx.Graph()
        for j in range(0, 2):
            for i in range(0, 2):
                target.graph_block_add(graph,
                                       'beam1',
                                       Vector3D(i, j, 0),
                                       Orientation("0"))

        for i in range(0, 1):
            for j in range(0, 2):
                target.graph_block_add(graph,
                                       'beam1',
                                       Vector3D(i, j, 1),
                                       Orientation("0"))

        for i in range(2, 3):
            for j in range(0, 2):
                target.graph_block_add(graph,
                                       'beam2',
                                       Vector3D(i, j, 1),
                                       Orientation("PI"))

        stem = pathlib.Path(args.output_dir)
        target.write_graphml(graph,
                             stem / "incoherent-cube-overhangs.graphml")

    def _levee(self, args: argparse.Namespace) -> None:
        self.logger.info("Processing levee example")
        XMAX = 20
        YMAX = 60
        ZMAX = 50
        target = ctset.factory([f"ct_specs.prism.beam1.{XMAX}x{YMAX}x{ZMAX}@0,0,0"],
                               ["0"],
                               args.ct_paradigm,
                               pathlib.Path()).targets[0]
        graph = nx.Graph()

        # First, generate bricklaying at Z=0 for all X,Y
        for j in range(0, YMAX):
            i = 0
            while i < XMAX:
                if (i == 0 and j % 2 == 0) or (i == XMAX-1 and j % 2 == 0):
                    target.graph_block_add(graph,
                                           'beam1',
                                           Vector3D(i, j, 0),
                                           Orientation("0"))
                else:
                    target.graph_block_add(graph,
                                           'beam2',
                                           Vector3D(i, j, 0),
                                           Orientation("0"))
                    i += 1
                i += 1

        # HORRIBLE HORRIBLE HORRIBLE unintelligible loop to try and generate a
        # curved levee wall. Doesn't work, but DOES generate something
        # no-trivial, which should be enough.
        for k in range(1, ZMAX):
            for i in range(0, XMAX):
                if i < int(XMAX/3):
                    for j in range(int(i / 2), 10 - (k + 2) + int(i/2)):
                        target.graph_block_add(graph,
                                               'beam3',
                                               Vector3D(
                                                   i, 10 + (j) * 3 + (k - 2), k),
                                               Orientation("PI/2"))
                elif i > int(XMAX / 3) and i <= int(2*XMAX/3):
                    for j in range(int(i / 2), 10 - (k + 2) + int(i/2)):
                        target.graph_block_add(graph,
                                               'beam2',
                                               Vector3D(
                                                   i, 8 + (j) * 3 + (k - 2), k),
                                               Orientation("PI/2"))
                else:
                    for j in range(int(i / 2), 10 - (k + 2) + int(i/2)):
                        target.graph_block_add(graph,
                                               'beam3',
                                               Vector3D(
                                                   i, 10 + (j) * 2 + (k - 2), k),
                                               Orientation("PI/2"))

        stem = pathlib.Path(args.output_dir)
        target.write_graphml(graph,
                             stem / "levee.graphml")


def main() -> None:
    cmdline = GMTGeneratorCmdline()
    args = cmdline.parser.parse_args()

    GMTGenerator()(args)


if __name__ == '__main__':
    main()
