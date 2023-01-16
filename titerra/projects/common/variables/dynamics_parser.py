# Copyright 2020 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import re

# 3rd party packages
from sierra.core import types

# Project packages


class DynamicsParser():
    """
    Base class for some dynamics parsers to reduce code duplication.
    """

    def __init__(self) -> None:
        pass

    def specs_dict(self) -> types.CLIArgSpec:
        raise NotImplementedError

    def __call__(self,
                 criteria_str: str) -> dict:
        ret = {
            'dynamics': list(),
            'factor': float(),
            'dynamics_types': list()
        }
        specs_dict = self.specs_dict()

        # Parse cardinality
        res = re.search(r".C[0-9]+", criteria_str)
        assert res is not None, \
            "Bad cardinality for dynamics in criteria '{0}'".format(
                criteria_str)
        ret['cardinality'] = int(res.group(0)[2:])

        # Parse factor characteristic
        res = re.search(r'F[0-9]+p[0-9]+', criteria_str)
        assert res is not None, \
            "Bad Factor specification in criteria '{0}'".format(
                criteria_str)
        characteristic = float(res.group(0)[1:].split('p')[0])
        mantissa = float("0." + res.group(0)[1:].split('p')[1])

        ret['factor'] = characteristic + mantissa

        # Parse dynamics parameters
        specs = criteria_str.split('.')[3:]
        dynamics = []
        dynamics_types = []

        for spec in specs:
            # Parse characteristic
            res = re.search('[0-9]+p', spec)
            assert res is not None, \
                "Bad characteristic specification in criteria '{0}'".format(
                    criteria_str)
            characteristic = float(res.group(0)[0:-1])

            # Parser mantissa
            res = re.search('p[0-9]+', spec)
            assert res is not None, \
                "Bad mantissa specification in criteria '{0}'".format(
                    criteria_str)
            mantissa = float("0." + res.group(0)[1:])

            for k in specs_dict.keys():
                if k in spec:
                    dynamics.append((specs_dict[k], characteristic + mantissa))
                    dynamics_types.append(k)

        ret['dynamics'] = dynamics
        ret['dynamics_types'] = dynamics_types

        return ret
