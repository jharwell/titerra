# Copyright 2021 John Harwell, All rights reserved.
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

"""Extensions to
:class:`~sierra.plugins.platform.argos.platform_generators.PlatformExpDefGenerator`
common to all TITAN scenarios which use ARGoS.

"""
# Core packages
import re

# 3rd party packages
from sierra.core.utils import ArenaExtent
from sierra.core.xml import XMLLuigi
from sierra.plugins.platform.argos.generators.platform_generators import PlatformExpDefGenerator
from sierra.plugins.platform.argos.generators.platform_generators import PlatformExpRunDefUniqueGenerator
import sierra.core.utils as scutils

# Project packages
from titerra.platform.argos.variables import block_distribution, arena, block_quantity
from titerra.platform.argos.variables.nest import Nest
from titerra.projects.common.generators import utils as tiutils
from titerra.projects.common.variables import exp_setup


class BaseScenarioGenerator(PlatformExpDefGenerator):
    def __init__(self, *args, **kwargs) -> None:
        PlatformExpDefGenerator.__init__(self, *args, **kwargs)

    def generate_convergence(self, exp_def: XMLLuigi):
        """
        Generate XML changes for calculating swarm convergence.

        Does not write generated changes to the simulation definition pickle
        file.
        """
        # This whole tree can be missing and that's fine
        if exp_def.has_tag(".//loop_functions/convergence"):
            exp_def.attr_change(".//loop_functions/convergence",
                                "n_threads",
                                str(self.cmdopts["physics_n_engines"]))

    def generate_arena_map(self,
                           exp_def: XMLLuigi,
                           the_arena: arena.RectangularArena) -> None:
        """
        Generate XML changes for the specified arena map configuration.

        Writes generated changes to the simulation definition pickle file.
        """
        _, adds, chgs = scutils.apply_to_expdef(the_arena, exp_def)
        scutils.pickle_modifications(adds, chgs, self.spec.exp_def_fpath)

    @staticmethod
    def generate_block_dist(exp_def: XMLLuigi,
                            block_dist: block_distribution.BaseDistribution) -> None:
        """
        Generate XML changes for the specified block distribution.

        Does not write generated changes to the simulation definition pickle
        file.
        """
        scutils.apply_to_expdef(block_dist, exp_def)

    def generate_block_count(self, exp_def: XMLLuigi) -> None:
        """
        Generates XML changes for # blocks in the simulation. If specified on
        the cmdline, that quantity is used (split evenly between ramp and cube
        blocks).

        Writes generated changes to the simulation definition pickle file.

        """
        if self.cmdopts['n_blocks'] is not None:
            n_blocks = self.cmdopts['n_blocks']
            chgs1 = block_quantity.BlockQuantity.gen_attr_changelist_from_list([n_blocks / 2],
                                                                               'cube')[0]
            chgs2 = block_quantity.BlockQuantity.gen_attr_changelist_from_list([n_blocks / 2],
                                                                               'ramp')[0]
        else:
            # This may have already been set by the batch criteria, but we can't
            # know for sure, and we need block quantity definitions to always be
            # written to the pickle file for later retrieval.
            n_blocks1 = int(exp_def.attr_get('.//manifest', 'n_cube'))
            n_blocks2 = int(exp_def.attr_get('.//manifest', 'n_ramp'))

            chgs1 = block_quantity.BlockQuantity.gen_attr_changelist_from_list([n_blocks1],
                                                                               'cube')[0]
            chgs2 = block_quantity.BlockQuantity.gen_attr_changelist_from_list([n_blocks2],
                                                                               'ramp')[0]

        chgs = chgs1 | chgs2
        for chg in chgs:
            exp_def.attr_change(chg.path, chg.attr, chg.value)

        chgs.pickle(self.spec.exp_def_fpath)


class ForagingScenarioGenerator(BaseScenarioGenerator):
    def __init__(self, *args, **kwargs) -> None:
        BaseScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self) -> XMLLuigi:
        exp_def = super().generate()

        # Generate time definitions for TITAN
        tiutils.generate_time(exp_def, self.cmdopts, self.spec)

        # Generate and apply convergence definitions
        self.generate_convergence(exp_def)

        # Generate and apply # blocks definitions
        self.generate_block_count(exp_def)

        return exp_def


