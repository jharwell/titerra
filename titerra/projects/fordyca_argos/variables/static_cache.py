# Copyright 2018 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import typing as tp

# 3rd party packages
import implements

# Project packages
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.utils import ArenaExtent as ArenaExtent
from sierra.core.experiment import xml


@implements.implements(IBaseVariable)
class StaticCache():

    """
    Defines the size and capacity of a static cache with.

    Attributes:
        sizes: List of the # of blocks the cache should have each time the simulation respawns
               it.
        extents: List of the extents within the arena to generate definitions for.
    """
    kCacheDimFrac = 0.15

    def __init__(self, sizes: tp.List[int], extents: tp.List[ArenaExtent]):
        self.sizes = sizes
        self.extents = extents
        self.attr_changes = None

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        """
        Generate list of sets of changes necessary to make to the input file to
        correctly set up the simulation for the list of static cache sizes
        specified in constructor.

        - Disables dynamic caches

        - Enables static caches

        - Sets static cache size (initial # blocks upon creation) and its
          dimensions in the arena during its existence.

        """
        if self.attr_changes is None:

            self.attr_changes = [xml.AttrChangeSet(
                xml.AttrChange(".//loop_functions/caches/dynamic",
                               "enable",
                               "false"),
                xml.AttrChange(".//loop_functions/caches/static",
                               "enable",
                               "true"),
                xml.AttrChange(".//loop_functions/caches/static",
                               "size",
                               "{0:.9f}".format(s)),
                xml.AttrChange(".//loop_functions/caches",
                               "dimension",
                               "{0:.9f}".format(max(e.ur.x * self.kCacheDimFrac,
                                                    e.ur.y * self.kCacheDimFrac)))
            ) for e in self.extents for s in self.sizes]

        return self.attr_changes

    def gen_tag_rmlist(self) -> tp.List[xml.TagRmList]:
        return []

    def gen_tag_addlist(self) -> tp.List[xml.TagAddList]:
        return []

    def gen_files(self) -> None:
        pass
