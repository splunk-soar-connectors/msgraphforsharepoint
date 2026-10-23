"""Microsoft Graph transport and response handling."""

from __future__ import annotations

import json
import math
import urllib.parse
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import httpx
from soar_sdk.exceptions import ActionFailure

from .auth import create_auth_flow

if TYPE_CHECKING:
    from .app import Asset


GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
REQUEST_TIMEOUT = 30.0
MAX_PAGINATION_PAGES = 1000


def encode_path_segment(value: str) -> str:
    """Encode one user-controlled Graph path segment and reject traversal."""
    decoded = str(value)
    for _ in range(5):
        unquoted = urllib.parse.unquote(decoded)
        if unquoted == decoded:
            break
        decoded = unquoted
    if decoded in {"", ".", ".."} or any(char in decoded for char in "/\\?#%"):
        raise ValueError("Path values must contain non-empty, non-traversal segments")
    if any(ord(char) < 32 for char in decoded):
        raise ValueError("Path values must not contain control characters")
    return urllib.parse.quote(decoded, safe="")


def encode_path(value: str, *, allow_empty: bool = False) -> str:
    """Encode each logical path component while rejecting traversal syntax."""
    stripped = str(value).strip("/")
    if not stripped:
        if allow_empty:
            return ""
        raise ValueError("Path values must not be empty")
    return "/".join(encode_path_segment(segment) for segment in stripped.split("/"))


def _sanitize_non_finite(data: Any) -> Any:  # noqa: ANN401
    if isinstance(data, dict):
        return {key: _sanitize_non_finite(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_sanitize_non_finite(value) for value in data]
    if isinstance(data, float) and not math.isfinite(data):
        return None
    return data


class GraphClient:
    """Small connector-specific Graph client with SDK-managed token state."""

    def __init__(self, asset: Asset) -> None:
        self._asset = asset
        self._auth_flow = create_auth_flow(asset)
        self._http = httpx.Client(timeout=REQUEST_TIMEOUT, verify=True)

    def __enter__(self) -> GraphClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self._http.close()

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: str | bytes | None = None,
        json_body: Any = None,  # noqa: ANN401
        force_token_refresh: bool = False,
    ) -> Any:  # noqa: ANN401
        url = (
            endpoint
            if endpoint.startswith("https://")
            else f"{GRAPH_BASE_URL}{endpoint}"
        )
        parsed_url = urllib.parse.urlsplit(url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname != "graph.microsoft.com"
            or parsed_url.port is not None
            or parsed_url.username
            or parsed_url.password
        ):
            raise ActionFailure("Rejected request URL outside Microsoft Graph")
        token = self._auth_flow.authenticate() if force_token_refresh else self._auth_flow.get_token()
        for attempt in range(2):
            try:
                response = self._http.request(
                    method,
                    url,
                    headers={
                        "Authorization": f"Bearer {token.access_token}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    params=params,
                    content=data,
                    json=json_body,
                )
            except httpx.RequestError as exc:
                raise ActionFailure("Error connecting to Microsoft Graph") from exc

            if response.status_code == 401 and attempt == 0:
                token = self._auth_flow.authenticate()
                continue
            break

        if not 200 <= response.status_code < 399:
            message = self._error_message(response)
            raise ActionFailure(message)
        if not response.content:
            return {}
        try:
            return _sanitize_non_finite(json.loads(response.text, parse_constant=lambda _value: None))
        except (json.JSONDecodeError, TypeError) as exc:
            raise ActionFailure(f"Unable to parse Microsoft Graph response JSON: {exc}") from exc

    def download_to_file(self, endpoint: str, destination: str) -> None:
        """Stream Graph file content to disk, following its content redirect."""
        url = endpoint if endpoint.startswith("https://") else f"{GRAPH_BASE_URL}{endpoint}"
        parsed_url = urllib.parse.urlsplit(url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname != "graph.microsoft.com"
            or parsed_url.port is not None
            or parsed_url.username
            or parsed_url.password
        ):
            raise ActionFailure("Rejected request URL outside Microsoft Graph")

        token = self._auth_flow.get_token()
        for attempt in range(2):
            try:
                with self._http.stream(
                    "GET",
                    url,
                    headers={
                        "Authorization": f"Bearer {token.access_token}",
                        "Accept": "application/json",
                    },
                    follow_redirects=True,
                ) as response:
                    if response.status_code == 401 and attempt == 0:
                        token = self._auth_flow.authenticate()
                        continue
                    if not 200 <= response.status_code < 399:
                        response.read()
                        raise ActionFailure(self._error_message(response))
                    with open(destination, "wb") as output:
                        for chunk in response.iter_bytes(chunk_size=10 * 1024 * 1024):
                            output.write(chunk)
                return
            except httpx.RequestError as exc:
                raise ActionFailure("Error connecting to Microsoft Graph") from exc

    @staticmethod
    def _error_message(response: httpx.Response) -> str:
        try:
            body = json.loads(response.text)
        except (json.JSONDecodeError, TypeError):
            body = None
        error = body.get("error", {}) if isinstance(body, dict) else {}
        if isinstance(error, dict):
            code = error.get("code")
            message = error.get("message") or body.get("error_description")
            if code:
                message = f"{code}. {message or ''}".strip()
            if message:
                return f"Error from server. Status Code: {response.status_code} Data from server: {message}"
        return f"Error from server. Status Code: {response.status_code} Data from server: {response.text}"

    def paginate(
        self,
        endpoint: str,
        *,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        page_params = dict(params or {})
        page_params["$top"] = min(limit, 1000) if limit else 1000
        items: list[dict[str, Any]] = []
        next_link: str | None = None
        seen_links: set[str] = set()
        for _ in range(MAX_PAGINATION_PAGES):
            page = self.request("GET", next_link or endpoint, params=None if next_link else page_params)
            items.extend(page.get("value", []))
            if limit is not None and len(items) >= limit:
                return items[:limit]
            next_link = page.get("@odata.nextLink")
            if not next_link:
                return items
            parsed = urllib.parse.urlsplit(next_link)
            if (
                parsed.scheme != "https"
                or parsed.hostname != "graph.microsoft.com"
                or parsed.port is not None
                or parsed.username
                or parsed.password
            ):
                raise ActionFailure("Rejected pagination URL outside Microsoft Graph")
            if next_link in seen_links:
                raise ActionFailure("Rejected repeated Microsoft Graph pagination URL")
            seen_links.add(next_link)
        raise ActionFailure("Microsoft Graph pagination exceeded its safety limit")


def validate_limit(value: float | None) -> int | None:
    if value is None:
        return None
    if not float(value).is_integer():
        raise ActionFailure("Please provide a valid integer value in the 'limit' action parameter")
    limit = int(value)
    if limit < 0:
        raise ActionFailure("Please provide a valid non-zero positive integer in the 'limit' action parameter")
    if limit == 0:
        raise ActionFailure("Please provide non-zero positive integer in 'limit' action parameter")
    return limit
