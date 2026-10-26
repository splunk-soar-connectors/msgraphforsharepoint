"""Deterministic SDK structure and pure input-boundary checks."""

from __future__ import annotations

import httpx
import pytest
import ast
from pathlib import Path
from soar_sdk.exceptions import ActionFailure

from src.actions._limits import validate_limit
from src.actions._paths import encode_path, encode_path_segment
from src.app import create_msgraphforsharepoint_app
from src.auth import _GraphAuth
from src.consts import GRAPH_BASE_URL


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
    output_classes = []
    for source in actions_dir.glob("*.py"):
        module = ast.parse(source.read_text(encoding="utf-8"))
        for node in module.body:
            if isinstance(node, ast.ClassDef) and node.name.endswith("Output"):
                output_classes.append((source.name, node.name, node.bases))

    assert output_classes
    for source_name, class_name, bases in output_classes:
        base_names = {
            base.id for base in bases if isinstance(base, ast.Name)
        }
        assert "PermissiveActionOutput" in base_names, (
            f"{source_name}:{class_name} must preserve variable Microsoft Graph "
            "response fields with PermissiveActionOutput"
        )


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
