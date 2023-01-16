# Copyright 2020 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

"""
Common functionality/configuration for all PRISM scenarios.
"""
# Core packages
import logging

# 3rd party packages
from sierra.core.experiment import definition
from sierra.core import utils as scutils

# Project packages
from titerra.platform.argos.variables import block_distribution, arena
import titerra.projects.prism.variables.ct_set as ctset
from titerra.projects.common.generators.argos import ForagingScenarioGenerator


class ConstructionScenarioGenerator(ForagingScenarioGenerator):
    def __init__(self, *args, **kwargs) -> None:
        ForagingScenarioGenerator.__init__(self, *args, **kwargs)

    def generate(self):
        exp_def = super().generate()

        # Generate and apply construction targets definitions
        self.generate_construct_targets(exp_def)

        return exp_def

    def generate_mixed_physics(self,
                               exp_def: definition.XMLExpDef,
                               block_dist: str) -> None:
        """Generate mixed 2D/3D physics engine definitions for the arena, according to
        the specified block distribution configuration, maximum structure
        height, and # physics engines.

        """
        zmax = 0
        target_set = ctset.factory(self.cmdopts['ct_specs'],
                                   self.cmdopts['ct_orientations'],
                                   self.spec.exp_input_root)

        for t in target_set.targets:
            zmax = max(zmax, t.extent.zsize())

        if self.cmdopts['physics_n_engines'] == 1:
            logging.warning(
                "Cannot mix 2D/3D engines with only 1 engine: using 1 3D engine")
            n_engines_2D = 0
            n_engines_3D = 1
            extents_3D = [self.spec.arena_dim]
            extents_2D = [None]

        else:
            n_engines_2D = int(self.cmdopts['physics_n_engines'] / 2.0)
            n_engines_3D = int(self.cmdopts['physics_n_engines'] / 2.0)

            if block_dist == 'single_source':
                # Construction area needs 3D physics, 2D OK for everything
                # else. Allocating the first 25% of the arena in X is more than
                # is needed, but it is a reasonable first attempt at mixing
                # 2D/3D engines.
                extents_3D = [scutils.ArenaExtent(dims=(self.spec.arena_dim.xsize() * 0.25,
                                                        self.spec.arena_dim.ysize(),
                                                        zmax))]
                extents_2D = [scutils.ArenaExtent(dims=(self.spec.arena_dim.xsize() * 0.75,
                                                        self.spec.arena_dim.ysize(),
                                                        zmax),
                                                  offset=(self.spec.arena_dim.xsize() * 0.25, 0, 0))]
            elif block_dist == 'dual_source':
                # Construction area needs 3D physics, 2D OK for everything
                # else. Allocating the middle 26% of the arena in X is more than
                # is needed, but it is a reasonable first attempt at mixing
                # 2D/3D engines. 26% rather than 25% because the 3D portion is
                # in the middle of the arena, with 74 / 2 = 37.5 % of the arena
                # with 2D physics on either side.
                extents_3D = [scutils.ArenaExtent(dims=(self.spec.xsize() * 0.26,
                                                        self.spec.ysize(),
                                                        zmax),
                                                  offset=(self.spec.xsize() * 0.37,
                                                          0.0,
                                                          0.0))]

                extent_2D1 = scutils.ArenaExtent(dims=(self.spec.xsize() * 0.37,
                                                       self.spec.ysize(),
                                                       zmax))
                extent_2D2 = scutils.ArenaExtent(dims=(self.spec.xsize() * 0.37,
                                                       self.spec.ysize(),
                                                       zmax),
                                                 offset=(self.spec.xsize() * 0.63, 0.0, 0.0))
                extents_2D = [extent_2D1, extent_2D2]
            else:
                # The square arenas with the nest in the center will be trickier
                # to divide up so that the 2D/3D split is as efficient as
                # possible, so punting for now.
                raise NotImplementedError

        self.generate_physics(exp_def,
                              self.cmdopts,
                              self.cmdopts['physics_engine_type3D'],
                              n_engines_3D,
                              extents_3D,
                              True)
        self.generate_physics(exp_def,
                              self.cmdopts,
                              self.cmdopts['physics_engine_type2D'],
                              n_engines_2D,
                              extents_2D,
                              False)

    def generate_construct_targets(self,
                                   exp_def: definition.XMLExpDef) -> None:
        target_set = ctset.factory(self.cmdopts['ct_specs'],
                                   self.cmdopts['ct_orientations'],
                                   self.spec.exp_input_root)
        scutils.apply_to_expdef(target_set, exp_def)

        # Generate .graphml files
        target_set.gen_files()
