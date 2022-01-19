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
import os
import typing as tp

# 3rd party packages
import pandas as pd

# Project packages
from sierra.core.pipeline.stage3 import run_collator
import sierra.core.storage as storage


class ExperimentalRunCSVGatherer(run_collator.ExperimentalRunCSVGatherer):
    def gather_csvs_from_run(self, run: str) -> tp.Dict[tp.Tuple[str, str], pd.DataFrame]:
        ret = super().gather_csvs_from_run(run)

        intra_interference_leaf = self.main_config['sierra']['perf']['intra_interference_csv'].split('.')[
            0]
        intra_interference_col = self.main_config['sierra']['perf']['intra_interference_col']

        run_output_root = os.path.join(self.exp_output_root,
                                       run,
                                       self.run_metrics_leaf)

        reader = storage.DataFrameReader(self.storage_medium)
        run_output_root = os.path.join(self.exp_output_root,
                                       run,
                                       self.run_metrics_leaf)
        interference_df = reader(os.path.join(run_output_root,
                                              intra_interference_leaf + '.csv'),
                                 index_col=False)
        key = (intra_interference_leaf, intra_interference_col)
        ret.update({key: interference_df[intra_interference_col]})
        return ret
