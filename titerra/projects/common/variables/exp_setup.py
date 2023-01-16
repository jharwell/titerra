# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

"""
See :ref:`ln-var-expsetup` for documentation and usage.
"""

# Core packages
import typing as tp

# 3rd party packages
import implements
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.experiment import xml
from sierra.core.variables import exp_setup as exp
from sierra.core import config

# Project packages


kND_DATA_DIVISOR_DEFAULT = 10
"""
Default divisor for the output interval for each .csv of two- or
three-dimensional data, as compared to the output interval for 1D data.

"""


@implements.implements(IBaseVariable)
class TimeSetup():
    def __init__(self, n_secs_per_run: int, metric_interval: int) -> None:
        self.n_secs_per_run = n_secs_per_run
        self.metric_interval = metric_interval
        self.attr_changes = []

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        if not self.attr_changes:
            self.attr_changes = [xml.AttrChangeSet(
                # 2022/4/7: Network metrics are streamed to the master every
                # timestep for simplicity; this may be revisited in the future
                # if needed. It seemed better to make this change here than to
                # have the C++ code ignore what is set here and always do 1.
                xml.AttrChange(".//output/metrics/sinks/network/stream",
                               "output_interval",
                               "{0}".format(1)),
                xml.AttrChange(".//output/metrics/sinks/file/append",
                               "output_interval",
                               "{0}".format(self.metric_interval)),
                xml.AttrChange(".//output/metrics/sinks/file/truncate",
                               "output_interval",
                               "{0}".format(self.metric_interval)),
                xml.AttrChange(".//output/metrics/sinks/file/create",
                               "output_interval",
                               "{0}".format(max(1, self.metric_interval / kND_DATA_DIVISOR_DEFAULT))))]

        return self.attr_changes

    def gen_tag_rmlist(self) -> tp.List[xml.TagRmList]:
        return []

    def gen_tag_addlist(self) -> tp.List[xml.TagAddList]:
        return []

    def gen_files(self) -> None:
        pass


class Parser(exp.Parser):
    pass


def factory(arg: str) -> TimeSetup:
    """
    Factory to create :class:`TimeSetup` derived classes from the command line definition.

    Parameters:
       arg: The value of ``--time-setup``
    """
    parser = Parser({'n_secs_per_run': config.kARGoS['n_secs_per_run'],
                     'n_ticks_per_sec': config.kARGoS['n_ticks_per_sec'],
                     'n_datapoints': config.kExperimentalRunData['n_datapoints_1D']})
    attr = parser(arg)

    def __init__(self) -> None:
        TimeSetup.__init__(self,
                           attr["n_secs_per_run"],
                           int(attr["n_secs_per_run"] * attr['n_ticks_per_sec'] / attr["n_datapoints"]))

    return type(attr['pretty_name'],  # type: ignore
                (TimeSetup,),
                {"__init__": __init__})


__api__ = [
    'kND_DATA_DIVISOR_DEFAULT',
    'TimeSetup',
]
