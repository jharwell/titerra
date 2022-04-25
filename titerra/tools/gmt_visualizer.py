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
Graph Manipulation Target (GMT) visualizer for verifying that the structure
you hand to the swarm to build is what you think it is.

"""
# Core packages
import argparse
import typing as tp
import os
import sys
import logging

# 3rd party packages
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import matplotlib as mpl

# Project packages
from sierra.core.cmdline import BaseCmdline
import sierra.core.config
from sierra.core.vector import Vector3D
import sierra.core.logging
from sierra.core.utils import ArenaExtent

from titerra.projects.prism.variables.construct_targets import BaseConstructTarget
from titerra.projects.prism import gmt_spec


class GMTVisualizerCmdline(BaseCmdline):
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(prog='gmt_visualizer')

        self.parser.add_argument("-p", "--prismatic",
                                 help="""

                                 Output prismatic visualization of the input GMT
                                 spec.

                                 """,
                                 action='store_true')

        self.parser.add_argument("-g", "--graph",
                                 help="""

                                 Output graph visualization of the input GMT
                                 spec.

                                 """,
                                 action='store_true')

        self.parser.add_argument("--aspect-ratio",
                                 help="""

                                 The X:Y:Z aspect ratio to use for the
                                 graph. Mainly useful with --prismatic when
                                 generating graphs of individual blocks.

                                 """,
                                 default="1:1:1")

        self.parser.add_argument("input_file")
        self.parser.add_argument("-o", "--output-dir", required=True)


class GMTVisualizer():
    """
    Given a path to a .graphml file, generate a set of images which visualize
    different representations of the graph:

    - A prismatic representation with blocks

    - A face-adjacency representation showing which vertices (blocks) are
      connected to which other vertices through face adjacencies with its
      manhattan neighbors.
    """
    @staticmethod
    def _destringizer(x):
        if x.isalpha():
            return str(x)
        elif '(' in x and ')' in x:
            return eval(x)  # tuple

    def __init__(self, args: argparse.Namespace) -> None:
        sierra.core.logging.initialize('INFO')
        self.logger = logging.getLogger(__name__)

        self.graph_type = os.path.basename(args.input_file).split('.')[0]
        self.graph = nx.read_graphml(args.input_file,
                                     node_type=int)

        self.output_dir = args.output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.do_prismatic = args.prismatic
        self.do_graph = args.graph
        self.aspect_ratio = tuple(map(float, args.aspect_ratio.split(':')))

        assert self.do_prismatic or self.do_graph, \
            "Either --prismatic or --graph is required"

    def __call__(self) -> None:
        """
        Generate multiple rotated copies of the same structure graph plotted in
        3D in various ways, to aid in diagnostic debugging and for nice figures
        in papers.

        """
        for angle in range(0, 360, 30):
            self.logger.info("Generate for angle=%s", angle)
            if self.do_prismatic:
                ax = VolumetricPlotGenerator(self.graph)(self.aspect_ratio)
                self._output_plot(ax, angle)

            if self.do_graph:
                ax = GraphPlotGenerator()(self.graph)
                self._output_plot(ax, angle)

    def _output_plot(self, ax: Axes3D,  angle: int):
        ax.view_init(elev=None, azim=angle)
        fig = ax.get_figure()

        # Reduce whitespace around figure
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                            hspace=0, wspace=0)
        plt.margins(0, 0, 0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.gca().zaxis.set_major_locator(plt.NullLocator())

        # The path we are passed may contain dots from the controller name,
        # so we extract the leaf of that for manipulation to add the angle
        # of the view right before the file extension.
        fname = "{0}_{1}{2}".format(self.graph_type,
                                    angle,
                                    sierra.core.config.kImageExt)

        fig.savefig(os.path.join(self.output_dir, fname),
                    bbox_inches='tight',
                    dpi=sierra.core.config.kGraphDPI,
                    pad_inches=0)
        # Prevent memory accumulation (fig.clf() does not close everything)
        plt.close(fig)


class GraphPlotGenerator():
    def __call__(self, graph: nx.Graph) -> Axes3D:

        # Get node attributes
        anchors = nx.get_node_attributes(graph, gmt_spec.kVertexAnchorKey)
        assert anchors, \
            ("'{0}' is not the attribute of block anchors".format(
                gmt_spec.kVertexAnchorKey))

        # 3D network plot
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(projection='3d')

        # Hide grid lines and axes (easier to see graphs)
        ax.grid(False)
        ax.set_axis_off()

        # Loop on the pos dictionary to extract the x,y,z coordinates of each
        # node
        vals = [(vd, Vector3D.from_str(value)) for vd, value in anchors.items()]

        # Scatter plot
        ax.scatter([v[1].x for v in vals],
                   [v[1].y for v in vals],
                   [v[1].z for v in vals],
                   c=[graph.nodes[v[0]][gmt_spec.kVertexColorKey]
                       for v in vals],
                   s=400)

        # Loop on the list of edges to get the x,y,z, coordinates of the
        # connected nodes. Those two points are the extrema of the line to be
        # plotted
        vals = []
        for i, j in enumerate(graph.edges()):
            # Only show edges between pairs of vertices (i.e., ignore dangling
            # edges)
            u_vd = j[0]
            v_vd = j[1]

            if u_vd in anchors and v_vd in anchors:
                u_coord = Vector3D.from_str(anchors[u_vd])
                v_coord = Vector3D.from_str(anchors[v_vd])
                x = np.array((u_coord.x, v_coord.x))
                y = np.array((u_coord.y, v_coord.y))
                z = np.array((u_coord.z, v_coord.z))
                # Plot the connecting lines
                ax.plot(x,
                        y,
                        z,
                        linewidth=2,
                        c='black')

        return ax


class VolumetricPlotGenerator():
    def __init__(self, graph: nx.Graph) -> None:
        self.logger = logging.getLogger(__name__)
        self.graph = graph

    def __call__(self, aspect_ratio: tp.Tuple[int]) -> Axes3D:
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(projection='3d')

        ax.set_box_aspect(aspect=aspect_ratio)
        # Hide grid lines and axes (easier to see graphs)
        ax.grid(False)
        ax.set_axis_off()

        # Get node attributes
        anchors = nx.get_node_attributes(self.graph, gmt_spec.kVertexAnchorKey)
        assert anchors, \
            ("'{0}' is not the attribute of block anchors".format(
                gmt_spec.kVertexAnchorKey))

        # Extract the x,y,z coordinates of each node
        items = [(vd, Vector3D.from_str(value)) for vd, value in anchors.items()]

        ct_extent = self._calc_bb(self.graph)

        self.logger.info("Calculated bounding box ll=%s,ur=%s",
                         ct_extent.ll,
                         ct_extent.ur)

        # self._plot_as_voxels(ax, ct_extent, items)

        self._plot_as_matrix(ax, ct_extent, items)

        return ax

    def _plot_as_voxels(self,
                        ax: Axes3D,
                        ct_extent: ArenaExtent,
                        items: tp.Dict[int, Vector3D]) -> None:
        voxelarray = np.zeros((ct_extent.ur.x - ct_extent.ll.x,
                               ct_extent.ur.y - ct_extent.ll.y,
                               ct_extent.ur.z - ct_extent.ll.z))
        dims = list(voxelarray.shape)
        dims.append(4)
        colors = np.empty(tuple(dims), dtype=object)

        for vd, coord in items:
            rgba = VolumetricPlotGenerator._color_to_rgba(self.graph.nodes[vd][gmt_spec.kVertexColorKey],
                                                          0)

            voxelarray[coord.x][coord.y][coord.z] = 1
            colors[coord.x, coord.y, coord.z] = rgba

            # Set block extent voxels and colors
            block_extent = BaseConstructTarget.calc_block_extent_from_vd(self.graph,
                                                                         vd)

            # Index 0 is the anchor
            for e in block_extent[1:]:
                percentile = block_extent.index(e) / float(len(block_extent))
                rgba = VolumetricPlotGenerator._color_to_rgba(self.graph.nodes[vd][gmt_spec.kVertexColorKey],
                                                              percentile)
                voxelarray[e.x][e.y][e.z] = 1
                colors[e.x, e.y, e.z] = rgba

        ax.voxels(voxelarray, facecolors=colors, edgecolor='k')

    def _plot_as_matrix(self,
                        ax: Axes3D,
                        ct_extent: ArenaExtent,
                        items: tp.Dict[int, Vector3D]) -> None:
        xaxis = (ct_extent.ur.x - ct_extent.ll.x)
        yaxis = (ct_extent.ur.y - ct_extent.ll.y)
        zaxis = (ct_extent.ur.z - ct_extent.ll.z)
        colors = np.empty((xaxis, yaxis, zaxis, 4), dtype=object)

        for vd, coord in items:
            rgba = self._color_to_rgba(self.graph.nodes[vd][gmt_spec.kVertexColorKey],
                                       0)

            # Set block anchor voxels and color
            colors[coord.x, coord.y, coord.z] = rgba

            # Set block extent voxels and colors
            block_extent = BaseConstructTarget.calc_block_extent_from_vd(self.graph,
                                                                         vd)

            # Index 0 is the anchor
            for e in block_extent[1:]:
                percentile = block_extent.index(e) / float(len(block_extent))
                rgba = self._color_to_rgba(self.graph.nodes[vd][gmt_spec.kVertexColorKey],
                                           percentile)
                colors[e.x, e.y, e.z] = rgba

        for i, xi in enumerate(range(xaxis)):
            for j, yi in enumerate(range(yaxis)):
                for k, zi, in enumerate(range(zaxis)):
                    rgba = colors[i, j, k]

                    if any(c is None for c in rgba):
                        continue

                    # Plotting N cube elements at position pos
                    X, Y, Z = VolumetricPlotGenerator._cuboid_data((xi, yi, zi))
                    ax.plot_surface(X,
                                    Y,
                                    Z,
                                    color=rgba,
                                    rstride=1,
                                    cstride=1,
                                    alpha=rgba[3])

    @staticmethod
    def _cuboid_data(center, size=(1.0, 1.0, 1.0)):
        # code taken from
        # http://stackoverflow.com/questions/30715083/python-plotting-a-wireframe-3d-cuboid?noredirect=1&lq=1
        # suppose axis direction: x: to left; y: to inside; z: to upper

        # get the (left, outside, bottom) point
        o = [a - b / 2 for a, b in zip(center, size)]

        # get the length, width, and height
        l, w, h = size

        x = np.array([ \
            # x coordinate of points in bottom surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]],
            # x coordinate of points in upper surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]],
            # x coordinate of points in outside surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]],
            # x coordinate of points in inside surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]]])

        y = np.array([ \
            # y coordinate of points in bottom surface
            [o[1], o[1], o[1] + w, o[1] + w, o[1]],
            # y coordinate of points in upper surface
            [o[1], o[1], o[1] + w, o[1] + w, o[1]],
            # y coordinate of points in outside surface
            [o[1], o[1], o[1], o[1], o[1]],
            # y coordinate of points in inside surface
            [o[1] + w, o[1] + w, o[1] + w, o[1] + w, o[1] + w]])

        z = np.array([  \
            # z coordinate of points in bottom surface
            [o[2], o[2], o[2], o[2], o[2]],
            # z coordinate of points in upper surface
            [o[2] + h, o[2] + h, o[2] + h, o[2] + h, o[2] + h],
            # z coordinate of points in outside surface
            [o[2], o[2], o[2] + h, o[2] + h, o[2]],
            # z coordinate of points in inside surface
            [o[2], o[2], o[2] + h, o[2] + h, o[2]]])
        return x, y, z

    @staticmethod
    def _calc_bb(graph: nx.Graph) -> ArenaExtent:
        ur = Vector3D(0, 0, 0)

        for vd in graph.nodes:
            extent = BaseConstructTarget.calc_block_extent_from_vd(graph, vd)
            anchor = Vector3D.from_str(graph.nodes[vd][gmt_spec.kVertexAnchorKey])

            # Check block anchor cells
            ur.x = max(ur.x, anchor.x)
            ur.y = max(ur.y, anchor.y)
            ur.z = max(ur.z, anchor.z)

            # Check all cells in the block's extent
            for e in extent:
                ur.x = max(ur.x, e.x)
                ur.y = max(ur.y, e.y)
                ur.z = max(ur.z, e.z)

        ur += Vector3D(1, 1, 1)
        return ArenaExtent.from_corners(ll=Vector3D(0, 0, 0), ur=ur)

    @staticmethod
    def _color_to_rgba(color: str, percentile: float) -> tp.List[int]:
        if color == 'red':
            return [1.0, 0, percentile * 0.9 + 0.25, 1.0]

        if color == 'blue':
            return [0, percentile * 0.9 + 0.25, 1.0, 1.0]

        if color == 'green':
            return [percentile * 0.9 + 0.25, 1.0, 0.0, 1.0]

        if color == 'grey':
            return [0.5, 0.5, 0.5, 0.03]

        raise NotImplementedError(f"Color {color} -> rgba not implemented")


def main() -> None:
    cmdline = GMTVisualizerCmdline()
    args = cmdline.parser.parse_args()

    GMTVisualizer(args)()


if __name__ == '__main__':
    main()
