# Copyright (c) 2026 Splunk Inc.
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
"""Regression checks for legacy SharePoint output field contracts."""

from src.actions.add_item import AddItemOutput, FieldsOutput as AddItemFieldsOutput
from src.actions.get_file import GetFileSummary
from src.actions.get_list import FieldsOutput as GetListFieldsOutput
from src.actions.update_item import (
    FieldsOutput as UpdateItemFieldsOutput,
    UpdateItemOutput,
)


def test_add_item_preserves_graph_metadata_aliases_and_optional_columns() -> None:
    aliases = {
        name: AddItemOutput.model_fields[name].alias
        for name in ("odata_context", "odata_etag", "fields_odata_context")
    }
    assert aliases == {
        "odata_context": "@odata.context",
        "odata_etag": "@odata.etag",
        "fields_odata_context": "fields@odata.context",
    }
    assert AddItemFieldsOutput.model_fields["etag"].alias == "@odata.etag"

    fields = AddItemFieldsOutput.model_validate(
        {"@odata.etag": "fields-etag", "CustomColumn": "value"}
    )
    assert fields.model_dump(by_alias=True, exclude_none=True) == {
        "@odata.etag": "fields-etag",
        "CustomColumn": "value",
    }


def test_update_item_preserves_graph_metadata_aliases_and_optional_columns() -> None:
    aliases = {
        name: UpdateItemOutput.model_fields[name].alias
        for name in ("odata_context", "odata_etag", "fields_odata_context")
    }
    assert aliases == {
        "odata_context": "@odata.context",
        "odata_etag": "@odata.etag",
        "fields_odata_context": "fields@odata.context",
    }
    assert UpdateItemFieldsOutput.model_fields["etag"].alias == "@odata.etag"

    fields = UpdateItemFieldsOutput.model_validate(
        {"@odata.etag": "fields-etag", "CustomColumn": "value"}
    )
    assert fields.model_dump(by_alias=True, exclude_none=True) == {
        "@odata.etag": "fields-etag",
        "CustomColumn": "value",
    }


def test_get_list_accepts_lists_with_different_columns() -> None:
    fields = GetListFieldsOutput.model_validate({"DifferentColumn": "value"})
    assert fields.model_dump(exclude_none=True) == {"DifferentColumn": "value"}


def test_get_file_summary_retains_legacy_vault_id_cef_types() -> None:
    field = GetFileSummary.model_fields["vault_id"]
    assert field.json_schema_extra["cef_types"] == ["sha1", "vault id"]
