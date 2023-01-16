# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
"""
.. IMPORTANT:: The attribute names specified here for vertices and edges must
               match the names of the structs attached to the boost:graph
               properties in PRISM exactly, or run-time errors will
               result.
"""
# Core packages

# 3rd party packages

# Project packages

kBlockTypes = {
    'beam1': 1,
    'beam2': 2,
    'beam3': 3,
    'ramp2': 4,
    'vbeam1': 5,
}
kBlockColors = {
    'beam1': 'red',
    'beam2': 'green',
    'beam3': 'blue',
    'ramp2': 'yellow',
    'vbeam1': 'grey',
}

kBlockExtents = {
    'beam1': 1,
    'beam2': 2,
    'beam3': 3,
    'vbeam1': 1
}
kBlockTypeKey = 'type'
kVertexAnchorKey = 'anchor'
kVertexColorKey = 'color'
kVertexZRotKey = 'z_rot'
