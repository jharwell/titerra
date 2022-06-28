# Copyright 2022 John Harwell, All rights reserved.
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
"""
Extensions to SIERRA batch criteria classes for the TITAN project.
"""

# Core packages

# 3rd party packages
import implements

from sierra.core.variables import batch_criteria as bc
from sierra.core.variables.batch_criteria import IBivarBatchCriteria, IConcreteBatchCriteria, IBatchCriteriaType, BatchCriteria, UnivarBatchCriteria, factory


class IPMQueryableBatchCriteria(implements.Interface):
    """Mixin interface for batch criteria which can be queried during stage
    4 to generate performance measures.
    """

    def pm_query(self, pm: str) -> bool:
        """
        Arguments:
            pm: A possible performance measure to generate from the results of
                the batch experiment defined by this object.

        Returns:
            `True` if the specified pm should be generated for the current
            object, and `False` otherwise.
        """
        raise NotImplementedError


@implements.implements(IBivarBatchCriteria)
@implements.implements(IBatchCriteriaType)
@implements.implements(IPMQueryableBatchCriteria)
class BivarBatchCriteria(bc.BivarBatchCriteria):
    """
    Combination of the definition of two separate batch criteria.
    """

    def __init__(self, *args, **kwargs) -> None:

        bc.BivarBatchCriteria.__init__(self, *args, **kwargs)

    def pm_query(self, pm: str) -> bool:
        return self.criteria1.pm_query(pm) or self.criteria2.pm_query(pm)


__api__ = [
    'IConcreteBatchCriteria',
    'IPMQueryableBatchCriteria',
    'BivarBatchCriteria',
]
