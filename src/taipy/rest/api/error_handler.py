# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from flask import jsonify
from marshmallow import ValidationError

from taipy.core.exceptions.exceptions import (
    NonExistingCycle,
    NonExistingDataNode,
    NonExistingJob,
    NonExistingPipeline,
    NonExistingPipelineConfig,
    NonExistingScenario,
    NonExistingScenarioConfig,
    NonExistingTask,
    NonExistingTaskConfig,
)

from .exceptions.exceptions import ConfigIdMissingException
from .views import blueprint


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400


@blueprint.errorhandler(ConfigIdMissingException)
def handle_config_id_missing_exception(e):
    """Return json error for config id missing exception.

    This will avoid having to try/catch ConfigIdMissingException in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify({"message": e.message}), 400


@blueprint.errorhandler(NonExistingDataNode)
def handle_data_node_not_found(e):
    """Return json error for data node not found.

    This will avoid having to try/catch NotFound errors in all endpoints, returning
    correct JSON response with associated HTTP 404 Status (https://tools.ietf.org/html/rfc7231#section-6.5.4)
    """
    return jsonify({"message": str(e)}), 404
