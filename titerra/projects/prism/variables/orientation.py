# Copyright 2021 John Harwell, All rights reserved.
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
import typing as tp
import re

# 3rd party packages

# Project packages


class Orientation():
    """
    Represents the orientation of a construction target as one of the 4 cardinal directions.
    """

    def __init__(self, val: str) -> None:
        self.str_val = val
        self.num_val = self.to_radians(val)

    def __str__(self):
        return str(self.num_val)

    def is_NS(self) -> bool:
        return self.str_val in ['PI/2', '3PI/2']

    def is_EW(self) -> bool:
        return self.str_val in ['0', 'PI']

    @staticmethod
    def to_radians(orientation: str) -> float:
        if orientation == '0':
            return 0.0
        elif orientation == 'PI/2':
            return math.pi / 2.0
        elif orientation == 'PI':
            return math.pi
        elif orientation == '3PI/2':
            return math.pi * 1.5


class OrientationParser():
    """
    Enforces the cmdline definition of the :class:`Orientation` specified in
    :ref:`ln-prism-bc-ct-specs`.
    """

    def __call__(self, cmdline: str) -> tp.Dict[str, tp.Any]:
        """
        Returns:
            List of dictionaries
                orientation:

        """
        ret = {}

        # Parse target orientation
        res = re.search(r"3PI/2|PI/2|PI|0", cmdline)
        assert res is not None, \
            "Bad target orientation specification in {0}".format(cmdline)
        ret['orientation'] = res.group(0)

        return ret
