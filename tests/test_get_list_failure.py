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
"""Regression tests for get_list failure parameter preservation."""

import pytest

from src.actions.get_list import GetListParams
from src.app import create_msgraphforsharepoint_app
from src.asset import Asset


@pytest.mark.parametrize(
    ("site_id", "list_name", "limit", "message"),
    [
        (
            None,
            "Test List",
            10.0,
            (
                "The asset configuration parameter 'Sharepoint Site ID' is required "
                "for retrieving a list from specific site"
            ),
        ),
        (
            "site-id",
            "Test List",
            0.0,
            "Please provide non-zero positive integer in 'limit' action parameter",
        ),
        (
            "site-id",
            "invalid/list",
            10.0,
            "Invalid list ID: Path values must contain non-empty, non-traversal segments",
        ),
    ],
)
def test_registered_get_list_failure_preserves_parameters(
    site_id: str | None,
    list_name: str,
    limit: float,
    message: str,
) -> None:
    app = create_msgraphforsharepoint_app()
    action = app.get_actions()["get_list"]
    params = GetListParams(list=list_name, limit=limit)
    asset = Asset(
        tenant_id="test-tenant",
        site_id=site_id,
        client_id="test-client",
        client_secret="test-secret",
    )

    assert action(params, soar=app.soar_client, asset=asset) is False

    [action_result] = app.actions_manager.get_results()
    assert action_result.get_status() is False
    assert action_result.get_message() == message
    assert action_result.get_param() == params.model_dump(by_alias=True)
