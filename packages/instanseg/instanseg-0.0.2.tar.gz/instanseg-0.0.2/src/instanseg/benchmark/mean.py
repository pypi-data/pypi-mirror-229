# Copyright (c) 2023, Pavel Mokeev, Dmitrii Iarosh, Anastasiia Kornilova
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy as np

from typing import Any, Callable
from nptyping import NDArray

import instanseg.metrics.constants
from instanseg.utils.metrics_utils import (
    __group_indices_by_labels,
    __statistics_functions,
)


def __mean(
    pred_labels: NDArray[Any, np.int32],
    gt_labels: NDArray[Any, np.int32],
    metric: Callable[
        [NDArray[Any, np.int32], NDArray[Any, np.int32]],
        np.float64,
    ],
    tp_condition: str,
) -> float:
    instance_predicted_dict = __group_indices_by_labels(pred_labels)
    instance_gt_dict = __group_indices_by_labels(gt_labels)
    if instanseg.metrics.constants.UNSEGMENTED_LABEL in instance_predicted_dict:
        del instance_predicted_dict[instanseg.metrics.constants.UNSEGMENTED_LABEL]
    if instanseg.metrics.constants.UNSEGMENTED_LABEL in instance_gt_dict:
        del instance_gt_dict[instanseg.metrics.constants.UNSEGMENTED_LABEL]
    mean_array = []

    tp_condition_function = __statistics_functions[tp_condition]

    for label_index, label in enumerate(instance_predicted_dict.keys()):
        for gt_label in instance_gt_dict.keys():
            is_overlap = tp_condition_function(
                instance_predicted_dict[label], instance_gt_dict[gt_label]
            )
            if is_overlap:
                metric_value = metric(
                    instance_predicted_dict[label], instance_gt_dict[gt_label]
                )
                mean_array.append(metric_value)
                break

    return np.array(mean_array).mean() if len(mean_array) != 0 else 0.0
