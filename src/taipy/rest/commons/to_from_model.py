# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from taipy.core.cycle._cycle_converter import _CycleConverter
from taipy.core.data._data_converter import _DataNodeConverter
from taipy.core.pipeline._pipeline_converter import _PipelineConverter
from taipy.core.scenario._scenario_converter import _ScenarioConverter
from taipy.core.task._task_converter import _TaskConverter

entity_to_models = {
    "scenario": _ScenarioConverter._entity_to_model,
    "pipeline": _PipelineConverter._entity_to_model,
    "task": _TaskConverter._entity_to_model,
    "data": _DataNodeConverter._entity_to_model,
    "cycle": _CycleConverter._entity_to_model,
}

# TODO: correctly get _to_model function (converter) from taipy-core


def _to_model(repository, entity, **kwargs):
    return entity_to_models[repository](entity)
