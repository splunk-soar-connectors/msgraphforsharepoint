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

import warnings

import pytest

from src.actions.add_item import AddItemOutput, FieldsOutput as AddItemFieldsOutput
from src.actions.get_file import GetFileSummary
from src.actions.get_list import FieldsOutput as GetListFieldsOutput
from src.actions.update_item import (
    FieldsOutput as UpdateItemFieldsOutput,
    UpdateItemOutput,
)


@pytest.mark.parametrize("output_model", [AddItemOutput, UpdateItemOutput])
def test_item_output_serialization_preserves_graph_response_keys(output_model) -> None:
    response = {
        "@odata.context": "https://graph.microsoft.com/$metadata#items/$entity",
        "@odata.etag": "item-etag",
        "contentType": {"id": "0x", "name": "Item"},
        "createdBy": {"user": {"displayName": "Creator"}},
        "createdDateTime": "2026-10-30T00:00:00Z",
        "eTag": '"item-etag"',
        "fields": {"@odata.etag": "fields-etag", "CustomColumn": "value"},
        "fields@odata.context": "https://graph.microsoft.com/$metadata#fields",
        "id": "1",
        "lastModifiedBy": {
            "application": {"displayName": "App", "id": "app-id"},
            "user": {"displayName": "Editor"},
        },
        "lastModifiedDateTime": "2026-10-30T00:00:00Z",
        "parentReference": {"id": "parent-id", "siteId": "site-id"},
        "webUrl": "https://example.sharepoint.com/items/1",
    }

    output = output_model.model_validate(response)

    assert output.model_dump(by_alias=True, exclude_none=True) == response


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

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        fields = AddItemFieldsOutput.model_validate(
            {"@odata.etag": "fields-etag", "CustomColumn": "value"}
        )
    assert not captured
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

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        fields = UpdateItemFieldsOutput.model_validate(
            {"@odata.etag": "fields-etag", "CustomColumn": "value"}
        )
    assert not captured
    assert fields.model_dump(by_alias=True, exclude_none=True) == {
        "@odata.etag": "fields-etag",
        "CustomColumn": "value",
    }


def test_get_list_accepts_lists_with_different_columns() -> None:
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        fields = GetListFieldsOutput.model_validate({"DifferentColumn": "value"})
    assert not captured
    assert fields.model_dump(exclude_none=True) == {"DifferentColumn": "value"}


def test_get_file_summary_retains_legacy_vault_id_cef_types() -> None:
    field = GetFileSummary.model_fields["vault_id"]
    assert field.json_schema_extra["cef_types"] == ["sha1", "vault id"]
