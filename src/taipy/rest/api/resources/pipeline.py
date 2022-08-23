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


from flask import request
from flask_restful import Resource

from taipy.config.config import Config
from taipy.core.exceptions.exceptions import NonExistingPipeline, NonExistingPipelineConfig
from taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory

from ...commons.to_from_model import _to_model
from ..exceptions.exceptions import ConfigIdMissingException
from ..middlewares._middleware import _middleware
from ..schemas import PipelineResponseSchema


def _get_or_raise(pipeline_id: str):
    manager = _PipelineManagerFactory._build_manager()
    pipeline = manager._get(pipeline_id)
    if pipeline is None:
        raise NonExistingPipeline(pipeline_id)
    return pipeline


REPOSITORY = "pipeline"


class PipelineResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a pipeline.
      description: |
        Return a single pipeline by pipeline_id. If the pipeline does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires _TAIPY_READER_ role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/pipelines/PIPELINE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: pipeline_id
          schema:
            type: string
          description: The identifier of the pipeline.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  pipeline: PipelineSchema
        404:
          description: No pipeline has the *pipeline_id* identifier.
    delete:
      tags:
        - api
      summary: Delete a pipeline.
      description: |
        Delete a pipeline. If the pipeline does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires _TAIPY_EDITOR_ role.

        Code example:

        ```shell
          curl -X DELETE http://localhost:5000/api/v1/pipelines/PIPELINE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: pipeline_id
          schema:
            type: string
          description: The identifier of the pipeline.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Status message.
        404:
          description: No pipeline has the *pipeline_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, pipeline_id):
        schema = PipelineResponseSchema()
        pipeline = _get_or_raise(pipeline_id)
        return {"pipeline": schema.dump(_to_model(REPOSITORY, pipeline))}

    @_middleware
    def delete(self, pipeline_id):
        manager = _PipelineManagerFactory._build_manager()
        _get_or_raise(pipeline_id)
        manager._delete(pipeline_id)
        return {"message": f"Pipeline {pipeline_id} was deleted."}


class PipelineList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get all pipelines.
      description: |
        Return an array of all pipelines.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires _TAIPY_READER_ role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/pipelines
        ```

      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/PipelineSchema'
    post:
      tags:
        - api
      summary: Create a pipeline.
      description: |
        Create a pipeline from its config_id. If the config does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires _TAIPY_EDITOR_ role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/pipelines?config_id=my_pipeline_config
        ```

      parameters:
        - in: query
          name: config_id
          schema:
            type: string
          description: The identifier of the pipeline configuration.
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Status message.
                  pipeline: PipelineSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        config = Config.pipelines.get(config_id)
        if not config:
            raise NonExistingPipelineConfig(config_id)
        return config

    @_middleware
    def get(self):
        schema = PipelineResponseSchema(many=True)
        manager = _PipelineManagerFactory._build_manager()
        pipelines = [_to_model(REPOSITORY, pipeline) for pipeline in manager._get_all()]
        return schema.dump(pipelines)

    @_middleware
    def post(self):
        args = request.args
        config_id = args.get("config_id")

        response_schema = PipelineResponseSchema()
        manager = _PipelineManagerFactory._build_manager()
        if not config_id:
            raise ConfigIdMissingException

        config = self.fetch_config(config_id)
        pipeline = manager._get_or_create(config)

        return {
            "message": "Pipeline was created.",
            "pipeline": response_schema.dump(_to_model(REPOSITORY, pipeline)),
        }, 201


class PipelineExecutor(Resource):
    """Execute a pipeline

    ---
    post:
      tags:
        - api
      summary: Execute a pipeline.
      description: |
        Execute a pipeline from pipeline_id. If the pipeline does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), This endpoint requires _TAIPY_EXECUTOR_ role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/pipelines/submit/PIPELINE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: pipeline_id
          schema:
            type: string
      responses:
        204:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Status message.
                  pipeline: PipelineSchema
        404:
            description: No pipeline has the *pipeline_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def post(self, pipeline_id):
        _get_or_raise(pipeline_id)
        manager = _PipelineManagerFactory._build_manager()
        manager._submit(pipeline_id)
        return {"message": f"Pipeline {pipeline_id} was submitted."}
