import importlib

from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.core.task.task_manager import TaskManager
from taipy.core.data.data_manager import DataManager
from taipy.core.exceptions.repository import ModelNotFound

from taipy_rest.api.schemas import TaskSchema
from taipy.core.task.task import Task
from taipy.core.common.utils import load_fct
from taipy.core.scheduler.scheduler import Scheduler

from taipy_rest.config import TAIPY_SETUP_FILE


class TaskResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a task
      description: Get a single task by ID
      parameters:
        - in: path
          name: task_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  task: TaskSchema
        404:
          description: task does not exist
    delete:
      tags:
        - api
      summary: Delete a task
      description: Delete a single task by ID
      parameters:
        - in: path
          name: task_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: task deleted
        404:
          description: task does not exist
    """

    def get(self, task_id):
        schema = TaskSchema()
        manager = TaskManager()
        task = manager.get(task_id)
        if not task:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)
        return {"task": schema.dump(manager.repository.to_model(task))}

    def delete(self, task_id):
        try:
            manager = TaskManager()
            manager.delete(task_id)
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataNode {task_id} not found"}), 404
            )

        return {"msg": f"task {task_id} deleted"}


class TaskList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of tasks
      description: Get a list of paginated tasks
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
                          $ref: '#/components/schemas/TaskSchema'
    post:
      tags:
        - api
      summary: Create a task
      description: Create a new task
      requestBody:
        content:
          application/json:
            schema:
              TaskSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: task created
                  task: TaskSchema
    """

    def __init__(self):
        spec = importlib.util.spec_from_file_location("taipy_setup", TAIPY_SETUP_FILE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def fetch_config(self, config_name):
        return getattr(self.module, config_name)

    def get(self):
        schema = TaskSchema(many=True)
        manager = TaskManager()
        tasks = manager.get_all()
        tasks_model = [manager.repository.to_model(t) for t in tasks]
        return schema.dump(tasks_model)

    def post(self):
        args = request.args
        config_name = args.get("config_name")

        schema = TaskSchema()
        manager = TaskManager()
        if not config_name:
            return {"msg": "Config name is mandatory"}, 400

        try:
            config = self.fetch_config(config_name)
            task = manager.get_or_create(config)

            return {
                "msg": "task created",
                "task": schema.dump(manager.repository.to_model(task)),
            }, 201
        except AttributeError:
            return {"msg": f"Config name {config_name} not found"}, 404

    def __create_task_from_schema(self, task_schema: TaskSchema):
        data_manager = DataManager()
        return Task(
            task_schema.get("config_name"),
            [data_manager.get(ds) for ds in task_schema.get("input_ids")],
            load_fct(
                task_schema.get("function_module"), task_schema.get("function_name")
            ),
            [data_manager.get(ds) for ds in task_schema.get("output_ids")],
            task_schema.get("parent_id"),
        )


class TaskExecutor(Resource):
    """Execute a task

    ---
    post:
      tags:
        - api
      summary: Execute a task
      description: Execute a task
      parameters:
        - in: path
          name: task_id
          schema:
            type: string
      responses:
        204:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: task created
                  task: TaskSchema
      404:
          description: task does not exist
    """

    def post(self, task_id):
        manager = TaskManager()
        task = manager.get(task_id)
        if not task:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)
        Scheduler().submit_task(task)
        return {"message": f"Executed task {task_id}"}
