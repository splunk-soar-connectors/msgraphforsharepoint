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
"""Registered action failure results retain their submitted parameters."""

import pytest
from soar_sdk.params import Params

from src.actions.add_item import AddItemParams
from src.actions.copy_drive_item import CopyDriveItemParams
from src.actions.create_folder import CreateFolderParams
from src.actions.drive_children import ListDriveChildrenParams
from src.actions.drives import ListDrivesParams
from src.actions.folder_items import ListFolderItemsParams
from src.actions.get_file import GetFileParams
from src.actions.list_lists import ListListsParams
from src.actions.make_request import GraphMakeRequestParams
from src.actions.remove_file import RemoveFileParams
from src.actions.remove_folder import RemoveFolderParams
from src.actions.sites import ListSitesParams
from src.actions.update_item import UpdateItemParams
from src.app import create_msgraphforsharepoint_app
from src.asset import Asset


@pytest.mark.parametrize(
    ("action_name", "params", "site_id", "message"),
    [
        (
            "list_sites",
            ListSitesParams(limit=0),
            "site-id",
            "Please provide non-zero positive integer in 'limit' action parameter",
        ),
        (
            "list_drives",
            ListDrivesParams(limit=None),
            None,
            "The asset configuration parameter 'Sharepoint Site ID' is required ",
        ),
        (
            "list_lists",
            ListListsParams(limit=None),
            None,
            "The asset configuration parameter 'Sharepoint Site ID' is required ",
        ),
        (
            "list_folder_items",
            ListFolderItemsParams(folder_path="/"),
            None,
            "The asset configuration parameter 'Sharepoint Site ID' is required ",
        ),
        (
            "list_drive_children",
            ListDriveChildrenParams(drive_id="bad/id"),
            "site-id",
            "Invalid drive ID:",
        ),
        (
            "add_item",
            AddItemParams(list="bad/id", item="{}"),
            "site-id",
            "Invalid list ID:",
        ),
        (
            "create_folder",
            CreateFolderParams(
                parent_item_id="bad/id", folder_name="test", drive_id=None
            ),
            "site-id",
            "Invalid parent item ID:",
        ),
        (
            "update_item",
            UpdateItemParams(list="bad/id", item_id=1, item="{}"),
            "site-id",
            "Invalid list or item ID:",
        ),
        (
            "copy_drive_item",
            CopyDriveItemParams(
                source_item_id="bad/id",
                source_drive_id=None,
                dest_drive_id=None,
                dest_folder_id="folder-id",
                file_name=None,
            ),
            "site-id",
            "Invalid source item ID:",
        ),
        (
            "get_file",
            GetFileParams(file_name="report.csv", file_path="/", drive_id=None),
            None,
            "The asset configuration parameter 'Sharepoint Site ID' is required ",
        ),
        (
            "remove_file",
            RemoveFileParams(file_name="report.csv", file_path="/", drive_id=None),
            None,
            "The asset configuration parameter 'Sharepoint Site ID' is required ",
        ),
        (
            "remove_folder",
            RemoveFolderParams(folder_path="/", drive_id=None),
            None,
            "The asset configuration parameter 'Sharepoint Site ID' is required ",
        ),
        (
            "make_request",
            GraphMakeRequestParams(
                http_method="GET", endpoint="https://example.com/v1.0/sites"
            ),
            "site-id",
            "Endpoint must be a relative Microsoft Graph path",
        ),
    ],
)
def test_registered_action_failures_preserve_parameters(
    action_name: str, params: Params, site_id: str | None, message: str
) -> None:
    app = create_msgraphforsharepoint_app()
    action = app.get_actions()[action_name]
    asset = Asset(
        tenant_id="test-tenant",
        site_id=site_id,
        client_id="test-client",
        client_secret="test-secret",
    )

    assert action(params, soar=app.soar_client, asset=asset) is False

    [action_result] = app.actions_manager.get_results()
    assert action_result.get_status() is False
    assert message in action_result.get_message()
    assert action_result.get_param() == params.model_dump(by_alias=True)
