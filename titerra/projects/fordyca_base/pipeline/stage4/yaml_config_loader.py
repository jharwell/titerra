# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

# Core packages
import pathlib
import typing as tp
import logging

# 3rd party packages
import yaml

# Project packages
import titerra.projects.common.pipeline.stage4.yaml_config_loader as ycl
from sierra.core import utils, types


class YAMLConfigLoader(ycl.YAMLConfigLoader):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, cmdopts: types.Cmdopts) -> tp.Dict[str, types.YAMLDict]:
        joint_config = super().__call__(cmdopts)

        # Replace logger for more accurate messages
        self.logger = logging.getLogger(__name__)

        root = pathlib.Path(cmdopts['project_config_root'])
        fordyca_inter_LN = root / 'inter-graphs-line.yaml'
        fordyca_intra_LN = root / 'intra-graphs-line.yaml'
        fordyca_intra_HM = root / 'intra-graphs-hm.yaml'

        # Load FORDYCA config
        if utils.path_exists(fordyca_intra_LN):
            self.logger.info("Intra-experiment linegraph config for FORDYCA")
            fordyca_dict = yaml.load(open(fordyca_intra_LN), yaml.FullLoader)

            for category in fordyca_dict:
                if category not in joint_config['intra_LN']:
                    joint_config['intra_LN'].update(
                        {category: fordyca_dict[category]})
                else:
                    joint_config['intra_LN'][category]['graphs'].extend(
                        fordyca_dict[category]['graphs'])

        if utils.path_exists(fordyca_intra_HM):
            self.logger.info("Intra-experiment heatmap config for FORDYCA")
            fordyca_dict = yaml.load(open(fordyca_intra_HM), yaml.FullLoader)

            for category in fordyca_dict:
                if category not in joint_config['intra_HM']:
                    joint_config['intra_HM'].update(
                        {category: fordyca_dict[category]})
                else:
                    joint_config['intra_HM'][category]['graphs'].extend(
                        fordyca_dict[category]['graphs'])

        if utils.path_exists(fordyca_inter_LN):
            self.logger.info("Inter-experiment linegraph config for FORDYCA")
            fordyca_dict = yaml.load(open(fordyca_inter_LN), yaml.FullLoader)

            for category in fordyca_dict:
                if category not in joint_config['inter_LN']:
                    joint_config['inter_LN'].update(
                        {category: fordyca_dict[category]})
                else:
                    joint_config['inter_LN'][category]['graphs'].extend(
                        fordyca_dict[category]['graphs'])

        return joint_config
