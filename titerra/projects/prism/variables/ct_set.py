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
Classes for the construct target set variable. See :ref:`ln-prism-var-ct-set`
for usage documentation.
"""

# Core packages
import re
import typing as tp
import os

# 3rd party packages
import implements
from sierra.core.variables.base_variable import IBaseVariable
from sierra.core.xml import XMLTagAddList, XMLTagRmList, XMLTagRm, XMLTagAdd, XMLAttrChangeSet
from sierra.core import types

# Project packages

from titerra.projects.prism.variables import construction_targets as ct
import titerra.projects.prism.variables.orientation as orientation


@implements.implements(IBaseVariable)
class ConstructionTargetSet():
    """
    Composite class wrapping a set of one or more construction targets to build.
    """

    def __init__(self,
                 target_specs: types.CLIArgSpec,
                 graphml_root: str) -> None:
        self.target_specs = target_specs
        self.graphml_root = graphml_root

        self.targets = []
        self.tag_adds = []

        target_id = 0
        for spec in self.target_specs:
            if spec['shape'] == 'prism':
                self.targets.append(self._gen_prism(target_id, spec))
            elif spec['shape'] == 'pyramid':
                self.targets.append(self._gen_pyramid(target_id, spec))
            elif spec['shape'] == 'ramp':
                self.targets.append(self._gen_ramp(target_id, spec))
            else:
                assert False,\
                    "Missing case for target shape '{0}'".format(spec['type'])

            target_id += 1

    def gen_attr_changelist(self) -> tp.List[XMLAttrChangeSet]:
        """
        Does nothing because all tags/attributes are either deleted or added.
        """
        return []

    def gen_tag_rmlist(self) -> tp.List[XMLTagRmList]:
        """
        Always remove the ``<construct_targets>`` tag if it exists so we are
        starting from a clean slate each time. Obviously you *must* call this
        function BEFORE adding new definitions. Because both robots and loop
        functions need the full structure definition, we remove it from each.

        """
        return [XMLTagRmList(XMLTagRm(".//loop_functions",
                                      "./construct_targets"))]

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
            graph = target.gen_graph()
            target.write_graphml(graph, target.graphml_path)

    def _gen_prism(self, target_id: int, spec: types.CLIArgSpec):
        if spec['composition'] == 'beam1':
            graphml_path = os.path.join(self.graphml_root,
                                        ct.Beam1Prism.uuid(target_id) + '.graphml')
            return ct.Beam1Prism(spec, target_id, graphml_path)
        elif spec['composition'] == 'mixed_beam':
            graphml_path = os.path.join(self.graphml_root,
                                        ct.MixedBeamPrism.uuid(target_id) + '.graphml')
            return ct.MixedBeamPrism(spec, target_id, graphml_path)

    def _gen_pyramid(self, target_id: int, spec: types.CLIArgSpec):
        if spec['composition'] == 'beam1':
            graphml_path = os.path.join(self.graphml_root,
                                        ct.Beam1Pyramid.uuid(target_id) + '.graphml')
            return ct.Beam1Pyramid(spec, target_id, graphml_path)

    def _gen_ramp(self, target_id: int, spec: types.CLIArgSpec):
        if spec['composition'] == 'ramp+beam1':
            graphml_path = os.path.join(self.graphml_root,
                                        ct.Ramp.uuid(target_id) + '.graphml')
            return ct.Ramp(spec, target_id, graphml_path)


class Parser():
    """
    Enforces the cmdline definition of the :class:`ConstructTargets` specified
    in :ref:`ln-prism-bc-ct-specs`.

    """

    def __call__(self,
                 specs: tp.List[str],
                 orientations: tp.List[str]) -> tp.List[types.CLIArgSpec]:
        """
        Returns:
            List of dictionaries (one per parsed construction target) with keys:
                shape: prism|ramp|pyramid
                composition: ramp+beam1|beam1|mixed_beam
                bb: (X,Y,Z)
                anchor: (X,Y)
                orientation: X|Y

        """
        ret = []
        for spec, orient in zip(specs, orientations):
            # strip off 'construct_target.'
            spec = '.'.join(spec.split('.')[1:])
            parsed_spec = {}

            # Parse target shape
            res = re.search("prism|ramp|pyramid", spec)
            assert res is not None, \
                "Bad target shape specification in {0}".format(spec)
            parsed_spec['shape'] = res.group(0)

            # Parse target composition
            res = re.search(r"ramp\+beam1|beam1|mixed_beam", spec)
            assert res is not None, \
                "Bad target composition specification in {0}".format(spec)
            parsed_spec['composition'] = res.group(0)

            if parsed_spec['shape'] == 'ramp':
                assert parsed_spec['composition'] == 'ramp+beam1',\
                    "Bad composition specification for {0}".format(
                        parsed_spec['shape'])
            elif parsed_spec['shape'] == 'prism':
                assert parsed_spec['composition'] in ['beam1', 'mixed_beam'],\
                    "Bad composition specification for {0}".format(
                        parsed_spec['shape'])
            elif parsed_spec['shape'] == 'pyramid':
                assert parsed_spec['composition'] == 'beam1',\
                    "Bad composition specification for {0}".format(
                        parsed_spec['shape'])

            # Parse target bounding box
            res = re.search('[0-9]+x[0-9]+x[0-9]+', spec)
            assert res is not None, \
                "Bad target bounding box specification in {0}".format(spec)
            parsed_spec['bb'] = tuple(int(x) for x in res.group(0).split('x'))

            # Parse target anchor
            res = re.search(r"@[0-9]+,[0-9]+,[0-9]+", spec)
            assert res is not None,\
                "Bad target anchor specification in {0}".format(spec)
            parsed_spec['anchor'] = tuple(int(x) for x in
                                          res.group(0)[1:].split(','))

            # Parse target orientation
            res = orientation.OrientationParser()(orient)
            parsed_spec.update(res)
            ret.append(parsed_spec)

        return ret


def factory(specs: tp.List[str],
            orientations: tp.List[str],
            exp_input_root: str):
    """
    Factory to create :class:`ConstructTargetSet` derived classes from the
    cmdline specification.
    """
    assert len(specs) == len(orientations),\
        "# specs != # orientations: {0} != {1}".format(len(specs),
                                                              len(orientations))
    targets = Parser()(specs, orientations)

    for target in targets:
        target['orientation'] = orientation.Orientation(target['orientation'])

    return ConstructionTargetSet(targets, exp_input_root)
