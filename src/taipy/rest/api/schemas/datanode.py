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

from marshmallow import Schema, fields, pre_dump


class DataNodeSchema(Schema):

    config_id = fields.String()
    scope = fields.String()
    id = fields.String()
    storage_type = fields.String()
    name = fields.String()
    parent_id = fields.String()
    last_edit_date = fields.String()
    job_ids = fields.List(fields.String)
    validity_days = fields.Float()
    validity_seconds = fields.Float()
    edit_in_progress = fields.Boolean()
    properties = fields.Dict()


class DataNodeConfigSchema(Schema):
    name = fields.String()
    storage_type = fields.String()
    scope = fields.Integer()

    @pre_dump
    def serialize_scope(self, obj, **kwargs):
        obj.scope = obj.scope.value
        return obj


class CSVDataNodeConfigSchema(DataNodeConfigSchema):
    path = fields.String()
    default_path = fields.String()
    has_header = fields.Boolean()


class InMemoryDataNodeConfigSchema(DataNodeConfigSchema):
    default_data = fields.Inferred()


class PickleDataNodeConfigSchema(DataNodeConfigSchema):
    path = fields.String()
    default_path = fields.String()
    default_data = fields.Inferred()


class SQLDataNodeConfigSchema(DataNodeConfigSchema):
    db_username = fields.String()
    db_password = fields.String()
    db_name = fields.String()
    db_engine = fields.String()
    read_query = fields.String()
    write_table = fields.String()


class MongoCollectionDataNodeConfigSchema(DataNodeConfigSchema):
    db_username = fields.String()
    db_password = fields.String()
    db_name = fields.String()
    collection_name = fields.String()


class ExcelDataNodeConfigSchema(DataNodeConfigSchema):
    path = fields.String()
    default_path = fields.String()
    has_header = fields.Boolean()
    sheet_name = fields.String()


class GenericDataNodeConfigSchema(DataNodeConfigSchema):
    pass


class JSONDataNodeConfigSchema(DataNodeConfigSchema):
    path = fields.String()
    default_path = fields.String()


class OperatorSchema(Schema):
    key = fields.String()
    value = fields.Inferred()
    operator = fields.String()


class DataNodeFilterSchema(DataNodeConfigSchema):
    operators = fields.List(fields.Nested(OperatorSchema))
    join_operator = fields.String(default="AND")
