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

"""
Classes for the construct target set variable. See :ref:`ln-silicon-var-ct-set` for usage
documentation.
"""

# Core packages
import re
import typing as tp
import os

# 3rd party packages
import implements
import networkx as nx

# Project packages
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.utils import ArenaExtent as ArenaExtent
from sierra.core.xml_luigi import XMLTagAddList, XMLTagRmList, XMLTagRm, XMLTagAdd, XMLAttrChangeSet
from sierra.core.vector import Vector3D

from projects.silicon.variables import construction_targets as ct


@implements.implements(IBaseVariable)
class ConstructionTargetSet():
    """
    Composite class wrapping a set of one or more construction targets to build.
    """

    def __init__(self,
                 target_specs: tp.Dict[str, tp.Any],
                 graphml_root: str) -> None:
        self.target_specs = target_specs
        self.graphml_root = graphml_root

        self.targets = []
        self.tag_adds = []

        uuid = 0
        for spec in self.target_specs:
            if spec['type'] == 'rectprism':
                graphml_path = os.path.join(
                    self.graphml_root, ct.RectPrismTarget.target_id(uuid) + '.graphml')
                self.targets.append(ct.RectPrismTarget(spec, uuid, graphml_path))
            elif spec['type'] == 'ramp':
                graphml_path = os.path.join(
                    self.graphml_root, ct.RampTarget.target_id(uuid) + '.graphml')
                self.targets.append(ct.RampTarget(spec, uuid, graphml_path))

            uuid += 1

    def gen_attr_changelist(self) -> tp.List[XMLAttrChangeSet]:
        """
        Does nothing because all tags/attributes are either deleted or added.
        """
        return []

    def gen_tag_rmlist(self) -> tp.List[XMLTagRmList]:
        """
        Always remove the ``<construct_targets>`` tag if it exists so we are starting from a clean
        slate each time. Obviously you *must* call this function BEFORE adding new
        definitions. Because both robots and loop functions need the full structure definition, we
        remove it from each.
        """
        return [XMLTagRmList(XMLTagRm(".//loop_functions", "./construct_targets"))]

    def gen_tag_addlist(self) -> tp.List[XMLTagAddList]:
        if not self.tag_adds:
            self.tag_adds = XMLTagAddList(XMLTagAdd('.//loop_functions',
                                                    'construct_targets',
                                                    {}))
            for target in self.targets:
                self.tag_adds.extend(target.gen_xml())

        return [self.tag_adds]

    def gen_files(self) -> None:
        for target in self.targets:
            graph = target.gen_graphml()
            graphml_path = os.path.join(
                self.graphml_root, target.target_id(target.uuid) + '.graphml')
            target.write_graphml(graph, graphml_path)


class ConstructionTargetSetParser():
    """
    Enforces the cmdline definition of the :class:`ConstructTargets` specified in
    :ref:`ln-silicon-vars-construct-targets`.
    """

    def __call__(self,
                 specs: tp.List[str],
                 orientations: tp.List[str]) -> tp.List[tp.Dict[str, tp.Any]]:
        """
        Returns:
            List of dictionaries (one per parsed construction target) with keys:
                type: ramp|rectprism
                bb: (X,Y,Z)
                anchor: (X,Y)
                orientation: X|Y

        """
        ret = []
        for spec, orientation in zip(specs, orientations):
            spec = '.'.join(spec.split('.')[1:])  # strip off 'construct_target.'
            parsed_spec = {}

            # Parse target type
            res = re.search(r"ramp|rectprism", spec)
            assert res is not None, "Bad target type specification in {0}".format(spec)
            parsed_spec['type'] = res.group(0)

            # Parse target bounding box
            res = re.search('[0-9]+x[0-9]+x[0-9]+', spec)
            assert res is not None, "Bad target bounding box specification in {0}".format(spec)
            parsed_spec['bb'] = tuple(int(x) for x in res.group(0).split('x'))

            # Parse target anchor
            res = re.search(r"@[0-9]+,[0-9]+,[0-9]+", spec)
            assert res is not None, "Bad target anchor specification in {0}".format(spec)
            parsed_spec['anchor'] = tuple(int(x) for x in res.group(0)[1:].split(','))

            # Parse target orientation
            res = re.search(r"3PI/2|PI/2|PI|0", orientation)
            assert res is not None, \
                "Bad target orientation specification in {0}".format(orientation)
            parsed_spec['orientation'] = res.group(0)
            ret.append(parsed_spec)

        return ret


def factory(specs: tp.List[str],
            orientations: tp.List[str],
            exp_input_root: str):
    """
    Factory to create :class:`ConstructTargetSet` derived classes from the cmdline specification.
    """
    targets = ConstructionTargetSetParser()(specs, orientations)

    return ConstructionTargetSet(targets, exp_input_root)
