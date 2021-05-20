# Copyright 2021 John Harwell, All rights reserved.
#
#  This file is part of TITERRA.
#
#  TITERRA is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  TITERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  TITERRA.  If not, see <http://www.gnu.org/licenses/

# Core packages
import typing as tp

# 3rd party packages
import implements

# Project packages
from sierra.core.utils import ArenaExtent
from sierra.core.vector import Vector3D
from sierra.core.variables.arena_shape import ArenaShape
from sierra.core.variables.base_variable import IBaseVariable
from projects.titan.variables.nest import Nest
from sierra.core.xml_luigi import XMLAttrChange, XMLAttrChangeSet, XMLTagRmList, XMLTagAddList


@implements.implements(IBaseVariable)
class RectangularArena():

    """
    Maps a list of desired arena dimensions to a list of sets of XML changes to set up the arena for
    the TITARRA project. This includes setup for the following C++ TITARRA components:

    - cpp:class:`~cosm::arena::base_arena_map` class and its derived classes.
    - cpp:class:`~cosm::repr::nest`.
    - cpp:class:`~cosm::subsystem::perception::base_perception_subsystems` and its derived classes.
    - cpp:class:`~cosm::convergence::convergence_calculator`.

    This class is a base class which should (almost) never be used on its own. Instead, derived
    classes defined in this file should be used instead.

    Attributes:
        extents: List of :class:`~sierra.core.utils.ArenaExtent` arena dimensions.
        attr_changes: List of sets of XML changes to apply to a template input file.
    """

    def __init__(self, extents: tp.List[ArenaExtent], dist_type: str) -> None:
        self.dist_type = dist_type
        self.shape = ArenaShape(extents)
        self.nest = Nest(self.dist_type, extents)
        self.extents = extents
        self.attr_changes = []

    def gen_attr_changelist(self) -> tp.List[XMLAttrChangeSet]:
        """
        Generate list of sets of changes necessary to make to the input file to correctly set up the
        simulation with the specified area size/shape.
        """
        if not self.attr_changes:
            grid_changes = [XMLAttrChangeSet(XMLAttrChange(".//arena_map/grid2D",
                                                           "dims",
                                                           "{0}, {1}, 2".format(extent.xsize(),
                                                                                extent.ysize())),
                                             XMLAttrChange(".//perception/grid2D", "dims",
                                                           "{0}, {1}, 2".format(extent.xsize(),
                                                                                extent.ysize())),
                                             )
                            for extent in self.extents]
            nest_changes = self.nest.gen_attr_changelist()
            shape_changes = self.shape.gen_attr_changelist()

            self.attr_changes = [XMLAttrChangeSet() for extent in self.extents]
            for achgs in self.attr_changes:
                for nchgs in nest_changes:
                    achgs |= nchgs
                for gchgs in grid_changes:
                    achgs |= gchgs
                for schgs in shape_changes:
                    achgs |= schgs

        return self.attr_changes

    def gen_tag_rmlist(self) -> tp.List[XMLTagRmList]:
        return []

    def gen_tag_addlist(self) -> tp.List[XMLTagAddList]:
        return []


class RectangularArenaTwoByOne(RectangularArena):
    """
    Define arenas that vary in size for each combination of extents in the specified X range and
    Y range, where the X dimension is always twices as large as the Y dimension.
    """

    def __init__(self,
                 x_range: tp.List[float],
                 y_range: tp.List[float],
                 z: float,
                 dist_type: str) -> None:
        super().__init__([ArenaExtent(Vector3D(x, y, z)) for x in x_range for y in y_range],
                         dist_type=dist_type)


class SquareArena(RectangularArena):
    """
    Define arenas that vary in size for each combination of extents in the specified X range and
    Y range, where the X and y extents are always equal.
    """

    def __init__(self,
                 sqrange: tp.List[float],
                 z: float,
                 dist_type: str) -> None:
        super().__init__([ArenaExtent(Vector3D(x, x, z)) for x in sqrange],
                         dist_type=dist_type)


__api__ = [
    'RectangularArena',
    'RectangularArenaTwoByOne',
    'SquareArena',
]
