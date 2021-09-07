# Copyright 2018 London Lowmanstone, John Harwell, All rights reserved.
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
Extensions to the :class:`~sierra.core.generators.ExpCreator` and
:class:`sierra.core.generators.SimDefUniqueGenerator` for the TITAN project.
"""

# Core packages

# 3rd party packages

# Project packages
import sierra.core.generators.exp_generators as exp_generators
from sierra.core.xml_luigi import XMLLuigi
import sierra.core.config as config


class SimDefUniqueGenerator(exp_generators.SimDefUniqueGenerator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def generate(self, exp_def: XMLLuigi, random_seeds):
        super().generate(exp_def, random_seeds)
        self._generate_output(exp_def)

    def _generate_output(self, exp_def: XMLLuigi):
        """
        Generates XML changes to setup unique output directories for TITAN simulations.
        """
        exp_def.attr_change(".//controllers/*/params/output",
                            "output_leaf",
                            self.sim_output_dir)

        exp_def.attr_change(".//controllers/*/params/output",
                            "output_parent",
                            self.exp_output_root)
        exp_def.attr_change(".//loop_functions/output",
                            "output_leaf",
                            self.sim_output_dir)
        exp_def.attr_change(".//loop_functions/output",
                            "output_parent",
                            self.exp_output_root)


__api__ = [
    'SimDefUniqueGenerator',
]
