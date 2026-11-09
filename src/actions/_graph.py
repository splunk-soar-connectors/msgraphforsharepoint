"""Shared Microsoft Graph request and pagination helpers."""

from __future__ import annotations

import httpx
from soar_sdk.exceptions import ActionFailure

from ..graph_response import GraphResponseError, get_graph_response


def _request_graph(client: httpx.Client, method: str, endpoint: str, **kwargs):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request_headers = kwargs.pop("headers", {})
    headers.update(request_headers)
    try:
        response = client.request(
            method, endpoint, headers=headers, follow_redirects=False, **kwargs
        )
    except httpx.RequestError as exc:
        raise ActionFailure("Error connecting to Microsoft Graph") from exc
    try:
        return get_graph_response(response)
    except GraphResponseError as exc:
        raise ActionFailure(str(exc)) from exc


def _page_contents(
    page: object,
) -> tuple[list[dict[str, object]], object]:
    """Validate the result collection in one Graph page."""
    if not isinstance(page, dict):
        raise ActionFailure("Microsoft Graph returned an invalid page")
    value = page.get("value", [])
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ActionFailure("Microsoft Graph returned an invalid page value")
    return value, page.get("@odata.nextLink")


def _next_page_link(next_link: object, seen_links: set[str]) -> str | None:
    """Validate and record the next link, rejecting repeated pagination URLs."""
    if not next_link:
        return None
    if not isinstance(next_link, str) or next_link in seen_links:
        raise ActionFailure(
            "Rejected repeated or invalid Microsoft Graph pagination URL"
        )
    seen_links.add(next_link)
    return next_link


def _paginate(
    client: httpx.Client,
    endpoint: str,
    *,
    limit: int | None = None,
    params: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    """Follow Graph pages while guarding against loops and runaway responses."""
    page_params = dict(params or {})
    page_params["$top"] = min(limit, 1000) if limit else 1000
    results: list[dict[str, object]] = []
    next_link: str | None = None
    seen_links: set[str] = set()
    for _ in range(1000):
        page = _request_graph(
            client,
            "GET",
            next_link or endpoint,
            **({} if next_link else {"params": page_params}),
        )
        value, candidate_next_link = _page_contents(page)
        results.extend(value)
        if limit is not None and len(results) >= limit:
            return results[:limit]
        next_link = _next_page_link(candidate_next_link, seen_links)
        if next_link is None:
            return results
    raise ActionFailure("Microsoft Graph pagination exceeded its safety limit")
