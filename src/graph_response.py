"""Microsoft Graph response parsing without action or transport orchestration."""

from __future__ import annotations

import json
import math
from typing import Any

import httpx


class GraphResponseError(RuntimeError):
    """An unsuccessful or malformed response from Microsoft Graph."""


def _sanitize_non_finite(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: _sanitize_non_finite(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_sanitize_non_finite(value) for value in data]
    if isinstance(data, float) and not math.isfinite(data):
        return None
    return data


def get_graph_response(response: httpx.Response, *, allow_empty: bool = True) -> Any:
    """Parse a Graph response, preserving the connector's accepted 2xx/3xx range."""
    successful = 200 <= response.status_code < 399
    if allow_empty and not response.content and successful:
        return {}

    try:
        payload = json.loads(response.text, parse_constant=lambda _value: None)
    except (json.JSONDecodeError, TypeError) as error:
        if successful:
            raise GraphResponseError(
                "Unable to parse Microsoft Graph response JSON"
            ) from error
        raise GraphResponseError(_error_message(response, None)) from error

    if not successful:
        raise GraphResponseError(_error_message(response, payload))
    return _sanitize_non_finite(payload)


def _error_message(response: httpx.Response, payload: Any) -> str:
    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    if isinstance(error, dict):
        code = error.get("code")
        message = error.get("message") or payload.get("error_description")
        if code:
            message = f"{code}. {message or ''}".strip()
        if message:
            return (
                "Error from server. Status Code: "
                f"{response.status_code} Data from server: {message}"
            )
    return (
        "Error from server. Status Code: "
        f"{response.status_code} Data from server: {response.text}"
    )
