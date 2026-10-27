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
"""Deterministic SDK structure and pure input-boundary checks."""

from __future__ import annotations

import ast
from pathlib import Path

import httpx
import pytest
from soar_sdk.exceptions import ActionFailure

from src.actions._limits import validate_limit
from src.actions._paths import encode_path, encode_path_segment
from src.app import create_msgraphforsharepoint_app
from src.auth import _GraphAuth
from src.consts import GRAPH_BASE_URL


def _inherits_permissive(
    class_name: str,
    class_bases: dict[str, set[str]],
    ancestors: set[str] | None = None,
) -> bool:
    ancestors = ancestors or set()
    if class_name in ancestors:
        return False
    bases = class_bases.get(class_name, set())
    return "PermissiveActionOutput" in bases or any(
        _inherits_permissive(base, class_bases, ancestors | {class_name})
        for base in bases
    )


def test_application_registers_all_connector_actions() -> None:
    app = create_msgraphforsharepoint_app()
    expected = {
        "copy_drive_item",
        "create_folder",
        "list_folder_items",
        "list_drives",
        "list_drive_children",
        "list_sites",
        "list_lists",
        "get_list",
        "add_item",
        "update_item",
        "get_file",
        "remove_file",
        "remove_folder",
        "make_request",
        "test_connectivity",
    }

    assert set(app.actions_manager.get_actions()) == expected


def test_action_models_precede_action_code() -> None:
    actions_dir = Path(__file__).resolve().parents[1] / "src" / "actions"
    for source in actions_dir.glob("*.py"):
        if source.name == "__init__.py":
            continue
        module = ast.parse(source.read_text(encoding="utf-8"))
        classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
        functions = [
            node
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        if classes and functions:
            assert max(node.lineno for node in classes) < min(
                node.lineno for node in functions
            ), source.name


def test_graph_response_output_models_are_permissive() -> None:
    actions_dir = Path(__file__).resolve().parents[1] / "src" / "actions"
    checked_classes = 0
    for source in actions_dir.glob("*.py"):
        module = ast.parse(source.read_text(encoding="utf-8"))
        class_bases: dict[str, set[str]] = {}
        for node in module.body:
            if isinstance(node, ast.ClassDef) and node.name.endswith("Output"):
                class_bases[node.name] = {
                    base.id for base in node.bases if isinstance(base, ast.Name)
                }

        for class_name in class_bases:
            assert _inherits_permissive(class_name, class_bases), (
                f"{source.name}:{class_name} must preserve variable Microsoft Graph "
                "response fields with PermissiveActionOutput"
            )
            checked_classes += 1

    assert checked_classes


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Asset List", "Asset%20List"),
        ("name+value", "name%2Bvalue"),
    ],
)
def test_graph_path_segment_encoding(value: str, expected: str) -> None:
    assert encode_path_segment(value) == expected


@pytest.mark.parametrize("value", ["", ".", "..", "%2e%2e", "a/b", "a?b", "a\\b"])
def test_graph_path_segment_rejects_traversal_syntax(value: str) -> None:
    with pytest.raises(ValueError, match="Path values"):
        encode_path_segment(value)


def test_graph_path_encodes_each_component() -> None:
    assert encode_path("Shared Documents/Quarter 1") == "Shared%20Documents/Quarter%201"
    assert encode_path("/", allow_empty=True) == ""


@pytest.mark.parametrize(
    ("value", "expected"), [(None, None), (1.0, 1), (1000.0, 1000)]
)
def test_limit_accepts_none_and_integral_values(
    value: float | None, expected: int | None
) -> None:
    assert validate_limit(value) == expected


@pytest.mark.parametrize("value", [0, -1, 1.5])
def test_limit_rejects_nonpositive_or_fractional_values(value: float) -> None:
    with pytest.raises(ValueError, match=r"integer|positive"):
        validate_limit(value)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/v1.0/sites",
        "http://graph.microsoft.com/v1.0/sites",
        "https://graph.microsoft.com:444/v1.0/sites",
        "https://user@graph.microsoft.com/v1.0/sites",
    ],
)
def test_auth_boundary_rejects_urls_outside_graph(url: str) -> None:
    with pytest.raises(ActionFailure, match="outside Microsoft Graph"):
        _GraphAuth._validate_request_url(httpx.Request("GET", url))


def test_auth_boundary_accepts_graph_origin() -> None:
    _GraphAuth._validate_request_url(httpx.Request("GET", f"{GRAPH_BASE_URL}/sites"))


def test_action_path_stays_under_graph_api_version() -> None:
    with httpx.Client(base_url=GRAPH_BASE_URL) as client:
        request = client.build_request("GET", "/sites")

    assert str(request.url) == f"{GRAPH_BASE_URL}/sites"
