# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import math
import typing as tp

# 3rd party packages
import implements
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.utils import ArenaExtent
from sierra.core.experiment import xml

# Project packages
from titerra.variables import batch_criteria as bc


@implements.implements(bc.IConcreteBatchCriteria)
class Convergence():
    """Maps a list of desired arena dimensions to a list of sets of XML changes to
    set up convergence XML configuration for the TITARRA project. This includes
    setup for the following C++ TITARRA components:

    - cpp:class:`~cosm::convergence::convergence_calculator`.

    Attributes:
        extents: List of :class:`~sierra.core.utils.ArenaExtent` arena dimensions.
        attr_changes: List of sets of XML changes to apply to a template input file.

    """

    def __init__(self, extents: tp.List[ArenaExtent]) -> None:
        self.extents = extents
        self.attr_changes = []  # type: tp.List

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        """
        Generate list of sets of changes necessary to make to the input file to correctly set up the
        simulation with the specified area size/shape.
        """
        if not self.attr_changes:
            self.attr_changes = [set([(".//convergence/positional_entropy",
                                       "horizon",
                                       "0:{0:.9f}".format(math.sqrt(extent.xsize() ** 2 + extent.ysize() ** 2))),
                                      (".//convergence/positional_entropy",
                                       "horizon_delta",
                                       "{0:.9f}".format(math.sqrt(extent.xsize() ** 2 + extent.ysize() ** 2) / 10.0)),
                                      ])
                                 for extent in self.extents]

        return self.attr_changes

    def gen_files(self) -> None:
        pass


__api__ = [
    'Convergence',
]
