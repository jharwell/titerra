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
"""
Graph Manipulation Target (GMT) visualizer for verifying that the structure you hand to the swarm to
build is what you think it is.
"""
# Core packages
import argparse
import typing as tp
import os

# 3rd party packages
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

# Project packages
from sierra.core.cmdline import BaseCmdline
from titerr.aprojects.prism.variables.construction_targets import BaseConstructTarget
import sierra.core.config


class GMTVisualizerCmdline(BaseCmdline):
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(prog='gmt_visualizer')

        self.parser.add_argument("input_file")
        self.parser.add_argument("-o", "--output-dir", required=True)


class GMTVisualizer():
    @staticmethod
    def _destringizer(x):
        if x.isalpha():
            return str(x)
        elif '(' in x and ')' in x:
            return eval(x)  # tuple

    def __init__(self, args) -> None:
        self.graph_type = os.path.basename(args.input_file).split('.')[0]
        self.graph = nx.read_graphml(args.input_file, label=None, destringizer=self._destringizer)
        self.output_dir = args.output_dir

    def __call__(self) -> None:
        """
        Generate multiple rotated copies of the same structure graph plotted in 3D, to aid in
        diagnostic debugging.
        """
        for angle in range(0, 360, 30):
            ax = self._gen_plot(self.graph, angle)
            ax.view_init(elev=None, azim=angle)
            fig = ax.get_figure()
            # The path we are passed may contain dots from the controller same, so we extract the
            # leaf of that for manipulation to add the angle of the view right before the file
            # extension.
            fname = "{0}_{1}{2}".format(self.graph_type, angle, sierra.core.config.kImageExt)
            fig.savefig(os.path.join(self.output_dir, fname),
                        bbox_inches='tight',
                        dpi=sierra.core.config.kGraphDPI,
                        pad_inches=0)
            plt.close(fig)  # Prevent memory accumulation (fig.clf() does not close everything)

    def _gen_plot(self, graph: nx.Graph, angle: int) -> Axes3D:

        # Get node attributes
        positions = nx.get_node_attributes(graph, 'pos')

        # 3D network plot
        fig = plt.figure(figsize=(10, 7))
        ax = Axes3D(fig)

        # Loop on the pos dictionary to extract the x,y,z coordinates of each node
        for key, value in positions.items():
            # Scatter plot
            ax.scatter(value[0],
                       value[1],
                       value[2],
                       edgecolors='k',
                       c=graph.nodes[key]['color'],
                       s=200)

        # Loop on the list of edges to get the x,y,z, coordinates of the connected nodes
        # Those two points are the extrema of the line to be plotted
        for i, j in enumerate(graph.edges()):
            # Not all edge pairs exist
            if j[0] in positions and j[1] in positions:
                x = np.array((positions[j[0]][0], positions[j[1]][0]))
                y = np.array((positions[j[0]][1], positions[j[1]][1]))
                z = np.array((positions[j[0]][2], positions[j[1]][2]))

                # Plot the connecting lines
                ax.plot(x, y, z, c='black')

        return ax


def main() -> None:
    cmdline = GMTVisualizerCmdline()
    args = cmdline.parser.parse_args()

    GMTVisualizer(args)()


if __name__ == '__main__':
    main()
