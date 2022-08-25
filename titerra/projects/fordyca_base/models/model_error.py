# Copyright 2020 John Harwell, All rights reserved.
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
import pathlib
import copy
import typing as tp

# 3rd party packages
import pandas as pd
from sierra.core import types, utils, storage
import sierra.core.models.interface

# Project packages
import titerra.variables.batch_criteria as bc


class Model2DError():
    """Runs the specified :class:`models.interface.IConcreteIntraExpModel2D` for
    each experiment in the batch, computing the average error between model
    prediction and empirical data as a single data point.

    Returns a 1D data frame for the batch.

    """

    def __init__(self,
                 stddev_fname: str,
                 model: sierra.core.models.interface.IConcreteIntraExpModel2D,
                 main_config: types.YAMLDict,
                 model_config: types.YAMLDict) -> None:
        self.stddev_fname = stddev_fname
        self.model = model
        self.main_config = main_config
        self.model_config = model_config

    def generate(self,
                 cmdopts: types.Cmdopts,
                 criteria: bc.IConcreteBatchCriteria) -> tp.List[pd.DataFrame]:
        dirs = criteria.gen_exp_names(cmdopts)
        res_df = pd.DataFrame(columns=dirs, index=[0])

        batch_input_root = pathlib.Path(cmdopts['batch_input_root'])
        batch_output_root = pathlib.Path(cmdopts['batch_output_root'])
        batch_model_root = pathlib.Path(cmdopts['batch_model_root'])
        batch_graph_root = pathlib.Path(cmdopts['batch_graph_root'])
        batch_stat_root = pathlib.Path(cmdopts['batch_stat_root'])

        for i, exp in enumerate(dirs):

            # Setup cmdopts for intra-experiment model
            cmdopts2 = copy.deepcopy(cmdopts)

            cmdopts2["exp0_output_root"] = str(batch_output_root / dirs[0])
            cmdopts2["exp0_stat_root"] = str(batch_stat_root / dirs[0])

            cmdopts2["exp_input_root"] = str(batch_input_root / exp)
            cmdopts2["exp_output_root"] = str(batch_output_root / exp)
            cmdopts2["exp_graph_root"] = str(batch_graph_root / exp)
            cmdopts2["exp_stat_root"] = str(batch_stat_root / exp)
            cmdopts2["exp_model_root"] = str(batch_model_root / exp)

            utils.dir_create_checked(cmdopts2['exp_model_root'], exist_ok=True)

            # Calculate model prediction heatmap
            model_df = self.model(self.main_config, self.model_config).run(
                cmdopts2, criteria, i)

            # Get data heatmap
            data_ipath = pathlib.Path(cmdopts2['exp_stat_root'],
                                      self.stddev_fname)
            reader = storage.DataFrameReader('storage.csv')
            data_df = reader(data_ipath)

            # Compute datapoint
            d1_norm = (model_df - data_df).abs().to_numpy().sum()
            # d2_norm = (model_df - data_df).pow(2).sum(1).sum()
            res_df[exp] = d1_norm

        return [res_df]
