"""Shared path validation for Microsoft Graph action endpoints."""

import urllib.parse


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
    """Encode path components while rejecting traversal syntax."""
    stripped = str(value).strip("/")
    if not stripped:
        if allow_empty:
            return ""
        raise ValueError("Path values must not be empty")
    return "/".join(encode_path_segment(segment) for segment in stripped.split("/"))
