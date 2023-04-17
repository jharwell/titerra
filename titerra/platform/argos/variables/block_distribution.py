# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
#

# core packages
import math
import typing as tp
import logging

# 3rd party packages
import implements

from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.utils import ArenaExtent
from sierra.core.experiment import xml

# Project packages


@implements.implements(IBaseVariable)
class BaseDistribution():
    """
    Defines the type of distribution of objects in the arena.

    Attributes:
        dist_type: [single_source, dual_source, quad_source, powerlaw, random].
    """

    def __init__(self, dist_type: str) -> None:
        self.dist_type = dist_type
        self.attr_changes = []  # type: tp.List
        self.logger = logging.getLogger(__name__)

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        """Generate a list of sets of changes necessary to make to the input file to
        correctly set up the simulation with the specified block distribution

        """
        if not self.attr_changes:
            self.attr_changes = [xml.AttrChangeSet(
                xml.AttrChange(".//arena_map/blocks/distribution",
                               "dist_type",
                               "{0}".format(self.dist_type))
            )]
        return self.attr_changes

    def gen_tag_rmlist(self) -> tp.List[xml.TagRmList]:
        return []

    def gen_tag_addlist(self) -> tp.List[xml.TagAddList]:
        return []

    def gen_files(self) -> None:
        pass


class SingleSource(BaseDistribution):
    def __init__(self) -> None:
        super().__init__("single_source")


class DualSource(BaseDistribution):
    def __init__(self) -> None:
        super().__init__("dual_source")


class QuadSource(BaseDistribution):
    def __init__(self) -> None:
        super().__init__("quad_source")


class PowerLaw(BaseDistribution):
    def __init__(self, arena_dim: ArenaExtent) -> None:
        super().__init__("powerlaw")
        self.arena_dim = arena_dim

    def gen_attr_changelist(self):
        r"""Generate a list of sets of changes necessary to make to the input file to
        correctly set up the simulation for the powerlaw block distribution.

        2021/04/12: Update parameters so that you get better distributions at
        BOTH small and large scales. For the 2021 IJCAI paper, this means that
        the capacity of all clusters in the arena is 3 times the number of
        robots in the arena, assuming a constant density of 1% across all arena
        sizes. The current powerlaw distributor implementation in COSM results
        in clusters only being able to be filled about halfway, so the effective
        capacity is actually only ~1.5 times the # robots in the arena. See
        COSM#145,COSM#146.

        Now setting:

        - Min :math:`2^k`  where :math:`k=\lceil{X^{1/4}}\rceil + 1`
        - Max :math:`2^k` where :math:`k=\lceil{X^{1/3}}\rceil + 1`
        - # clusters to :math:`\lceil{X^{3/5}}\rceil`

        where :math:`X` is the arena dimension (assumed to be square).

        """
        changes = super().gen_attr_changelist()
        pwr_min = math.ceil(math.pow(self.arena_dim.xsize(), 0.25)) + 1
        pwr_max = math.ceil(math.pow(self.arena_dim.xsize(), 1.0 / 3.0)) + 1
        n_clusters = math.ceil(math.pow(self.arena_dim.xsize(), 0.8))
        self.logger.debug("pwr_min=%s,pwr_max=%s,n_clusters=%s",
                          pwr_min, pwr_max, n_clusters)

        for c in changes:
            c |= xml.AttrChangeSet(xml.AttrChange(".//arena_map/blocks/distribution/powerlaw",
                                                  "pwr_min",
                                                  "{0}".format(pwr_min)),
                                   xml.AttrChange(".//arena_map/blocks/distribution/powerlaw",
                                                  "pwr_max",
                                                  "{0}".format(pwr_max)),
                                   xml.AttrChange(".//arena_map/blocks/distribution/powerlaw",
                                                  "n_clusters",
                                                  "{0}".format(n_clusters)))
        return changes


class Random(BaseDistribution):
    def __init__(self) -> None:
        super().__init__("random")


__api__ = [
    'BaseDistribution',
    'SingleSource',
    'DualSource',
    'QuadSource',
    'PowerLaw',
    'Random'


]
