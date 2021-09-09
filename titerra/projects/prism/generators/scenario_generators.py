# Copyright 2020 John Harwell, All rights reserved.
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

# Core packages

# 3rd party packages

# Project packages
import titerra.projects.titan.generators.common as ticom
from titerra.projects.titan.variables import arena, block_distribution
import titerra.projects.prism.generators.common as sicom


class SSGenerator(sicom.ConstructionScenarioGenerator):
    """
    PRISM extensions to the base scenario generator
    :class:`~titan.generators.scenario_generator.ConstrutionScenarioGenerator` for single source
    construction scenarios.

    This includes:

    - Ramp construction targets
    - Rectprism construction targets

    """

    def __init__(self, *args, **kwargs):
        sicom.ConstructionScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == 2 * self.spec.arena_dim.ysize(),\
            "FATAL: SS distribution requires a 2x1 arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                    self.spec.arena_dim.ysize())

        arena_map = arena.RectangularArenaTwoByOne(x_range=[self.spec.arena_dim.xsize()],
                                                   y_range=[
                                                   self.spec.arena_dim.ysize()],
                                                   z=self.spec.arena_dim.zsize(),
                                                   dist_type='SS',
                                                   gen_nests=False)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(exp_def, block_distribution.SingleSourceDistribution())

        # Mixed 2D/3D physics
        self.generate_mixed_physics(exp_def, 'single_source')

        return exp_def


class DSGenerator(sicom.ConstructionScenarioGenerator):
    """
    PRISM extensions to the base scenario generator
    :class:`~titan.generators.scenario_generator.ConstrutionScenarioGenerator` for dual source
    construction scenarios.

    This includes:

    - Ramp construction targets
    - Rectprism construction targets

    """

    def __init__(self, *args, **kwargs):
        sicom.ConstructionScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == 2 * self.spec.arena_dim.ysize(),\
            "FATAL: DS distribution requires a 2x1 arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                    self.spec.arena_dim.ysize())

        arena_map = arena.RectangularArenaTwoByOne(x_range=[self.spec.arena_dim.xsize()],
                                                   y_range=[
                                                   self.spec.arena_dim.ysize()],
                                                   z=self.spec.arena_dim.zsize(),
                                                   dist_type='DS',
                                                   gen_nests=False)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(exp_def, block_distribution.DualSourceDistribution())

        # Mixed 2D/3D physics
        self.generate_mixed_physics(exp_def, 'dual_source')

        return exp_def


class QSGenerator(sicom.ConstructionScenarioGenerator):
    """
    PRISM extensions to the base scenario generator
    :class:`~titan.generators.scenario_generator.ConstrutionScenarioGenerator` for quad source
    construction scenarios.

    This includes:

    - Ramp construction targets
    - Rectprism construction targets

    """

    def __init__(self, *args, **kwargs):
        sicom.ConstructionScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == self.spec.arena_dim.ysize(),\
            "FATAL: QS distribution requires a square arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                       self.spec.arena_dim.ysize())

        arena_map = arena.SquareArena(sqrange=[self.spec.arena_dim.xsize()],
                                      z=self.spec.arena_dim.zsize(),
                                      dist_type='QS',
                                      gen_nests=False)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(exp_def, block_distribution.QuadSourceDistribution())

        # Mixed 2D/3D physics
        self.generate_mixed_physics(exp_def, 'quad_source')

        return exp_def


class RNGenerator(sicom.ConstructionScenarioGenerator):
    """
    PRISM extensions to the base scenario generator
    :class:`~titan.generators.scenario_generator.ConstrutionScenarioGenerator` for random
    construction scenarios.

    This includes:

    - Ramp construction targets
    - Rectprism construction targets

    """

    def __init__(self, *args, **kwargs):
        sicom.ConstructionScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == self.spec.arena_dim.ysize(),\
            "FATAL: RN distribution requires a square arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                       self.spec.arena_dim.ysize())

        arena_map = arena.SquareArena(sqrange=[self.spec.arena_dim.xsize()],
                                      z=self.spec.arena_dim.zsize(),
                                      dist_type='RN',
                                      gen_nests=False)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(exp_def, block_distribution.RandomDistribution())

        # Mixed 2D/3D physics
        self.generate_mixed_physics(exp_def, 'random')

        return exp_def


class PLGenerator(sicom.ConstructionScenarioGenerator):
    """
    PRISM extensions to the base scenario generator
    :class:`~titan.generators.scenario_generator.ConstrutionScenarioGenerator` for powerlaw
    construction scenarios.

    This includes:

    - Ramp construction targets
    - Rectprism construction targets

    """

    def __init__(self, *args, **kwargs):
        sicom.ConstructionScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate arena definitions
        assert self.spec.arena_dim.xsize() == self.spec.arena_dim.ysize(),\
            "FATAL: PL distribution requires a square arena: xdim={0},ydim={1}".format(self.spec.arena_dim.xsize(),
                                                                                       self.spec.arena_dim.ysize())

        arena_map = arena.SquareArena(sqrange=[self.spec.arena_dim.xsize()],
                                      z=self.spec.arena_dim.zsize(),
                                      dist_type='PL',
                                      gen_nests=False)
        self.generate_arena_map(exp_def, arena_map)

        # Generate and apply block distribution type definitions
        self.generate_block_dist(exp_def,
                                 block_distribution.PowerLawDistribution(self.spec.arena_dim))

        # Mixed 2D/3D physics
        self.generate_mixed_physics(exp_def, 'powerlaw')

        return exp_def


def gen_generator_name(scenario_name: str) -> str:
    return ticom.gen_generator_name(scenario_name)
