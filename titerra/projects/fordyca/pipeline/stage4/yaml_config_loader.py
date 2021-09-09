# Copyright 2021 John Harwell, All rights reserved.
#
#  This file is part of TITAN.
#
#  TITAN is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  TITAN is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  TITAN.  If not, see <http://www.gnu.org/licenses/

# Core packages
import os
import typing as tp

# 3rd party packages
import yaml

# Project packages
import titerra.projects.titan.pipeline.stage4.yaml_config_loader as ycl
import sierra.core.utils


class YAMLConfigLoader(ycl.YAMLConfigLoader):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, cmdopts: tp.Dict[str, tp.Any]) -> tp.Dict[str, tp.Dict[str, str]]:
        joint_config = super().__call__(cmdopts)

        fordyca_inter_LN = os.path.join(cmdopts['project_config_root'],
                                        'inter-graphs-line.yaml')
        fordyca_intra_LN = os.path.join(cmdopts['project_config_root'],
                                        'intra-graphs-line.yaml')
        fordyca_intra_HM = os.path.join(cmdopts['project_config_root'],
                                        'intra-graphs-hm.yaml')

        # Load FORDYCA config
        if sierra.core.utils.path_exists(fordyca_intra_LN):
            self.logger.info("Loading intra-experiment linegraph config for FORDYCA")
            fordyca_dict = yaml.load(open(fordyca_intra_LN), yaml.FullLoader)

            for category in fordyca_dict:
                if category not in joint_config['intra_LN']:
                    joint_config['intra_LN'].update({category: fordyca_dict[category]})
                else:
                    joint_config['intra_LN'][category]['graphs'].extend(
                        fordyca_dict[category]['graphs'])

        if sierra.core.utils.path_exists(fordyca_intra_HM):
            self.logger.info("Loading intra-experiment heatmap config for FORDYCA")
            fordyca_dict = yaml.load(open(fordyca_intra_HM), yaml.FullLoader)

            for category in fordyca_dict:
                if category not in joint_config['intra_HM']:
                    joint_config['intra_HM'].update({category: fordyca_dict[category]})
                else:
                    joint_config['intra_HM'][category]['graphs'].extend(
                        fordyca_dict[category]['graphs'])

        if sierra.core.utils.path_exists(fordyca_inter_LN):
            self.logger.info("Loading inter-experiment linegraph config for project '%s'",
                             cmdopts['project'])
            fordyca_dict = yaml.load(open(fordyca_inter_LN), yaml.FullLoader)

            for category in fordyca_dict:
                if category not in joint_config['inter_LN']:
                    joint_config['inter_LN'].update({category: fordyca_dict[category]})
                else:
                    joint_config['inter_LN'][category]['graphs'].extend(
                        fordyca_dict[category]['graphs'])

        return joint_config
