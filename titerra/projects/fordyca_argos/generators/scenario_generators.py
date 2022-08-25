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

# Core packages
import typing as tp

# 3rd party packages
from sierra.core import utils as scutils
from sierra.core.experiment import definition

# Project packages
import titerra.projects.common.generators.argos as tiargos
from titerra.projects.fordyca_argos.variables import dynamic_cache, static_cache


class SSGenerator(tiargos.ForagingSSGenerator):
    """
    FORDYCA extensions to the single source foraging generator
    :class:`~common.generators.scenario_generator.SSGenerator`.

    This includes:

    - Static caches
    - Dynamic caches

    """

    def __init__(self, *args, **kwargs):
        tiargos.ForagingSSGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate physics engine definitions. Cannot be in common, because not
        # shared between FORDYCA and PRISM.
        self.generate_physics(exp_def,
                              self.cmdopts,
                              self.cmdopts['physics_engine_type2D'],
                              self.cmdopts['physics_n_engines'],
                              [self.spec.arena_dim])

        if "d1" in self.controller:
            generate_static_cache(exp_def, self.spec.arena_dim, self.cmdopts)
        if "d2" in self.controller:
            generate_dynamic_cache(exp_def, self.spec.arena_dim)

        return exp_def


class DSGenerator(tiargos.ForagingDSGenerator):
    """
    FORDYCA extensions to the single source foraging generator
    :class:`~common.generators.single_source.DSGenerator`.

    This includes:

    - Static caches
    - Dynamic caches

    """

    def __init__(self, *args, **kwargs):
        tiargos.ForagingDSGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate physics engine definitions. Cannot be in common, because not
        # shared between FORDYCA and PRISM.
        self.generate_physics(exp_def,
                              self.cmdopts,
                              self.cmdopts['physics_engine_type2D'],
                              self.cmdopts['physics_n_engines'],
                              [self.spec.arena_dim])

        if "d1" in self.controller:
            generate_static_cache(exp_def, self.spec.arena_dim, self.cmdopts)
        if "d2" in self.controller:
            generate_dynamic_cache(exp_def, self.spec.arena_dim)

        return exp_def


class QSGenerator(tiargos.ForagingQSGenerator):
    """
    FORDYCA extensions to the single source foraging generator
    :class:`~common.generators.scenario_generator.QSGenerator`.

    This includes:

    - Static caches
    - Dynamic caches

    """

    def __init__(self, *args, **kwargs):
        tiargos.ForagingQSGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate physics engine definitions. Cannot be in common, because not
        # shared between FORDYCA and PRISM.
        self.generate_physics(exp_def,
                              self.cmdopts,
                              self.cmdopts['physics_engine_type2D'],
                              self.cmdopts['physics_n_engines'],
                              [self.spec.arena_dim])

        if "d1" in self.controller:
            generate_static_cache(exp_def, self.spec.arena_dim, self.cmdopts)
        if "d2" in self.controller:
            generate_dynamic_cache(exp_def, self.spec.arena_dim)

        return exp_def


class RNGenerator(tiargos.ForagingRNGenerator):
    """
    FORDYCA extensions to the single source foraging generator
    :class:`~common.generators.scenario_generator.RNGenerator`.

    This includes:

    - Static caches
    - Dynamic caches

    """

    def __init__(self, *args, **kwargs):
        tiargos.ForagingRNGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate physics engine definitions. Cannot be in common, because not
        # shared between FORDYCA and PRISM
        self.generate_physics(exp_def,
                              self.cmdopts,
                              self.cmdopts['physics_engine_type2D'],
                              self.cmdopts['physics_n_engines'],
                              [self.spec.arena_dim])

        if "d1" in self.controller:
            generate_static_cache(exp_def, self.spec.arena_dim, self.cmdopts)
        if "d2" in self.controller:
            generate_dynamic_cache(exp_def, self.spec.arena_dim)

        return exp_def


class PLGenerator(tiargos.ForagingPLGenerator):
    """
    FORDYCA extensions to the single source foraging generator
    :class:`~common.generators.scenario_generator.PLGenerator`.

    This includes:

    - Static caches
    - Dynamic caches

    """

    def __init__(self, *args, **kwargs):
        tiargos.ForagingPLGenerator.__init__(self, *args, **kwargs)

    def generate(self):

        exp_def = super().generate()

        # Generate physics engine definitions. Cannot be in common, because not
        # shared between FORDYCA and PRISM.
        self.generate_physics(exp_def,
                              self.cmdopts,
                              self.cmdopts['physics_engine_type2D'],
                              self.cmdopts['physics_n_engines'],
                              [self.spec.arena_dim])

        if "d1" in self.controller:
            generate_static_cache(exp_def, self.spec.arena_dim, self.cmdopts)
        if "d2" in self.controller:
            generate_dynamic_cache(exp_def, self.spec.arena_dim)

        return exp_def


def generate_dynamic_cache(exp_def: definition.XMLExpDef, extent: scutils.ArenaExtent):
    """
    Generate XML changes for dynamic cache usage (depth2 simulations only).

    Does not write generated changes to the simulation definition pickle file.
    """
    cache = dynamic_cache.DynamicCache([extent])
    _, adds, chgs = scutils.apply_to_expdef(cache, exp_def)


def generate_static_cache(exp_def: definition.XMLExpDef,
                          extent: scutils.ArenaExtent,
                          cmdopts: tp.Dict[str, str]):
    """
    Generate XML changes for static cache usage (depth1 simulations only).

    Does not write generated changes to the simulation definition pickle file.
    """

    # If they specified how many blocks to use for static cache respawn, use that.
    # Otherwise use the floor of 2.
    if cmdopts['static_cache_blocks'] is None:
        cache = static_cache.StaticCache([2], [extent])
    else:
        cache = static_cache.StaticCache([cmdopts['static_cache_blocks']],
                                         [extent])

    _, adds, chgs = scutils.apply_to_expdef(cache, exp_def)


def gen_generator_name(scenario_name: str) -> str:
    return tiargos.gen_generator_name(scenario_name)
