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
"""Pure request construction and input validation checks; no HTTP substitutes."""

import json

import httpx
import pytest
from soar_sdk.exceptions import ActionFailure

from src.actions.make_request import GraphMakeRequestParams, _build_request


def request(**overrides: object) -> httpx.Request:
    params = GraphMakeRequestParams(
        **{"http_method": "GET", "endpoint": "/v1.0/sites/root", **overrides}
    )
    return _build_request(params)


@pytest.mark.parametrize(
    "endpoint",
    ["/v1.0/sites/root", "v1.0/sites/root", " /v1.0/sites/root "],
)
def test_accepts_versioned_relative_paths(endpoint: str) -> None:
    assert str(request(endpoint=endpoint).url) == (
        "https://graph.microsoft.com/v1.0/sites/root"
    )


def test_accepts_beta_paths() -> None:
    assert str(request(endpoint="/beta/users").url) == (
        "https://graph.microsoft.com/beta/users"
    )


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://example.com/v1.0/sites/root",
        "http://graph.microsoft.com/v1.0/sites/root",
        "//example.com/v1.0/sites/root",
        "/sites/root",
        "/v2.0/sites/root",
        "",
        "/beta",
        "/v1.0/sites/root#fragment",
        "/v1.0/sites/root#",
        "/v1.0/\\example.com",
        "/v1.0/sites/root\r\nHost: example.com",
    ],
)
def test_rejects_absolute_unversioned_and_unsafe_paths(endpoint: str) -> None:
    with pytest.raises(ActionFailure):
        request(endpoint=endpoint)


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        (method, method.upper())
        for method in (
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "HEAD",
            "OPTIONS",
            "get",
        )
    ],
)
def test_supports_standard_methods(method: str, expected: str) -> None:
    assert request(http_method=method).method == expected


def test_rejects_unsupported_method() -> None:
    with pytest.raises(ActionFailure, match="Unsupported HTTP method"):
        request(http_method="TRACE")


@pytest.mark.parametrize("timeout", [0, -1])
def test_rejects_nonpositive_timeout(timeout: float) -> None:
    with pytest.raises(ActionFailure, match="Timeout"):
        request(timeout=timeout)


@pytest.mark.parametrize(
    "query",
    ['{"$top": 1, "$select": "id,displayName"}', "?$top=1&$select=id%2CdisplayName"],
)
def test_merges_query_parameters_with_endpoint_query(query: str) -> None:
    actual = request(endpoint="/v1.0/users?$count=true", query_parameters=query)
    assert actual.url.params == httpx.QueryParams(
        {"$count": "true", "$top": "1", "$select": "id,displayName"}
    )


@pytest.mark.parametrize("query", ["[]", "null", "1", '{"$top":'])
def test_rejects_invalid_query_shapes(query: str) -> None:
    with pytest.raises(ActionFailure, match="Query parameters"):
        request(query_parameters=query)


def test_custom_headers_are_merged_case_insensitively() -> None:
    actual = request(
        headers='{"content-type": "text/plain", "ConsistencyLevel": "eventual"}',
        body="hello",
    )
    assert actual.headers["Content-Type"] == "text/plain"
    assert actual.headers["ConsistencyLevel"] == "eventual"
    assert actual.content == b"hello"


@pytest.mark.parametrize(
    "header",
    [
        "Authorization",
        "Proxy-Authorization",
        "Host",
        "Content-Length",
        "Transfer-Encoding",
        "Connection",
    ],
)
def test_rejects_reserved_headers(header: str) -> None:
    with pytest.raises(ActionFailure, match="cannot be overridden"):
        request(headers=json.dumps({header: "not-logged"}))


@pytest.mark.parametrize(
    "headers", ["[]", '"string"', "null", '{"Accept": 1}', "{bad"]
)
def test_rejects_invalid_headers_without_echoing_input(headers: str) -> None:
    with pytest.raises(ActionFailure) as error:
        request(headers=headers)
    assert headers not in str(error.value)


@pytest.mark.parametrize(
    "body", ['{"displayName": "你好"}', "[]", "false", "0", "null", '"text"', '""']
)
def test_json_body_preserves_values_including_falsy_and_scalar(body: str) -> None:
    actual = request(http_method="POST", body=body)
    assert json.loads(actual.content) == json.loads(body)


@pytest.mark.parametrize("body", ["", "null"])
def test_empty_body_is_distinct_from_json_null(body: str) -> None:
    actual = request(body=body)
    assert actual.content == (b"null" if body == "null" else b"")


@pytest.mark.parametrize("body", ["{bad", "not-json"])
def test_rejects_invalid_json_body(body: str) -> None:
    with pytest.raises(ActionFailure, match="Body contains invalid JSON"):
        request(body=body)


def test_non_json_body_is_utf8_encoded() -> None:
    actual = request(
        headers='{"Content-Type": "text/plain; charset=utf-8"}', body="你好"
    )
    assert actual.content == "你好".encode()
