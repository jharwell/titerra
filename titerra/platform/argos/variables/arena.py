# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import typing as tp

# 3rd party packages
import implements
from sierra.core.utils import ArenaExtent
from sierra.core.vector import Vector3D
from sierra.plugins.platform.argos.variables.arena_shape import ArenaShape
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.experiment import xml

# Project packages
from titerra.platform.argos.variables.nest import Nest


@implements.implements(IBaseVariable)
class RectangularArena():
    """Maps a list of desired arena dimensions to a list of sets of XML changes to
    set up the arena for the TITARRA project. This includes setup for the
    following C++ TITERRA components:

    - cpp:class:`~cosm::arena::base_arena_map` class and its derived classes.

    - cpp:class:`~cosm::repr::nest`.

    - cpp:class:`~cosm::subsystem::perception::base_perception_subsystem` and
      its derived classes.

    - cpp:class:`~cosm::convergence::convergence_calculator`.

    This class is a base class which should (almost) never be used on its
    own. Instead, derived classes defined in this file should be used instead.

    Attributes:

        extents: List of arena extents.

        gen_nests: Should a nest/nests be generated for each extent?

        dist_type: The block distribution for all extents. Only used if nests
                   are generated.

    """

    def __init__(self,
                 extents: tp.List[ArenaExtent],
                 nests_config: dict[str, str]) -> None:
        self.nests_config = nests_config
        self.shapes = ArenaShape(extents)
        self.extents = extents

        if self.nests_config:
            self.nests_config.update({'from_src': 'arena'})
            self.nests = {arena: Nest(config=self.nests_config, arena=arena)
                          for arena in self.extents}
        else:
            self.nests = {}

        self.attr_changes = []
        self.tag_adds = []
        self.tag_rms = []

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        """
        Generate list of sets of changes necessary to make to the input file to
        correctly set up the simulation with the specified area size/shape.
        """
        if not self.attr_changes:
            grid_changes = [xml.AttrChangeSet(
                xml.AttrChange(".//arena_map/grid2D",
                               "dims",
                               "{0}, {1}, 2".format(extent.xsize(),
                                                    extent.ysize())),
                xml.AttrChange(".//perception/grid2D", "dims",
                               "{0}, {1}, 2".format(extent.xsize(),
                                                    extent.ysize())),
            )
                for extent in self.extents]
            shape_changes = self.shapes.gen_attr_changelist()
            self.attr_changes = [xml.AttrChangeSet() for extent in self.extents]
            for achgs in self.attr_changes:
                for gchgs in grid_changes:
                    achgs |= gchgs
                for schgs in shape_changes:
                    achgs |= schgs

        return self.attr_changes

    def gen_tag_rmlist(self) -> tp.List[xml.TagRmList]:
        if not self.tag_rms:
            for arena in self.nests.keys():
                rms = self.nests[arena].gen_tag_rmlist()
                for rm in rms:
                    self.tag_rms.append(rm)

        return self.tag_rms

    def gen_tag_addlist(self) -> tp.List[xml.TagAddList]:
        if not self.tag_adds:
            for arena in self.nests.keys():
                adds = self.nests[arena].gen_tag_addlist()
                for add in adds:
                    self.tag_adds.append(add)

        return self.tag_adds

    def gen_files(self) -> None:
        pass


class RectangularArenaTwoByOne(RectangularArena):
    """Define arenas that vary in size for each combination of extents in the
    specified X range and Y range, where the X dimension is always twices as
    large as the Y dimension.

    """

    def __init__(self,
                 x_range: tp.List[float],
                 y_range: tp.List[float],
                 z: float,
                 nests_config: tp.Dict[str, str]
                 ) -> None:
        super().__init__([ArenaExtent(Vector3D(x, y, z)) for x in x_range for y in y_range],
                         nests_config=nests_config)


class SquareArena(RectangularArena):
    """Define arenas that vary in size for each combination of extents in the
    specified X range and Y range, where the X and y extents are always equal.

    """

    def __init__(self,
                 sqrange: tp.List[float],
                 z: float,
                 nests_config: tp.Dict[str, str]
                 ) -> None:
        super().__init__([ArenaExtent(Vector3D(x, x, z)) for x in sqrange],
                         nests_config=nests_config)


__api__ = [
    'RectangularArena',
    'RectangularArenaTwoByOne',
    'SquareArena',


]
