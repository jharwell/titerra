# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import math
import typing as tp
import re

# 3rd party packages
import numpy as np

# Project packages
from sierra.core import types


class Orientation():
    """
    Represents the orientation of a construction target as one of the 4 cardinal
    directions.
    """

    @staticmethod
    def from_num(val: float) -> 'Orientation':
        if np.isclose([val], [0], rtol=0, atol=10 ** -3):
            return Orientation('0')
        elif np.isclose([val], [math.pi/2.0], rtol=0, atol=10 ** -3):
            return Orientation('PI/2')
        elif np.isclose([val], [math.pi], rtol=0, atol=10 ** -3):
            return Orientation('PI')
        elif np.isclose([val], [3.0 * math.pi/2.0], rtol=0, atol=10 ** -3):
            return Orientation('3PI/2')

        assert False

    def __init__(self, val: str) -> None:
        self.str_val = val
        self.num_val = self.to_radians(val)

    def __str__(self):
        return str(self.num_val)

    def is_NS(self) -> bool:
        return self.is_N() or self.is_S()

    def is_EW(self) -> bool:
        return self.is_E() or self.is_W()

    def is_N(self) -> bool:
        return self.str_val in ['PI/2']

    def is_S(self) -> bool:
        return self.str_val in ['3PI/2']

    def is_E(self) -> bool:
        return self.str_val in ['0']

    def is_W(self) -> bool:
        return self.str_val in ['PI']

    @staticmethod
    def to_radians(orientation: str) -> float:
        if orientation == '0':
            return 0.0
        if orientation == 'PI/2':
            return math.pi / 2.0
        if orientation == 'PI':
            return math.pi
        if orientation == '3PI/2':
            return math.pi * 1.5

        assert False


class OrientationParser():
    """
    Enforces the cmdline definition of the :class:`Orientation` specified in
    :ref:`ln-prism-bc-ct-specs`.
    """

    def __call__(self, cmdline: str) -> types.CLIArgSpec:
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
