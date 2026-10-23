"""Microsoft Graph authentication using SDK-managed asset state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.auth.flows import ClientCredentialsFlow

if TYPE_CHECKING:
    from .app import Asset


GRAPH_SCOPE = "https://graph.microsoft.com/.default"
TOKEN_ENDPOINT = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"


def create_auth_flow(asset: Asset) -> ClientCredentialsFlow:
    """Build the app's client-credentials flow over encrypted SDK asset state."""
    return ClientCredentialsFlow(
        asset.auth_state,
        client_id=asset.client_id,
        client_secret=asset.client_secret,
        token_endpoint=TOKEN_ENDPOINT.format(tenant_id=asset.tenant_id),
        scope=GRAPH_SCOPE,
    )
