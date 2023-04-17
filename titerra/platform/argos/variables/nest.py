# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import typing as tp
import math

# 3rd party packages
import implements

# Project packages
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.utils import ArenaExtent as ArenaExtent
from sierra.core.experiment import xml


@implements.implements(IBaseVariable)
class Nest():

    """
    Defines the position/size/etc of the nest based on block distribution type.

    """

    def __init__(self,
                 config: tp.Dict[str, str],
                 arena: tp.Optional[ArenaExtent] = None) -> None:
        self.config = config
        self.arena = arena
        self.tag_adds = []  # type: tp.List

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        return []

    def gen_tag_rmlist(self) -> tp.List[xml.TagRmList]:
        return [xml.TagRmList(xml.TagRm(".//arena_map", "nests"))]

    def gen_files(self) -> None:
        pass

    def gen_tag_addlist(self) -> tp.List[xml.TagAddList]:
        """
        Generate list of new tags changes necessary to make to the input file to correctly set up
        the simulation for the specified block distribution/nest.
        """

        if self.tag_adds:
            return [self.tag_adds]

        if self.config['from_src'] == 'arena':
            root = xml.TagAdd(".//arena_map", "nests", {}, False)
            self.tag_adds = self._gen_adds_from_arena()
            self.tag_adds.prepend(root)
        else:
            assert False, "Bad source {0}".format(self.config['from_src'])

        return [self.tag_adds]

    def _gen_adds_from_arena(self) -> xml.TagAddList:
        if self.config['pos_src'] == 'dist':
            return self._gen_adds_from_block_dist()
        elif self.config['pos_src'] == 'corner':
            return self._gen_adds_for_corner()
        else:
            raise NotImplementedError(("Nest position paradigm must be "
                                       "'dist' or 'corner'"))

    def _gen_adds_for_corner(self) -> xml.TagAddList:
        """
        Generate XML to put the nest in one of the arena corners.
        """
        if self.config['corner'] == 'UL':
            attr = {
                "dims": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.2,
                                                  self.arena.ur.y * 0.2),
                "center": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.1,
                                                    self.arena.ur.y -
                                                    self.arena.ur.y * 0.1),
            }
            return xml.TagAddList(
                xml.TagAdd(".//arena_map/nests", "nest", attr, False),
                xml.TagAdd(".//params", "nest", attr, False)
            )

        # Eventually, I might want to have definitions for the other corners
        raise NotImplementedError

    def _gen_adds_from_block_dist(self) -> xml.TagAddList:
        """
        Generate XML for the nest location, size based on the block distribution.
        """
        if self.config['dist'] == 'SS':
            attr = {
                "dims": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.2,
                                                  self.arena.ur.y * 0.2),
                "center": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.5,
                                                    self.arena.ur.y * 0.5),
            }

            return xml.TagAddList(
                xml.TagAdd(".//arena_map/nests", "nest", attr, False),
                xml.TagAdd(".//params", "nest", attr, False)
            )

        if self.config['dist'] == 'DS':
            attr = {
                "dims": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.1,
                                                  self.arena.ur.y * 0.8),
                "center": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.5,
                                                    self.arena.ur.y * 0.5),
            }
            return xml.TagAddList(
                xml.TagAdd(".//arena_map/nests", "nest", attr, False),
                xml.TagAdd(".//params", "nest", attr, False)
            )

        if (self.config['dist'] == 'PL' or
            self.config['dist'] == 'RN' or
                self.config['dist'] == 'QS'):
            attr = {
                "dims": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.2,
                                                  self.arena.ur.y * 0.2),
                "center": "{0:.9f}, {1:.9f}".format(self.arena.ur.x * 0.5,
                                                    self.arena.ur.y * 0.5),
            }
            return xml.TagAddList(
                xml.TagAdd(".//arena_map/nests", "nest", attr, False),
                xml.TagAdd(".//params", "nest", attr, False)
            )

        # Eventually, I might want to have definitions for the other block distribution
        # types
        raise NotImplementedError
