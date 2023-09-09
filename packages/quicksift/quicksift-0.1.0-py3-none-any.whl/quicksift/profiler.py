import json
import logging
import os
from datetime import datetime
from functools import cached_property
from typing import Optional

import ray
from fast_eda import statistics


class Profiler:
    def __init__(
        self,
        dataset,
        dataset_operations: Optional[list] = None,
        column_operations: Optional[list] = None,
    ):
        self.analysis_time_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ray.init(ignore_reinit_error=True)
        self.dataset = dataset
        if not dataset_operations:
            self.dataset_operations = [
                statistics.number_rows,
                statistics.number_columns,
            ]
        if not column_operations:
            self.column_operations = [
                statistics.column_min,
                (statistics.column_mean, {"sigdig": 4}),
                statistics.column_variance,
                statistics.column_std,
                statistics.column_quantiles,
                statistics.column_max,
                statistics.column_dtype,
                statistics.column_number_negative,
                statistics.column_proportion_negative,
                statistics.column_number_zeros,
                statistics.column_proportion_zeros,
                statistics.column_number_positive,
                statistics.column_proportion_positive,
            ]
        self._results = []
        for operation in self.dataset_operations:
            self._results.append(operation.remote(self.dataset))
        for column in self.dataset.columns:
            if self.dataset[column].dtype == "object":
                continue
            try:
                for operation in self.column_operations:
                    if isinstance(operation, tuple):
                        self._results.append(
                            operation[0].remote(
                                column={"name": column, "values": self.dataset[column]},
                                **operation[1]
                            )
                        )
                    else:
                        self._results.append(
                            operation.remote(
                                column={"name": column, "values": self.dataset[column]}
                            )
                        )
            except:
                pass

    def profile(self):
        return return ray.get(self._results)
