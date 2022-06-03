# Copyright 2022 Angel Sylvester, John Harwell, All rights reserved.
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
import math
import statistics
import typing as tp
import os

# 3rd party packages

# Project packages
from sierra.core import types
from sierra.core.vector import Vector3D
from sierra.core.utils import ArenaExtent
from sierra.core.experiment.spec import ExperimentSpec
from titerra.projects.fordyca_base.models import representation as rep


class Calculator:
    """
    Calculates the heterogenity of a scenario w.r.t a reference version.
    """

    def __init__(self, scenario: str) -> None:
        self.scenario = scenario

    def from_results(self,
                     main_config: types.YAMLDict,
                     cmdopts: types.Cmdopts,
                     spec: ExperimentSpec) -> float:
        # We calculate per-run, rather than using the averaged block cluster
        # results, because for power law distributions different simulations
        # have different cluster locations, which affects the distribution via
        # locality.
        #
        # For all other block distributions, we can operate on the averaged
        # results, because the position of block clusters is the same in all
        # runs.
        if 'PL' in cmdopts['scenario']:
            result_opaths = [os.path.join(cmdopts['exp_output_root'],
                                          d,
                                          main_config['sierra']['run']['run_metrics_leaf'])
                             for d in os.listdir(cmdopts['exp_output_root'])]
        else:
            result_opaths = [os.path.join(cmdopts['exp_stat_root'])]

        nest = rep.Nest(cmdopts, spec)

        heterogeneity = 0.0

        for result in result_opaths:
            clusters = rep.BlockClusterSet(cmdopts, nest, result)
            heterogeneity += self.from_clusters(clusters, spec.arena_dim, nest)

        avg_hetero = heterogeneity / len(result_opaths)

        return avg_hetero

    def from_clusters(self,
                      clusters: rep.BlockClusterSet,
                      arena: ArenaExtent,
                      nest: rep.Nest) -> float:
        clusters_l = list(clusters)
        diagonal = Vector3D.d2norm(arena.ll, arena.ur)
        if 'SS' in self.scenario:
            center = clusters_l[0].extent.center
            dist = Vector3D.d2norm(center, nest.extent.center)
            ret = (dist / diagonal) * (1 / arena.area())
            return ret

        elif 'DS' in self.scenario:
            left_calc = Vector3D.d2norm(clusters_l[0].extent.center,
                                        nest.extent.center)
            right_calc = Vector3D.d2norm(clusters_l[1].extent.center,
                                         nest.extent.center)
            return (((left_calc + right_calc) / 2) / diagonal) * (2 / arena.area())

        variance = Calculator._variance_calc(clusters)
        return (variance / diagonal)*(len(clusters) / arena.area())

    @staticmethod
    def _variance_calc(clusters: rep.BlockClusterSet) -> float:
        """
        This will calculate the variance for the distances measured for each cluster
        and will be probably be a scaled metric to be integrated into the
        existing PDF

        """

        nearest_neighbors = Calculator._nn_calc(clusters)

        # this is an array of variance of each neighbor, ordered from least to
        # greatest distance
        complete_variance = [statistics.variance(i) for i in zip(*nearest_neighbors)]

        return statistics.mean(complete_variance)

    @staticmethod
    def _nn_calc(clusters: rep.BlockClusterSet) -> tp.List[float]:

        ret = []

        for outer in clusters:
            nearest_distance = []

            for inner in clusters:

                if inner == outer:
                    continue

                dist = Vector3D.d2norm(outer.extent.center, inner.extent.center)

                if nearest_distance:
                    if min(nearest_distance) > dist:
                        index = nearest_distance.index(min(nearest_distance))
                        nearest_distance[index] = dist
                else:
                    nearest_distance.append(dist)

            # so that variance comparisons compare similar neighbors
            nearest_distance.sort()
            ret.append(nearest_distance)
        return ret
