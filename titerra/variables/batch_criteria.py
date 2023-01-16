# Copyright 2022 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
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
