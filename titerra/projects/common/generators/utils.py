# Copyright 2018 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
"""
Utils to support generator extensions for the the TITAN project.
"""

# Core packages
import pathlib

# 3rd party packages
from sierra.core.experiment import definition, spec
from sierra.core import types
from sierra.core import utils as scutils

# Project packages
from titerra.projects.common.variables import exp_setup


def generate_time(exp_def: definition.XMLExpDef,
                  cmdopts: types.Cmdopts,
                  the_spec: spec.ExperimentSpec) -> None:
    """
    Generates XML changes for setting up time in TITAN.

    Writes generated changes to the simulation definition pickle file.
    """
    tsetup = exp_setup.factory(cmdopts['exp_setup'])()

    _, adds, chgs = scutils.apply_to_expdef(tsetup, exp_def)
    scutils.pickle_modifications(adds, chgs, the_spec.exp_def_fpath)


def generate_random(exp_def: definition.XMLExpDef,
                    controller_param_xpath: pathlib.Path,
                    random_seed: int) -> None:
    """
    Generates XML changes for setting up metric collection in TITAN.

    Does not write generated changes to the simulation definition pickle
    file.
    """
    if exp_def.has_tag(f'{controller_param_xpath}/rng'):
        exp_def.attr_change(f'{controller_param_xpath}/rng',
                            "seed",
                            str(random_seed))
    else:
        exp_def.tag_add(f'{controller_param_xpath}/rng',
                        {
                            "seed": str(random_seed)
                        })


def generate_output(exp_def: definition.XMLExpDef,
                    controller_param_xpath: pathlib.Path,
                    run_output_path: pathlib.Path):
    """
    Generates XML changes to setup unique output directories for TITAN
    simulations.
    """

    exp_def.attr_change(f"{controller_param_xpath}/output",
                        "output_leaf",
                        run_output_path.name)

    exp_def.attr_change(f"{controller_param_xpath}/output",
                        "output_parent",
                        str(run_output_path.parent))
    exp_def.attr_change(".//loop_functions/output",
                        "output_leaf",
                        run_output_path.name)
    exp_def.attr_change(".//loop_functions/output",
                        "output_parent",
                        str(run_output_path.parent))
