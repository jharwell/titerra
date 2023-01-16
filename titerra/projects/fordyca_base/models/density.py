# Copyright 2020 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import math
import typing as tp

# 3rd party packages
import scipy.integrate as si

# Project packages
import sierra.core.utils
from sierra.core.vector import Vector3D

import titerra.projects.fordyca_base.models.representation as rep
from titerra.projects.fordyca_base.models.dist_measure import DistanceMeasure2D


class BaseDensity():
    def at_point(self, x: tp.Optional[float] = None, y: tp.Optional[float] = None) -> float:
        """Get the value of the density at an x,y point. Either x or y can be None (but
        not both). If x is None, then the value of :meth:`at_point()` should
        return the project of the densty function on the x axis, and vice versa.

        """
        raise NotImplementedError

    def for_region(self, ll: Vector3D, ur: Vector3D):
        r"""Calculate the cumulative probability density within a region defined by the
        lower left and upper right corners of the 2D region using
        :method:`at_point`.

        """
        res, _ = si.nquad(self.at_point, [[ll.x, ur.x], [
                          ll.y, ur.y]], opts={'limit': 100})
        return res

    def evx_for_region(self, ll: Vector3D, ur: Vector3D):
        """Calculate the expected value of the X coordinate of the average density
        location within the region defined by the lower left and upper right
        corners of the 2D region.

        """
        res, _ = si.nquad(lambda x: self._marginal_pdfx(ll=ll, ur=ur) * x,
                          [[ll.x, ur.x]],
                          opts={'limit': 100})

        return res

    def evy_for_region(self, ll: Vector3D, ur: Vector3D):
        """Calculate the expected value of the Y coordinate of the average density
        location within the region defined by the lower left and upper right
        corners of the 2D region.

        """
        res, _ = si.nquad(lambda y: self._marginal_pdfy(ll=ll, ur=ur) * y,
                          [[ll.y, ur.y]],
                          opts={'limit': 100})
        return res

    def _marginal_pdfx(self, ll: Vector3D, ur: Vector3D):
        """
        Calculate the marginal PDF of density function for X.
        """
        res, _ = si.nquad(lambda y: self.at_point(None, y),
                          [[ll.y, ur.y]],
                          opts={'limit': 100})
        return res

    def _marginal_pdfy(self, ll: Vector3D, ur: Vector3D):
        """
        Calculate the marginal PDF of the density function for Y.
        """
        pdf, _ = si.nquad(lambda x: self.at_point(x, None),
                          [[ll.x, ur.x]],
                          opts={'limit': 100})
        return pdf


class ClusterBlockDensity(BaseDensity):
    """
    Cluster block density calculations.

    This definition assumes:

    - Uniform block distribution within the cluster's extent.
    - Cubical blocks.
    """
    kCUBE_BLOCK_DIM = 0.2

    def __init__(self, cluster: rep.BlockCluster, nest: rep.Nest):
        self.cluster = cluster
        self.nest = nest

        area = self.cluster.extent.area()

        # Random block distributions have the nest in the middle of the cluster,
        # and blocks are not distributed within the nest's extent, so we adjust
        # accordingly.
        if cluster.extent.contains(nest.extent.center):
            area -= nest.extent.area()

        # Block density is the total 2D area covered by blocks, as a fraction of
        # the total area. We can't just use # blocks, as the density then can be
        # < 1 or > 1, depending. This way, it is ALWAYS <= 1.
        self.rho_b = self.cluster.avg_blocks * self.kCUBE_BLOCK_DIM ** 2 / area

        # Since we assume a uniform distribution, normalizing to get a true
        # density function is easy to do analytically. rho_b can be 0 in PL if
        # the cluster never had any blocks distributed to it during simulation.
        self.norm_factor = 1.0 / (self.rho_b * area) if self.rho_b > 0.0 else 0.0

    def at_point(self, x: tp.Optional[float] = None, y: tp.Optional[float] = None):
        r"""
        Calculate the block density at an (X,Y) point within the extent of the block cluster.
        """
        assert x is not None and y is not None

        pt = Vector3D(x, y)

        # No density outside cluster extent
        if not self.cluster.extent.contains(pt):
            return 0.0
        # No density inside nest
        elif self.nest.extent.contains(pt):
            return 0.0

        return self.rho_b * self.norm_factor


class BlockAcqDensity(BaseDensity):
    """
    Block acquisition probability density calculations.
    """

    def __init__(self,
                 nest: rep.Nest,
                 cluster: rep.BlockCluster,
                 dist_measure: DistanceMeasure2D):
        self.nest = nest
        self.dist_measure = dist_measure
        self.cluster = cluster
        cd = ClusterBlockDensity(cluster=cluster, nest=nest)

        # Cluster density can be 0 for PL if the cluster is small and no blocks were ever
        # distributed to it during simulation.
        # self.rho = -math.log((1.0 / 2.0) ** cd.rho_b) if cd.rho_b > 0.0 else None
        self.rho = -math.log(math.pow(cd.rho_b, cd.rho_b / 2.0)
                             ) if cd.rho_b > 0.0 else None

        # We normalize our density function within the cluster we are attached
        # to, NOT across all clusters. When calculating expected value we need
        # to integrate across all possible values of X/Y, and if we have
        # normalized our density function across multiple clusters, then
        # calculating the expected acquisition location for a single cluster
        # will be incorrect.
        self.norm_factor = 1.0
        total = self.for_region(ll=cluster.extent.ll, ur=cluster.extent.ur)

        # Can be 0 for PL if the cluster is small and no blocks were ever
        # distributed to it during simulation.
        self.norm_factor = 1.0 / total if total > 0 else 0.0

    def at_point(self, x: tp.Optional[float] = None, y: tp.Optional[float] = None):
        r"""Calculate the block acquisition probability density at an (X,Y) point within
        the arena.

        .. math::
           \frac{1}{{\sqrt{z + -\log{\rho_b ^ {\rho_b / 2}}}}

        where :math:`z` is the distance of the (X,Y) point to the center of the
        nest, and :math:`\rho_b` is the block density at (X,Y).

        """

        if x is None and y is not None:  # Calculating marginal PDF of X
            pt = Vector3D(self.cluster.extent.center.x, y)
        elif x is not None and y is None:  # Calculating marginal PDF of Y
            pt = Vector3D(x, self.cluster.extent.center.y)
        else:  # Normal case
            assert x is not None and y is not None
            pt = Vector3D(x, y)

        # No acquisitions possible if the cluster never had any blocks in it
        # during simulation.
        if self.rho is None:
            return 0.0

        z = self.dist_measure.to_nest(pt)
        if z < 0:
            z = 0
        return 1.0 / ((math.sqrt(z) + self.rho) ** 2) * self.norm_factor
