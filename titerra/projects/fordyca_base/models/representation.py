# Copyright 2020 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import pathlib
import typing as tp

# 3rd party packages
import pandas as pd
from sierra.core import storage, types
from sierra.core.experiment.spec import ExperimentSpec
from sierra.core.utils import ArenaExtent
from sierra.core.vector import Vector3D

# Project packages
import titerra.projects.common.generators.scenario_generator_parser as sgp
from titerra.platform.argos.variables import nest
import titerra.variables.batch_criteria as bc


class BlockCluster():
    """
    Representation of a block cluster object within the arena.
    """
    @classmethod
    def from_df(cls, clusters_df: pd.DataFrame, cluster_id: int) -> 'BlockCluster':
        col_stem = 'cluster' + str(cluster_id)

        xmin = clusters_df.filter(regex=col_stem + '_xmin').iloc[-1].values[0]
        xmax = clusters_df.filter(regex=col_stem + '_xmax').iloc[-1].values[0]
        ymin = clusters_df.filter(regex=col_stem + '_ymin').iloc[-1].values[0]
        ymax = clusters_df.filter(regex=col_stem + '_ymax').iloc[-1].values[0]

        # We approximate the # blocks in a cluster (which changes dynamically)
        # as a steady state quantity, where each cluster always contains the
        # fraction of total blocks in the arena corresponding to how much of the
        # overall distributable area it contains.
        total_blocks = clusters_df.filter(
            regex='int_avg_cluster[0-9]*_block_count').iloc[-1].sum()
        total_area = clusters_df.filter(
            regex='cluster[0-9]*_area').iloc[-1].sum()
        cluster_area = ArenaExtent.from_corners(ll=Vector3D(xmin, ymin),
                                                ur=Vector3D(xmax, ymax)).area()
        cluster_avg_blocks = total_blocks * cluster_area / total_area

        return BlockCluster(ll=Vector3D(xmin, ymin),
                            ur=Vector3D(xmax, ymax),
                            cluster_id=cluster_id,
                            avg_blocks=cluster_avg_blocks)

    def __init__(self, ll: Vector3D, ur: Vector3D, cluster_id: int, avg_blocks: float) -> None:
        self.extent = ArenaExtent.from_corners(ll=ll, ur=ur)
        self.cluster_id = cluster_id
        self.avg_blocks = avg_blocks


class Nest():
    def __init__(self, cmdopts: types.Cmdopts, criteria: bc.IConcreteBatchCriteria, exp_num: int):
        # Get nest position
        spec = ExperimentSpec(criteria, exp_num, cmdopts)
        res = sgp.ScenarioGeneratorParser().to_dict(cmdopts['scenario'])
        pose = nest.Nest(src='arena',
                         dist_type=res['scenario_tag'],
                         arena=spec.arena_dim)

        for _, tag, attr in pose.gen_tag_addlist()[0]:
            if tag == 'nest':
                x, y = attr['center'].split(',')
                center = Vector3D(float(x), float(y), 0.0)
                x, y = attr['dims'].split(',')
                dims = Vector3D(float(x), float(y), 0.0)

        self.extent = ArenaExtent(dims, center - dims / 2.0)


class BlockClusterSet():
    """
    Given a simulation directory within an experiment in a batch, calculate the
    :class:`BlockCluster`s for all clusters within the arena.

    Arguments:

       main_config: Main YAML configuration for project.

       cmdopts: Parsed cmdline parameters.

       clusters_fpath: Directory to the ``block-clusters.XXX`` can be
                       found.
    """

    def __init__(self,
                 cmdopts: types.Cmdopts,
                 nest: Nest,
                 clusters_fpath: pathlib.Path) -> None:

        reader = storage.DataFrameReader('storage.csv')
        clusters_df = reader(clusters_fpath)
        n_clusters = len([c for c in clusters_df.columns if 'xmin' in c])

        # Create extents from clusters
        self.clusters = set()

        # RN block distribution has a single cluster, but the nest is in the
        # middle of it, which makes density calculations much trickier when
        # integrating across/up to the nest (modeled as a single point). We
        # break it into an equivalent set of 4 smaller clusters ringing the nest
        # to avoid computational issues.

        if 'RN' in cmdopts['scenario']:
            cluster = BlockCluster.from_df(clusters_df, 0)
            total_area = cluster.extent.area()

            ll1 = cluster.extent.ll
            ur1 = Vector3D(nest.extent.ll.x, cluster.extent.ur.y)
            c1_extent = ArenaExtent.from_corners(ll=ll1, ur=ur1)

            c1 = BlockCluster(ll=ll1,
                              ur=ur1,
                              cluster_id=0,
                              avg_blocks=cluster.avg_blocks * c1_extent.area() / total_area)

            ll2 = Vector3D(nest.extent.ll.x, cluster.extent.ll.y)
            ur2 = Vector3D(nest.extent.ur.x, nest.extent.ll.y)
            c2_extent = ArenaExtent.from_corners(ll=ll2, ur=ur2)

            c2 = BlockCluster(ll=ll2,
                              ur=ur2,
                              cluster_id=1,
                              avg_blocks=cluster.avg_blocks * c2_extent.area() / total_area)

            ll3 = Vector3D(nest.extent.ll.x, nest.extent.ur.y)
            ur3 = Vector3D(nest.extent.ur.x, cluster.extent.ur.y)
            c3_extent = ArenaExtent.from_corners(ll=ll3, ur=ur3)

            c3 = BlockCluster(ll=ll3,
                              ur=ur3,
                              cluster_id=2,
                              avg_blocks=cluster.avg_blocks * c3_extent.area() / total_area)

            ll4 = Vector3D(nest.extent.ur.x, cluster.extent.ll.y)
            ur4 = cluster.extent.ur
            c4_extent = ArenaExtent.from_corners(ll=ll4, ur=ur4)

            c4 = BlockCluster(ll=ll4,
                              ur=ur4,
                              cluster_id=3,
                              avg_blocks=cluster.avg_blocks * c4_extent.area() / total_area)

            self.clusters = set([c1, c2, c3, c4])

        else:  # General case
            for c in range(0, n_clusters):
                self.clusters |= set([BlockCluster.from_df(clusters_df, c)])

    def __iter__(self):
        return iter(self.clusters)

    def __len__(self):
        return len(self.clusters)
