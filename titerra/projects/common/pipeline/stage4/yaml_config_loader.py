# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import typing as tp
import pathlib

# 3rd party packages
import yaml
import sierra.core.pipeline.stage4.yaml_config_loader as ycl
from sierra.core import types, utils

# Project packages


class YAMLConfigLoader(ycl.YAMLConfigLoader):
    """
    Load YAML config common to all projects in TITAN.
    """

    def __init__(self) -> None:
        super().__init__()

    def __call__(self, cmdopts: types.Cmdopts) -> tp.Dict[str, types.YAMLDict]:
        inter_LN_config = {}
        intra_LN_config = {}
        intra_HM_config = {}

        common_config_root = pathlib.Path(cmdopts['project_root'],
                                          '..',
                                          'common',
                                          'config')
        common_intra_LN = common_config_root / 'intra-graphs-line.yaml'
        common_intra_HM = common_config_root / 'intra-graphs-hm.yaml'
        common_inter_LN = common_config_root / 'inter-graphs-line.yaml'

        # Load TITAN base/common config
        if utils.path_exists(common_intra_LN):
            self.logger.info(
                "Loading intra-experiment linegraph config for TITAN")
            intra_LN_config = yaml.load(open(common_intra_LN), yaml.FullLoader)

        if utils.path_exists(common_intra_HM):
            self.logger.info(
                "Loading intra-experiment heatmap config for TITAN")
            intra_HM_config = yaml.load(open(common_intra_HM), yaml.FullLoader)

        if utils.path_exists(common_inter_LN):
            self.logger.info(
                "Loading inter-experiment linegraph config for TITAN")
            inter_LN_config = yaml.load(open(common_inter_LN), yaml.FullLoader)

        return {
            'intra_LN': intra_LN_config,
            'intra_HM': intra_HM_config,
            'inter_LN': inter_LN_config,
            'inter_HM': {}
        }
