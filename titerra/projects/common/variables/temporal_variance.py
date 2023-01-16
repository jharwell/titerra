# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
"""
Classes for the temporal variance batch criteria. See :ref:`ln-bc-tv` for usage
documentation.
"""

# Core packages
import math
import typing as tp
import logging
import pathlib

# 3rd party packages
import implements
from sierra.plugins.platform.argos.variables.population_size import PopulationSize
from sierra.core.experiment import xml
from sierra.core import types

# Project packages
from titerra.projects.common.perf_measures import vcs
from titerra.projects.common.variables.temporal_variance_parser import TemporalVarianceParser
import titerra.variables.batch_criteria as bc


@implements.implements(bc.IConcreteBatchCriteria)
@implements.implements(bc.IPMQueryableBatchCriteria)
class TemporalVariance(bc.UnivarBatchCriteria):
    """
    A univariate range specifiying the set of temporal variances (and possibly
    swarm size) to use to define the batched experiment. This class is a base
    class which should (almost) never be used on its own. Instead, the
    ``factory()`` function should be used to dynamically create derived classes
    expressing the user's desired variance set.

    Attributes:

        variances: List of tuples specifying the waveform characteristics for
                   each type of applied variance. Cardinality of each tuple is
                   3, and defined as follows:

                   - xml parent path: The path to the parent element in the XML
                     tree.

                   - [type, frequency, amplitude, offset, phase]: Waveform
                     parameters.

                   - value: Waveform specific parameters (optional, will be None
                            if not used for the selected variance).

    """

    def __init__(self,
                 cli_arg: str,
                 main_config: types.YAMLDict,
                 batch_input_root: pathlib.Path,
                 variance_type: str,
                 variances: tp.List[tp.Tuple[str,
                                             str,
                                             float,
                                             tp.Any,
                                             float,
                                             float]],
                 population: int) -> None:
        bc.UnivarBatchCriteria.__init__(
            self, cli_arg, main_config, batch_input_root)

        self.variance_type = variance_type
        self.variances = variances
        self.population = population
        self.attr_changes = []  # type: tp.List[xml.AttrChangeSet]

    def gen_attr_changelist(self) -> tp.List[xml.AttrChangeSet]:
        """
        Generate a list of sets of changes necessary to make to the input file to correctly set up
        the simulation with the specified temporal variances.
        """
        if not self.attr_changes:
            self.attr_changes = [
                xml.AttrChangeSet(xml.AttrChange("{0}/waveform".format(v[0]),
                                                 "type",
                                                 str(v[1])),
                                  xml.AttrChange("{0}/waveform".format(v[0]),
                                                 "frequency",
                                                 str(v[2])),
                                  xml.AttrChange("{0}/waveform".format(v[0]),
                                                 "amplitude",
                                                 str(v[3])),
                                  xml.AttrChange("{0}/waveform".format(v[0]),
                                                 "offset",
                                                 str(v[4])),
                                  xml.AttrChange("{0}/waveform".format(v[0]),
                                                 "phase",
                                                 str(v[5]))) for v in self.variances]

            # Swarm size is optional. It can be (1) controlled via this
            # variable, (2) controlled by another variable in a bivariate batch
            # criteria, (3) not controlled at all. For (2), (3), the swarm size
            # can be None.
            if self.population is not None:
                size_chgs = PopulationSize(self.cli_arg,
                                           self.main_config,
                                           self.batch_input_root,
                                           [self.population]).gen_attr_changelist()[0]
                for exp_chgs in self.attr_changes:
                    exp_chgs |= size_chgs

        return self.attr_changes

    def calc_reactivity_scaling(self, ideal_var: float, expx_var: float) -> float:
        # For motion throttling while robots carry blocks, the variances are
        # always percents between 0 and 1.
        if self.variance_type in ['BC', 'M']:
            if expx_var > ideal_var:
                return 1.0 - abs(expx_var - ideal_var)
            else:  # expx_var <= ideal_var:
                return 1.0 + abs(expx_var - ideal_var)
        elif self.variance_type == 'BM':
            return ideal_var / expx_var

        else:
            return 0.0

    def graph_xticks(self,
                     cmdopts: types.Cmdopts,
                     exp_names: tp.Optional[tp.List[str]] = None) -> tp.List[float]:

        # If exp_names is passed, then we have been handed a subset of the total
        # # of directories in the batch exp root, and so n_exp() will return
        # more experiments than we actually have. This behavior is needed to
        # correct extract x/y values for bivar experiments.
        if exp_names is None:
            exp_names = self.gen_exp_names(cmdopts)

        m = len(exp_names)

        return [round(vcs.EnvironmentalCS(self.main_config, cmdopts, x)(self, exp_names), 4)
                for x in range(0, m)]

    def graph_xticklabels(self,
                          cmdopts: types.Cmdopts,
                          exp_names: tp.Optional[tp.List[str]] = None) -> tp.List[str]:
        return list(map(str, self.graph_xticks(cmdopts, exp_names)))

    def graph_xlabel(self, cmdopts: types.Cmdopts) -> str:
        return vcs.method_xlabel(cmdopts["envc_cs_method"])

    def gen_exp_names(self, cmdopts: types.Cmdopts) -> tp.List[str]:
        return ['exp' + str(x) for x in range(0, len(self.gen_attr_changelist()))]

    def pm_query(self, pm: str) -> bool:
        return pm in ['raw', 'flexibility']

    def inter_exp_graphs_exclude_exp0(self) -> bool:
        return True


