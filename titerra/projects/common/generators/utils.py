# Copyright 2018 John Harwell, All rights reserved.
#
#  This file is part of SIERRA.
#
#  SIERRA is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  SIERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  SIERRA.  If not, see <http://www.gnu.org/licenses/
"""
Utils to support generator extensions for the the TITAN project.
"""

# Core packages
import os

# 3rd party packages
from sierra.core.xml import XMLLuigi
from sierra.core import types
from sierra.core.experiment.spec import ExperimentSpec
from sierra.core import utils as scutils

# Project packages
from titerra.projects.common.variables import exp_setup


def generate_time(exp_def: XMLLuigi,
                  cmdopts: types.Cmdopts,
                  spec: ExperimentSpec) -> None:
    """
    Generates XML changes for setting up time in TITAN.

    Writes generated changes to the simulation definition pickle file.
    """
    tsetup = exp_setup.factory(cmdopts['exp_setup'])()

    _, adds, chgs = scutils.apply_to_expdef(tsetup, exp_def)
    scutils.pickle_modifications(adds, chgs, spec.exp_def_fpath)


def generate_random(exp_def: XMLLuigi,
                    controller_param_xpath: str,
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


def generate_output(exp_def: XMLLuigi,
                    controller_param_xpath: str,
                    run_output_path: str):
    """
    Generates XML changes to setup unique output directories for TITAN
    simulations.
    """
    parent = os.path.abspath(os.path.join(run_output_path, '..'))
    leaf = os.path.basename(run_output_path)

    exp_def.attr_change(f"{controller_param_xpath}/output",
                        "output_leaf",
                        leaf)

    exp_def.attr_change(f"{controller_param_xpath}/output",
                        "output_parent",
                        parent)
    exp_def.attr_change(".//loop_functions/output",
                        "output_leaf",
                        leaf)
    exp_def.attr_change(".//loop_functions/output",
                        "output_parent",
                        parent)
