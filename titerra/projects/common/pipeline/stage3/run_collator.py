# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT

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
