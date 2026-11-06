"""Microsoft Graph authentication and HTTP client construction."""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import httpx
from soar_sdk.auth.flows import ClientCredentialsFlow
from soar_sdk.auth.models import OAuthToken
from soar_sdk.exceptions import ActionFailure

from .asset import Asset
from .consts import GRAPH_BASE_URL

if TYPE_CHECKING:
    from soar_sdk.auth.flows import ClientCredentialsFlow


GRAPH_SCOPE = "https://graph.microsoft.com/.default"
TOKEN_ENDPOINT = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"  # noqa: S105
REQUEST_TIMEOUT = 30.0


def create_auth_flow(asset: Asset) -> ClientCredentialsFlow:
    """Build the app's client-credentials flow over encrypted SDK asset state."""
    return ClientCredentialsFlow(
        asset.auth_state,
        client_id=asset.client_id,
        client_secret=asset.client_secret,
        token_endpoint=TOKEN_ENDPOINT.format(tenant_id=asset.tenant_id),
        scope=GRAPH_SCOPE,
    )


class _GraphAuth(httpx.Auth):
    """Attach SDK-managed tokens and retry once after an authentication failure."""

    def __init__(self, flow: ClientCredentialsFlow) -> None:
        self._flow = flow

    @staticmethod
    def _validate_request_url(request: httpx.Request) -> None:
        url = request.url
        if (
            url.scheme != "https"
            or url.host != "graph.microsoft.com"
            or url.port not in (None, 443)
            or url.username
            or url.password
        ):
            raise ActionFailure("Rejected request URL outside Microsoft Graph")

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response]:
        self._validate_request_url(request)
        token: OAuthToken = self._flow.get_token()
        request.headers["Authorization"] = f"Bearer {token.access_token}"
        response = yield request
        if response.status_code == 401:
            token = self._flow.authenticate()
            request.headers["Authorization"] = f"Bearer {token.access_token}"
            yield request


def get_graph_client(
    asset: Asset,
    *,
    verify: bool = True,
    force_token_refresh: bool = False,
) -> httpx.Client:
    """Return an authenticated HTTPX client scoped to Microsoft Graph."""
    flow = create_auth_flow(asset)
    if force_token_refresh:
        flow.authenticate()
    return httpx.Client(
        base_url=GRAPH_BASE_URL,
        auth=_GraphAuth(flow),
        timeout=REQUEST_TIMEOUT,
        verify=verify,
    )
