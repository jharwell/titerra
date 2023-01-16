# Copyright 2020 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import math

# 3rd party packages
import scipy.integrate as si

# Project packages
from sierra.core.vector import Vector3D
from titerra.projects.fordyca_base.models.representation import Nest


class DistanceMeasure2D():
    """Defines how the distance between two (X,Y) points in the plane should be
    measured. This is necessary in order to handle different block distributions
    within the same model.

    """

    def __init__(self, scenario: str, nest: Nest):
        self.scenario = scenario
        self.nest = nest

        if 'RN' in self.scenario or 'PL' in self.scenario:
            # Our model assumes all robots finish foraging EXACTLY at the nest
            # center, and the implementation has robots pick a random point
            # between where they enter the nest and the center, in order to
            # reduce congestion.
            #
            # This has the effect of making the expected distance the robots
            # travel after entering the nest but before dropping their object
            # LESS than the distance the model assumes. So, we calculate the
            # average distance from any point in the square defined by HALF the
            # nest span in X,Y (HALF being a result of uniform random choice in
            # X,Y) to the nest center:
            # https://math.stackexchange.com/questions/15580/what-is-average-distance-from-center-of-square-to-some-point
            edge = nest.extent.xsize() / 2.0
            self.nest_factor = edge / 6.0 * \
                (math.sqrt(2.0) + math.log(1 + math.sqrt(2.0)))
        elif 'SS' in self.scenario:
            # When I solve for the length of the edge of the triangle bisected
            # by the middle of the nest in X as a percentage of xsize(), I get
            # 0.032, and we want to integrate equally on either side of that.
            xmin = self.nest.extent.center.x
            xmax = self.nest.extent.center.x + self.nest.extent.xsize() / 2.0
            ymin = self.nest.extent.center.y - self.nest.extent.ysize() / 32.0
            ymax = self.nest.extent.center.y + self.nest.extent.ysize() / 32.0

            res, _ = si.nquad(lambda x, y: (self.nest.extent.center - Vector3D(x, y)).length(),
                              [[xmin, xmax], [ymin, ymax]],
                              opts={'limit': 100})
            # Because the effective area is actually a triangle, we take 1/2 the
            # area of the square we integrate over. This is NOT an exact
            # calculation, but it is close enough for now (2021/3/26).
            eff_area = (xmax - xmin) * (ymax - ymin) / 2.0
            self.nest_factor = res / eff_area

        elif 'DS' in self.scenario:
            # When I solve for the length of the edge of the triangle bisected
            # by the middle of the nest in X as a percentage of xsize(), I get
            # 0.125, and we want to integrate equally on either side of that.
            xmin = self.nest.extent.center.x
            xmax = self.nest.extent.center.x + self.nest.extent.xsize() / 2.0
            ymin = self.nest.extent.center.y - self.nest.extent.ysize() / 16.0
            ymax = self.nest.extent.center.y + self.nest.extent.ysize() / 16.0
            res, _ = si.nquad(lambda x, y: (self.nest.extent.center - Vector3D(x, y)).length(),
                              [[xmin, xmax], [ymin, ymax]],
                              opts={'limit': 100})

            # Because the effective area is actually a triangle, we take 1/2 the
            # area of the square we integrate over. This is NOT an exact
            # calculation, but it is close enough for now (2021/3/26).
            eff_area = (xmax - xmin) * (ymax - ymin) / 2.0
            self.nest_factor = res / eff_area

    def to_nest(self, pt: Vector3D):

        return (self.nest.extent.center - pt).length() - self.nest_factor
