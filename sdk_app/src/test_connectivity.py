"""Microsoft Graph connectivity check."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .client import GraphClient
from soar_sdk.exceptions import ActionFailure

if TYPE_CHECKING:
    from soar_sdk.abstract import SOARClient

    from .app import Asset


def run_test_connectivity(soar: SOARClient, asset: Asset) -> None:
    """Refresh client credentials and request the configured Graph endpoint."""
    if not asset.admin_consent:
        raise ActionFailure(
            "Admin-consent callback support is not yet migrated to the SDK webhook."
        )
    endpoint = asset.endpoint_test_connectivity or "/sites/root"
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    with GraphClient(asset) as graph:
        graph.request("GET", endpoint, force_token_refresh=True)
    soar.set_message("Test Connectivity Passed")