class VariancesGenerator():
    def __init__(self, main_config: types.YAMLDict, attr: types.CLIArgSpec):
        self.main_config = main_config
        self.attr = attr

    def __call__(self) -> tp.List[tp.Tuple[str,
                                           str,
                                           float,
                                           tp.Any,
                                           float,
                                           float]]:

        amps_key = self.attr['variance_type'] + '_amp'
        try:
            amps = self.main_config['sierra']['perf']['flexibility'][amps_key]
            hzs = self.main_config['sierra']['perf']['flexibility']['hz']
        except KeyError:
            msg = "'hz' or '{0}' not found in 'flexibility' section of main config file for project".format(
                amps_key)
            logging.fatal(msg)
            raise

        variances = [(self.attr["xml_parent_path"],
                      "Constant",
                      0.0,
                      amps[0],
                      0.0,
                      0.0)]
        if any(v == self.attr["waveform_type"] for v in ["Sine", "Square", "Sawtooth"]):

            variances.extend([(self.attr["xml_parent_path"],
                               self.attr["waveform_type"],
                               hz,
                               amp,
                               amp,
                               0.0) for hz in hzs for amp in amps[1:]])

        elif self.attr["waveform_type"] == "StepD":
            variances.extend([(self.attr["xml_parent_path"],
                               "Square",
                               1 / (2 * self.attr["waveform_param"]),
                               amp,
                               0.0,
                               0.0) for amp in amps[1:]])

        if self.attr["waveform_type"] == "StepU":
            variances.extend([(self.attr["xml_parent_path"],
                               "Square",
                               1 / (2 * self.attr["waveform_param"]),
                               amp,
                               amp,
                               math.pi) for amp in amps[1:]])
        return variances


def factory(cli_arg: str,
            main_config: types.YAMLDict,
            cmdopts: types.Cmdopts,
            **kwargs) -> TemporalVariance:
    """
    Factory to create :class:`TemporalVariance` derived classes from the command
    line definition of batch criteria.

    """
    attr = TemporalVarianceParser()(cli_arg)
    variances = VariancesGenerator(main_config, attr)()

    def __init__(self: TemporalVariance) -> None:
        TemporalVariance.__init__(self,
                                  cli_arg,
                                  main_config,
                                  cmdopts['batch_input_root'],
                                  attr['variance_type'],
                                  variances,
                                  attr.get("population", None))

    return type(cli_arg,
                (TemporalVariance,),
                {"__init__": __init__})   # type: ignore


__api__ = [
    'TemporalVariance'
]
