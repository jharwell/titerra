# Copyright 2021 John Harwell, All rights reserved.
#
#  This file is part of TITERRA.
#
#  TITERRA is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  TITERRA is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  TITERRA.  If not, see <http://www.gnu.org/licenses/

# Core packages
import typing as tp
import pathlib

# 3rd party packages
import pandas as pd
from sierra.core.pipeline import stage3
from sierra.core import storage, config

# Project packages


class ExperimentalRunCSVGatherer(stage3.run_collator.ExperimentalRunCSVGatherer):
    def gather_csvs_from_run(self,
                             run_output_root: pathlib.Path) -> tp.Dict[tp.Tuple[str, str],
                                                                       pd.DataFrame]:
        ret = super().gather_csvs_from_run(run_output_root)

        perf_config = self.main_config['sierra']['perf']
        intra_interference_leaf = perf_config['intra_interference_csv'].split('.')[0]
        intra_interference_col = perf_config['intra_interference_col']

        reader = storage.DataFrameReader(self.storage_medium)
        interference_ipath = run_output_root / (intra_interference_leaf +
                                                config.kStorageExt['csv'])
        interference_df = reader(interference_ipath, index_col=False)
        key = (intra_interference_leaf, intra_interference_col)
        ret.update({key: interference_df[intra_interference_col]})
        return ret
