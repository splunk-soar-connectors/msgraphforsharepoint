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
"""Deterministic contract checks for shared Graph pagination."""

import pytest
from soar_sdk.exceptions import ActionFailure

from src.actions._graph import _next_page_link, _page_contents


def test_page_contents_returns_values_and_tracks_next_link() -> None:
    seen_links: set[str] = set()
    values, candidate_next_link = _page_contents(
        {
            "value": [{"id": "first"}],
            "@odata.nextLink": "https://graph.microsoft.com/v1.0/sites?$skiptoken=next",
        }
    )
    next_link = _next_page_link(candidate_next_link, seen_links)

    assert values == [{"id": "first"}]
    assert next_link == ("https://graph.microsoft.com/v1.0/sites?$skiptoken=next")
    assert seen_links == {next_link}


@pytest.mark.parametrize("page", [None, [], "invalid"])
def test_page_contents_rejects_non_object_pages(page: object) -> None:
    with pytest.raises(ActionFailure, match="invalid page"):
        _page_contents(page)


@pytest.mark.parametrize("value", [None, {}, ["not an object"]])
def test_page_contents_rejects_invalid_value_collections(value: object) -> None:
    with pytest.raises(ActionFailure, match="invalid page value"):
        _page_contents({"value": value})


def test_page_contents_rejects_repeated_next_links() -> None:
    seen_links = {"https://graph.microsoft.com/v1.0/sites?$skiptoken=repeat"}

    with pytest.raises(ActionFailure, match="repeated or invalid"):
        _next_page_link(
            "https://graph.microsoft.com/v1.0/sites?$skiptoken=repeat", seen_links
        )


def test_page_contents_accepts_a_final_page_without_next_link() -> None:
    assert _page_contents({"value": [{"id": "last"}]}) == ([{"id": "last"}], None)
    assert _next_page_link(None, set()) is None