class ForagingSSGenerator(ForagingScenarioGenerator):
    """
    Generates XML changes for single source foraging.

    This includes:

    - Rectangular 2x1 arena
    - Single source block distribution
    - One nest
    """

    def __init__(self, *args, **kwargs) -> None:
        ForagingScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):
        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == 2 * self.spec.arena_dim.ysize(),\
            "SS distribution requires a 2x1 arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                             self.spec.arena_dim.ysize())

        arena_map = arena.RectangularArenaTwoByOne(x_range=[self.spec.arena_dim.xsize()],
                                                   y_range=[
                                                   self.spec.arena_dim.ysize()],
                                                   z=self.spec.arena_dim.zsize(),
                                                   dist_type='SS',
                                                   gen_nests=True)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(
            exp_def, block_distribution.SingleSourceDistribution())

        return exp_def


class ForagingDSGenerator(ForagingScenarioGenerator):
    """
    Generates XML changes for dual source foraging.

    This includes:

    - Rectangular 2x1 arena
    - Dual source block distribution
    - One nest
    """

    def __init__(self, *args, **kwargs) -> None:
        ForagingScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):
        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == 2 * self.spec.arena_dim.ysize(),\
            "DS distribution requires a 2x1 arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                             self.spec.arena_dim.ysize())

        arena_map = arena.RectangularArenaTwoByOne(x_range=[self.spec.arena_dim.xsize()],
                                                   y_range=[
                                                       self.spec.arena_dim.ysize()],
                                                   z=self.spec.arena_dim.zsize(),
                                                   dist_type='DS',
                                                   gen_nests=True)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(
            exp_def, block_distribution.DualSourceDistribution())

        return exp_def


class ForagingQSGenerator(ForagingScenarioGenerator):
    """
    Generates XML changes for quad source foraging.

    This includes:

    - Square arena
    - Quad source block distribution
    - One nest
    """

    def __init__(self, *args, **kwargs) -> None:
        ForagingScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):
        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == self.spec.arena_dim.ysize(),\
            "QS distribution requires a square arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                self.spec.arena_dim.ysize())

        arena_map = arena.SquareArena(sqrange=[self.spec.arena_dim.xsize()],
                                      z=self.spec.arena_dim.zsize(),
                                      dist_type='QS',
                                      gen_nests=True)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        source = block_distribution.QuadSourceDistribution()
        self.generate_block_dist(exp_def, source)

        return exp_def


class ForagingRNGenerator(ForagingScenarioGenerator):
    """
    Generates XML changes for random foraging.

    This includes:

    - Square arena
    - Random block distribution
    - One nest
    """

    def __init__(self, *args, **kwargs) -> None:
        ForagingScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):
        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == self.spec.arena_dim.ysize(),\
            "RN distribution requires a square arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                self.spec.arena_dim.ysize())
        arena_map = arena.SquareArena(sqrange=[self.spec.arena_dim.xsize()],
                                      z=self.spec.arena_dim.zsize(),
                                      dist_type='RN',
                                      gen_nests=True)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(
            exp_def, block_distribution.RandomDistribution())

        return exp_def


class ForagingPLGenerator(ForagingScenarioGenerator):
    """
    Generates XML changes for powerlaw source foraging.

    This includes:

    - Square arena
    - Powerlaw block distribution
    - One nest
    """

    def __init__(self, *args, **kwargs) -> None:
        ForagingScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):
        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == self.spec.arena_dim.ysize(),\
            "PL distribution requires a square arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                self.spec.arena_dim.ysize())

        arena_map = arena.SquareArena(sqrange=[self.spec.arena_dim.xsize()],
                                      z=self.spec.arena_dim.zsize(),
                                      dist_type='PL',
                                      gen_nests=True)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(exp_def,
                                 block_distribution.PowerLawDistribution(self.spec.arena_dim))

        return exp_def


class ExpRunDefUniqueGenerator(PlatformExpRunDefUniqueGenerator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def generate(self, exp_def: XMLLuigi):
        super().generate(exp_def)

        tiutils.generate_random(exp_def,
                                ".//controllers/*/params",
                                self.random_seed)

        tiutils.generate_output(exp_def,
                                ".//controllers/*/params",
                                self.run_output_path)


def gen_generator_name(scenario_name: str) -> str:
    res = re.search('[SDQPR][SSSLN]', scenario_name)
    assert res is not None, "Bad block distribution in {0}".format(
        scenario_name)
    abbrev = res.group(0)

    return abbrev + 'Generator'


__api__ = [
    'BaseScenarioGenerator',
    'ForagingScenarioGenerator',
    'ForagingSSGenerator',
    'ForagingDSGenerator',
    'ForagingQSGenerator',
    'ForagingPLGenerator',
    'ForagingRNGenerator',
]
