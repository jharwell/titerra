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
Classes for different types of construction targets; cannot be used as a
batch criteria or as a variable on the cmdline. See :ref:`ln-prism-var-ct-set`
for usage documentation.
"""

# Core packages
import logging  # type: ignore
import typing as tp
import pathlib

# 3rd party packages
import networkx as nx
import implements
from sierra.core.vector import Vector3D
from sierra.core.experiment import xml
from sierra.core import types

# Project packages
from sierra.core.utils import ArenaExtent
from titerra.projects.prism import gmt_spec
from titerra.projects.prism.variables.orientation import Orientation


class IConcreteGMT(implements.Interface):
    @staticmethod
    def uuid(target_id: int) -> str:
        """
        Return the UUID for the target.
        """
        raise NotImplementedError

    def gen_graph(self) -> nx.Graph:
        """
        Generates the graphical representation of the target.
        """
        raise NotImplementedError


class BaseConstructTarget():
    """
    Base Construction target class defining one or more 3D structures to be
    built.

    Attributes:
        structure: Dictionary of (key,value) pairs defining the structure, as
                   returned by :class:`ConstructTargetSetParser`.
    """

    def __init__(self,
                 spec: types.CLIArgSpec,
                 target_id: int,
                 paradigm: str,
                 graphml_path: pathlib.Path):
        self.spec = spec
        self.paradigm = paradigm

        self.target_id = target_id
        self.graphml_path = graphml_path
        self.extent = ArenaExtent(origin=Vector3D(self.spec['anchor'][0],
                                                  self.spec['anchor'][1],
                                                  self.spec['anchor'][2]),
                                  dims=Vector3D(self.spec['bb'][0],
                                                self.spec['bb'][1],
                                                self.spec['bb'][2]))
        self.logger = logging.getLogger(__name__)
        self.logger.info("BB=%s", self.extent)

    def gen_xml(self, uuid: str) -> xml.TagAddList:
        """
        Generate XML tags for the construction target. This is common to all
        targets.
        """
        # Direct XML for simulation input file
        attrs = {
            'bounding_box': "{0},{1},{2}".format(self.extent.xsize(),
                                                 self.extent.ysize(),
                                                 self.extent.zsize()),
            'anchor': "{0},{1},{2}".format(self.extent.origin().x,
                                           self.extent.origin().y,
                                           self.extent.origin().z),
            'orientation': self.spec['orientation'],
            'graphml': self.graphml_path
        }
        return xml.TagAddList(xml.TagAdd('.//loop_functions/construct_targets',
                                         uuid,
                                         attrs,
                                         False))

    def write_graphml(self, graph: nx.Graph, path: pathlib.Path) -> None:
        """
        Writes generated GraphML to the filesystem.
        """
        self.logger.info("Write graph to %s", str(path))
        nx.write_graphml(graph, path)

    def coord_within_bb(self, c: Vector3D) -> bool:
        index_bounds = self.extent.dims
        if c.x < 0 or c.y < 0 or c.z < 0:
            return False

        if c.x >= index_bounds.x or c.y >= index_bounds.y or c.z >= index_bounds.z:
            return False

        return True

    def graph_virtual_shell_add(self, graph: nx.Graph) -> nx.Graph:
        for vd in graph.copy():
            xplus1 = Vector3D(1, 0, 0)
            xminus1 = Vector3D(-1, 0, 0)
            yplus1 = Vector3D(0, 1, 0)
            yminus1 = Vector3D(0, -1, 0)
            zplus1 = Vector3D(0, 0, 1)
            zminus1 = Vector3D(0, 0, -1)
            neighbors = [xplus1, xminus1, yplus1, yminus1, zplus1, zminus1]

            c = self.calc_vertex_coord(vd, self.extent)
            for n in neighbors:
                n_vd = self.calc_vertex_descriptor(c + n, self.extent)
                if n_vd not in graph and self.coord_within_bb(c + n):
                    self.graph_block_add(graph,
                                         'vbeam1',
                                         c + n,
                                         Orientation("0"))

        return graph

    def graph_complement_shell_add(self, graph: nx.Graph) -> nx.Graph:
        """
        Adds virtual vertices to the graph to form the complement shell.

        .. IMPORTANT:: This function will not work if the structure the graph
                       represents contains holes. I haven't yet implemented that
                       check when adding virtual vertices because it is
                       non-trivial.
        """
        for i in range(0, self.extent.xsize()):
            for j in range(0, self.extent.ysize()):
                for k in range(0, self.extent.zsize()):
                    c = Vector3D(i, j, k)
                    vd = self.calc_vertex_descriptor(c, self.extent)
                    if vd not in graph:
                        self.graph_block_add(graph,
                                             'vbeam1',
                                             c,
                                             Orientation("0"))

        return graph

    def graph_block_remove(self,
                           graph: nx.Graph,
                           c: Vector3D) -> None:
        """
        Removes the block at the specified anchor point from the graph.
        """
        vd = self.calc_vertex_descriptor(c, self.extent)
        graph.remove_node(vd)

    def graph_block_add(self,
                        graph: nx.Graph,
                        block_type: str,
                        c: Vector3D,
                        z_rot: Orientation) -> None:
        """
        Idempotently add a node of the specified type and its edges using the
        configured block representation paradigm.
        """
        if self.paradigm == 'semantic':
            self._graph_block_add_semantic(graph, block_type, c, z_rot)
        elif self.paradigm == 'edge':
            self._graph_block_add_edge(graph, block_type, c, z_rot)
        elif self.paradigm == 'vertex':
            raise NotImplementedError

    def _graph_block_add_edge(self,
                              graph: nx.Graph,
                              block_type: str,
                              c: Vector3D,
                              z_rot: Orientation) -> None:
        # Add the anchor
        vd1 = self.calc_vertex_descriptor(c, self.extent)
        self.logger.trace("Add %s anchor1: %s -> %s", block_type, vd1, c)
        attrs = {
            gmt_spec.kBlockTypeKey: gmt_spec.kBlockTypes[block_type],
            gmt_spec.kVertexAnchorKey: '{0},{1},{2}'.format(c.x, c.y, c.z),
            gmt_spec.kVertexZRotKey: str(z_rot),
            gmt_spec.kVertexColorKey: gmt_spec.kBlockColors[block_type]
        }
        assert not graph.has_node(vd1), f"vd={vd1}=vertex@{c} already exists"
        graph.add_node(vd1, **attrs)
        self._connect_vertex_to_neighbors(graph, vd1, block_type, c)

        size = gmt_spec.kBlockExtents[block_type]
        extent = self.calc_block_extent_from_pose(c, z_rot, size)

        # Adding cube block--no other end to add
        if len(extent) == 0:
            return

        # Add the other end
        end = extent[-1]
        vd2 = self.calc_vertex_descriptor(end, self.extent)
        self.logger.trace("Add %s anchor2: %s -> %s", block_type, vd2, end)

        # We only need block anchor and color attributes. All other
        # information is encoding into the graph itself in the form of
        # additional vertices.
        attrs = {
            gmt_spec.kVertexAnchorKey: '{0},{1},{2}'.format(end.x,
                                                            end.y,
                                                            end.z),
            gmt_spec.kVertexColorKey: gmt_spec.kBlockColors[block_type]
        }
        assert not graph.has_node(vd2), f"vd={vd2}=vertex@{c} already exists"
        graph.add_node(vd2, **attrs)
        self._connect_vertex_to_neighbors(graph, vd2, block_type, end)

        # Connect endpoints
        graph.add_edge(vd1, vd2, weight=1)

    def _graph_block_add_semantic(self,
                                  graph: nx.Graph,
                                  block_type: str,
                                  c: Vector3D,
                                  z_rot: Orientation) -> None:
        """
        Idempotently add a node of the specified type and its edges.
        """
        vd = self.calc_vertex_descriptor(c, self.extent)
        self.logger.trace("Add %s anchor: %s -> %s", block_type, vd, c)
        attrs = {
            gmt_spec.kBlockTypeKey: gmt_spec.kBlockTypes[block_type],
            gmt_spec.kVertexAnchorKey: '{0},{1},{2}'.format(c.x, c.y, c.z),
            gmt_spec.kVertexZRotKey: str(z_rot),
            gmt_spec.kVertexColorKey: gmt_spec.kBlockColors[block_type]
        }
        assert not graph.has_node(vd), f"vd={vd}=vertex@{c} already exists"
        graph.add_node(vd, **attrs)

        self._connect_vertex_to_neighbors(graph, vd, block_type, c)

    def _connect_vertex_to_neighbors(self,
                                     graph: nx.Graph,
                                     vd: int,
                                     block_type: str,
                                     c: Vector3D) -> None:
        xplus1 = Vector3D(1, 0, 0)
        xminus1 = Vector3D(-1, 0, 0)
        yplus1 = Vector3D(0, 1, 0)
        yminus1 = Vector3D(0, -1, 0)
        zminus1 = Vector3D(0, 0, -1)
        zplus1 = Vector3D(0, 0, 1)

        neighbors = [yplus1, yminus1, xplus1, xminus1, zminus1, zplus1]

        # Connect vertex to its manhattan neighbors.
        for n in neighbors:
            if not self.coord_within_bb(c + n):
                continue

            n_vd = self.calc_vertex_descriptor(c + n, self.extent)
            if n_vd not in graph:
                continue

            graph.add_edge(vd, n_vd, weight=1)
            self.logger.trace("Add %s edge: origin -> neighbor: % s -> %s (%s -> %s)",
                              block_type,
                              c,
                              c + n,
                              vd,
                              n_vd)

    def _graph_ramp2_add(self,
                         graph: nx.Graph,
                         c: Vector3D,
                         z_rot: Orientation) -> None:
        """
        .. IMPORTANT:: The attribute names and types specified here for vertices
                       and edges must match the names of the structs attached to
                       the boost:graph properties in PRISM exactly, or run-time
                       errors will result.

        """
        # Add anchor node
        vd = self.calc_vertex_descriptor(c, self.extent)
        self.logger.trace("Add ramp anchor: %s -> %s", vd, c)

        attrs = {
            gmt_spec.kBlockTypeKey: gmt_spec.kBlockTypes['ramp2'],
            gmt_spec.kVertexAnchorKey: '{0},{1},{2}'.format(c.x, c.y, c.z),
            gmt_spec.kVertexZRotKey: str(z_rot),
            gmt_spec.kVertexColorKey: gmt_spec.kBlockColors['ramp2']
        }
        graph.add_node(vd, **attrs)

        zratio = 1
        if z_rot.is_EW():
            xratio = 2
            yratio = 1
        elif z_rot.is_NS():
            xratio = 1
            yratio = 2

        if c.x < self.extent.xsize() - xratio:
            dest = Vector3D(c.x + xratio, c.y, c.z)
            graph.add_edge(vd,
                           self.calc_vertex_descriptor(dest, self.extent),
                           weight=str(xratio))
            self.logger.trace(
                "Add ramp edge: %s -> %s,weight=%s", c, dest, xratio)

        if c.y < self.extent.ysize() - yratio:
            dest = Vector3D(c.x, c.y + yratio, c.z)
            graph.add_edge(vd,
                           self.calc_vertex_descriptor(dest, self.extent),
                           weight=str(yratio))
            self.logger.trace(
                "Add ramp edge: %s -> %s,weight=%s", c, dest, yratio)

        if c.z < self.extent.zsize() - zratio:
            dest = Vector3D(c.x, c.y, c.z + zratio)
            graph.add_edge(vd,
                           self.calc_vertex_descriptor(dest, self.extent),
                           weight=str(zratio))
            self.logger.trace(
                "Add ramp edge: %s -> %s,weight=%s", c, dest, zratio)

    @staticmethod
    def calc_vertex_coord(vd: int, extent: ArenaExtent) -> Vector3D:
        z = int(vd / (extent.xsize() * extent.ysize()))
        vd = vd - (z * extent.xsize() * extent.ysize())

        y = int(vd / extent.xsize())
        x = vd % extent.xsize()
        return Vector3D(x, y, z)

    @staticmethod
    def calc_vertex_descriptor(n: Vector3D, extent: ArenaExtent) -> int:
        """
        Map an (X,Y,Z) coordinate to a unique integer corresponding to its
        position in a 1D representation of a 3D array.

        """
        return n.z * extent.xsize() * extent.ysize() + \
            n.y * extent.xsize() + \
            n.x

    @staticmethod
    def calc_block_extent(graph: nx.Graph,
                          anchor: Vector3D,
                          bb: ArenaExtent) -> tp.List[Vector3D]:
        vd = BaseConstructTarget.calc_vertex_descriptor(anchor, bb)
        return BaseConstructTarget.calc_block_extent_from_vd(graph, vd)

    @staticmethod
    def calc_block_extent_from_pose(anchor: Vector3D,
                                    z_rot: Orientation,
                                    size: int) -> tp.List[Vector3D]:
        coords = []

        if size == 1:
            return coords

        if z_rot.is_N():
            for y in range(anchor.y, anchor.y + size):
                coords.append(anchor + Vector3D(0, 1, 0) * y)
        elif z_rot.is_S():
            for y in range(anchor.y, anchor.y - size, -1):
                coords.append(anchor - Vector3D(0, 1, 0) * y)
        elif z_rot.is_E():
            for x in range(anchor.x, anchor.x + size):
                coords.append(anchor + Vector3D(1, 0, 0) * x)
        elif z_rot.is_W():
            for x in range(anchor.x, anchor.x - size, -1):
                coords.append(anchor - Vector3D(1, 0, 0) * x)

        return coords

    @staticmethod
    def calc_block_extent_from_vd(graph: nx.Graph,
                                  vd: int) -> tp.List[Vector3D]:
        for k, v in gmt_spec.kBlockTypes.items():
            if v == graph.nodes[vd][gmt_spec.kBlockTypeKey]:
                block_type = k

        z_rot = Orientation.from_num(float(graph.nodes[vd][gmt_spec.kVertexZRotKey]))

        extent = gmt_spec.kBlockExtents[block_type]

        anchor = Vector3D.from_str(graph.nodes[vd][gmt_spec.kVertexAnchorKey])
        return BaseConstructTarget.calc_block_extent_from_pose(anchor,
                                                               z_rot,
                                                               extent)


@implements.implements(IConcreteGMT)
class Beam1Prism(BaseConstructTarget):
    """
    Construction target class for 3D rectangular prismatic structures composed
    only of cube blocks.
    """
    @staticmethod
    def uuid(target_id: int) -> str:
        return 'beam1prism' + str(target_id)

    def __init__(self,
                 spec: types.CLIArgSpec,
                 target_id: int,
                 paradigm: str,
                 graphml_path: pathlib.Path) -> None:
        super().__init__(spec, target_id, paradigm, graphml_path)

    def gen_graph(self) -> nx.Graph:
        graph = nx.Graph()

        # For rectprisms, there is no difference in the generated GRAPHML for +X
        # vs -X, or +Y vs -Y.
        if self.spec['orientation'].is_EW():
            for x in range(0, self.extent.xsize()):
                for y in range(0, self.extent.ysize()):
                    for z in range(0, self.extent.zsize()):
                        self.graph_block_add(graph,
                                             'beam1',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])
        elif self.spec['orientation'].is_NS():
            for y in range(0, self.extent.ysize()):
                for x in range(0, self.extent.xsize()):
                    for z in range(0, self.extent.zsize()):
                        self.graph_block_add(graph,
                                             'beam1',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])
        return graph


@implements.implements(IConcreteGMT)
class Beam2Prism(BaseConstructTarget):
    """
    Construction target class for 3D rectangular prismatic structures composed
    only of beam2 blocks.
    """
    @staticmethod
    def uuid(target_id: int) -> str:
        return 'beam2_prism' + str(target_id)

    def __init__(self,
                 spec: types.CLIArgSpec,
                 target_id: int,
                 paradigm: str,
                 graphml_path: pathlib.Path) -> None:
        super().__init__(spec, target_id, paradigm, graphml_path)

    def gen_graph(self) -> nx.Graph:
        graph = nx.Graph()

        if self.spec['orientation'].is_EW():
            for x in range(0, self.extent.xsize(), 2):
                for y in range(0, self.extent.ysize()):
                    for z in range(0, self.extent.zsize()):
                        self.graph_block_add(graph,
                                             'beam2',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])
        elif self.spec['orientation'].is_NS():
            for y in range(0, self.extent.ysize(), 2):
                for x in range(0, self.extent.xsize()):
                    for z in range(0, self.extent.zsize()):
                        self.graph_block_add(graph,
                                             'beam2',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])
        return graph


@implements.implements(IConcreteGMT)
class Beam3Prism(BaseConstructTarget):
    """
    Construction target class for 3D rectangular prismatic structures composed
    only of beam3 blocks.
    """
    @staticmethod
    def uuid(target_id: int) -> str:
        return 'beam3_prism' + str(target_id)

    def __init__(self,
                 spec: types.CLIArgSpec,
                 target_id: int,
                 paradigm: str,
                 graphml_path: pathlib.Path) -> None:
        super().__init__(spec, target_id, paradigm, graphml_path)

    def gen_graph(self) -> nx.Graph:
        graph = nx.Graph()

        if self.spec['orientation'].is_EW():
            for x in range(0, self.extent.xsize(), 3):
                for y in range(0, self.extent.ysize()):
                    for z in range(0, self.extent.zsize()):
                        self.graph_block_add(graph,
                                             'beam3',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])
        elif self.spec['orientation'].is_NS():
            for y in range(0, self.extent.ysize(), 3):
                for x in range(0, self.extent.xsize()):
                    for z in range(0, self.extent.zsize()):
                        self.graph_block_add(graph,
                                             'beam3',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])
        return graph


@implements.implements(IConcreteGMT)
class MixedBeamPrism(BaseConstructTarget):
    """
    Construction target class for 3D rectangular prismatic structures composed
    of a mix of beam blocks.

    """
    @staticmethod
    def uuid(target_id: int) -> str:
        return 'mixed_beam_prism' + str(target_id)

    def __init__(self,
                 spec: types.CLIArgSpec,
                 target_id: int,
                 paradigm: str,
                 graphml_path: pathlib.Path) -> None:
        super().__init__(spec, target_id, paradigm, graphml_path)

    def gen_graph(self) -> nx.Graph:
        raise NotImplementedError("Error: Cannot generate mixed graph--manual \
                                   specification required")


@implements.implements(IConcreteGMT)
class Beam1Pyramid(BaseConstructTarget):
    """
    Construction target class for 3D pyramids composed only of cube blocks;
    i.e., a stepped pyramid.
    """
    @staticmethod
    def uuid(target_id: int) -> str:
        return 'beam1_pyramid' + str(target_id)

    def __init__(self,
                 spec: types.CLIArgSpec,
                 target_id: int,
                 paradigm: str,
                 graphml_path: pathlib.Path) -> None:
        super().__init__(spec, target_id, paradigm, graphml_path)

    def gen_graph(self) -> nx.Graph:
        graph = nx.Graph()

        # For rectprisms, there is no difference in the generated GRAPHML for +X
        # vs -X, or +Y vs -Y.
        z = 0
        if self.spec['orientation'].is_EW():
            for z in range(z, self.extent.zsize()):
                for x in range(z, self.extent.xsize() - z):
                    for y in range(z, self.extent.ysize() - z):
                        self.graph_block_add(graph,
                                             'beam1',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])
        elif self.spec['orientation'].is_NS():
            for z in range(0, self.extent.zsize()):
                for y in range(z, self.extent.ysize() - z):
                    for x in range(z, self.extent.xsize() - z):
                        self.graph_block_add(graph,
                                             'beam1',
                                             Vector3D(x, y, z),
                                             self.spec['orientation'])

        return graph


@implements.implements(IConcreteGMT)
class Ramp(BaseConstructTarget):
    """
    Construction target class for 3D ramps.
    """

    kRAMP_LENGTH_RATIO = 2
    """
    The ratio between the length of beam1 blocks and ramp blocks.
    """

    @staticmethod
    def uuid(target_id: int) -> str:
        return 'ramp' + str(target_id)

    def __init__(self,
                 spec: types.CLIArgSpec,
                 target_id: int,
                 paradigm: str,
                 graphml_path: pathlib.Path) -> None:
        super().__init__(spec, target_id, paradigm, graphml_path)
        self.tag_adds = []
        self._structure_sanity_checks()

    def _structure_sanity_checks(self):
        if self.spec['orientation'].is_EW():
            assert self.extent.xsize() % self.kRAMP_LENGTH_RATIO == 0,\
                "X size={0} not a multiple for ramp block length ratio={1}".format(self.extent.xsize(),
                                                                                   self.kRAMP_LENGTH_RATIO)
        elif self.spec['orientation'].is_NS():
            assert self.extent.ysize() % self.kRAMP_LENGTH_RATIO == 0,\
                "Y size={0} not a multiple for ramp block length ratio {1}".format(self.extent.ysize(),
                                                                                   self.kRAMP_LENGTH_RATIO)

    def gen_graph(self) -> nx.Graph:
        graph = nx.Graph()

        # First, generate beam1 blocks
        self._gen_beam1_blocks(graph)

        # Then, generate ramp blocks
        self._gen_ramp_blocks(graph)

        return graph

    def _gen_ramp_blocks(self, graph: nx.Graph) -> None:
        """
        Add the nodes containing the anchor cells of ramp blocks to the
        structure graph, along with the connections to their neighbors.

        """
        ratio = self.kRAMP_LENGTH_RATIO

        if self.spec['orientation'].is_EW():
            corr = 1
            for z in range(0, self.extent.zsize()):
                x = self.extent.xsize() - ratio * corr
                for y in range(0, self.extent.ysize()):
                    self.graph_block_add(graph,
                                         'ramp',
                                         Vector3D(x, y, z))
                corr += 1

        elif self.spec['orientation'].is_NS():
            for z in range(0, self.extent.zsize()):
                y = self.extent.ysize() - ratio * corr
                for x in range(0, self.extent.xsize()):
                    self.graph_block_add(graph,
                                         'ramp2',
                                         Vector3D(x, y, z))
                corr += 1

    def _gen_beam1_blocks(self, graph: nx.Graph) -> None:
        """
        Add the nodes containing the anchor cells of beam1 blocks to the
        structure graph, along with the connections to their neighbors.

        """
        ratio = self.kRAMP_LENGTH_RATIO

        if self.spec['orientation'].is_EW():
            corr = 1
            for z in range(0, self.extent.zsize()):
                for x in range(0, self.extent.xsize() - ratio * corr):
                    for y in range(0, self.extent.ysize()):
                        self.graph_block_add(graph,
                                             'beam1',
                                             Vector3D(x, y, z),
                                             1)
                corr += 1
        elif self.spec['orientation'].is_NS():
            corr = 1
            for z in range(0, self.extent.zsize()):
                for y in range(0, self.extent.ysize() - ratio * corr):
                    for x in range(0, self.extent.xsize()):
                        self.graph_block_add(graph,
                                             'beam1',
                                             Vector3D(x, y, z),
                                             1)
                corr += 1
