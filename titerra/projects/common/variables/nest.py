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
import math

# 3rd party packages
import implements

# Project packages
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.utils import ArenaExtent as ArenaExtent
from sierra.core.xml import XMLAttrChangeSet, XMLTagRmList, XMLTagAddList, XMLTagRm, XMLTagAdd, XMLAttrChange


@implements.implements(IBaseVariable)
class Nest():

    """
    Defines the position/size/etc of the nest based on block distribution type.

    Attributes:
      dist_type: The block distribution type. Valid values are [single_source, dual_source,
                                                                quad_source, random, powerlaw].
      extents: List of arena extents to generation nest poses for.
    """

    def __init__(self,
                 src: str,
                 arena: tp.Optional[ArenaExtent] = None,
                 dist_type: tp.Optional[str] = None) -> None:
        self.dist_type = dist_type
        self.src = src
        self.arena = arena
        self.tag_adds = []  # type: tp.List

    def gen_attr_changelist(self) -> tp.List[XMLAttrChangeSet]:
        return []

    def gen_tag_rmlist(self) -> tp.List[XMLTagRmList]:
        return [XMLTagRmList(XMLTagRm(".//arena_map", "nests"))]

    def gen_files(self) -> None:
        pass

    def gen_tag_addlist(self) -> tp.List[XMLTagAddList]:
        """
        Generate list of new tags changes necessary to make to the input file to correctly set up
        the simulation for the specified block distribution/nest.
        """

        if self.tag_adds:
            return [self.tag_adds]

        if self.src == 'arena':
            root = XMLTagAdd(".//arena_map", "nests", {}, False)
            self.tag_adds = self.gen_adds_from_arena()
            self.tag_adds.prepend(root)
        else:
            assert False, "Bad source {0}".format(self.src)

        return [self.tag_adds]

    def gen_adds_from_arena(self) -> XMLTagAddList:
        if self.dist_type == 'SS':
            attr = {
                "dims": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.1,
                                                  self.arena.ur.y * 0.8),
                "center": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.1,
                                                    self.arena.ur.y / 2.0)
            }
            return XMLTagAddList(
                XMLTagAdd(".//arena_map/nests", "nest", attr, False),
                XMLTagAdd(".//params", "nest", attr, False)
            )

        if self.dist_type == 'DS':
            attr = {
                "dims": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.1,
                                                  self.arena.ur.y * 0.8),
                "center": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.5,
                                                    self.arena.ur.y * 0.5),
            }
            return XMLTagAddList(
                XMLTagAdd(".//arena_map/nests", "nest", attr, False),
                XMLTagAdd(".//params", "nest", attr, False)
            )
        if (self.dist_type == 'PL' or self.dist_type == 'RN' or self.dist_type == 'QS'):
            attr = {
                "dims": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.2,
                                                  self.arena.ur.y * 0.2),
                "center": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.5,
                                                    self.arena.ur.y * 0.5),
            }
            return XMLTagAddList(
                XMLTagAdd(".//arena_map/nests", "nest", attr, False),
                XMLTagAdd(".//params", "nest", attr, False)
            )

        # Eventually, I might want to have definitions for the other block distribution
        # types
        raise NotImplementedError
