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
"""Microsoft Graph authentication and HTTP client construction."""

from __future__ import annotations

from collections.abc import Generator

import httpx
from soar_sdk.auth import (
    AuthorizationCodeFlow,
    ClientCredentialsFlow,
    OAuthBearerAuth,
    OAuthConfig,
    SOARAssetOAuthClient,
)
from soar_sdk.auth.models import OAuthToken
from soar_sdk.exceptions import ActionFailure

from .asset import Asset
from .consts import (
    AUTH_METHOD_CLIENT_CREDENTIALS,
    AUTH_METHOD_DELEGATED,
    DELEGATED_GRAPH_SCOPES,
    GRAPH_BASE_URL,
    REDIRECT_URI_STATE_KEY,
)


GRAPH_SCOPE = "https://graph.microsoft.com/.default"
LOGIN_BASE_URL = "https://login.microsoftonline.com"
TOKEN_ENDPOINT = f"{LOGIN_BASE_URL}/{{tenant_id}}/oauth2/v2.0/token"
AUTHORIZATION_ENDPOINT = f"{LOGIN_BASE_URL}/{{tenant_id}}/oauth2/v2.0/authorize"
REQUEST_TIMEOUT = 30.0


def is_client_credentials_auth(asset: Asset) -> bool:
    """Default older assets to client credentials so existing configurations keep working."""
    auth_method = (asset.auth_method or AUTH_METHOD_CLIENT_CREDENTIALS).strip()
    if auth_method == AUTH_METHOD_DELEGATED:
        return False
    if auth_method == AUTH_METHOD_CLIENT_CREDENTIALS:
        return True
    raise ActionFailure("Unsupported authentication method")


def create_auth_flow(asset: Asset) -> ClientCredentialsFlow:
    """Build the app's client-credentials flow over encrypted SDK asset state."""
    return ClientCredentialsFlow(
        asset.auth_state,
        client_id=asset.client_id,
        client_secret=asset.client_secret,
        token_endpoint=TOKEN_ENDPOINT.format(tenant_id=asset.tenant_id),
        scope=GRAPH_SCOPE,
    )


def create_delegated_auth_flow(
    asset: Asset, asset_id: str, redirect_uri: str
) -> AuthorizationCodeFlow:
    """Build the SDK-managed delegated authorization-code flow."""
    return AuthorizationCodeFlow(
        asset.auth_state,
        asset_id,
        client_id=asset.client_id,
        client_secret=asset.client_secret,
        authorization_endpoint=AUTHORIZATION_ENDPOINT.format(tenant_id=asset.tenant_id),
        token_endpoint=TOKEN_ENDPOINT.format(tenant_id=asset.tenant_id),
        redirect_uri=redirect_uri,
        scope=DELEGATED_GRAPH_SCOPES,
        use_pkce=False,
        extra_token_params={"scope": " ".join(DELEGATED_GRAPH_SCOPES)},
    )


def get_oauth_client(asset: Asset) -> SOARAssetOAuthClient:
    """Create the SDK OAuth client used to validate and store callback codes."""
    return SOARAssetOAuthClient(
        OAuthConfig(
            client_id=asset.client_id,
            client_secret=asset.client_secret,
            token_endpoint=TOKEN_ENDPOINT.format(tenant_id=asset.tenant_id),
            redirect_uri=asset.auth_state.get(REDIRECT_URI_STATE_KEY, ""),
            scope=DELEGATED_GRAPH_SCOPES,
        ),
        asset.auth_state,
    )


class _ClientCredentialsAuth(httpx.Auth):
    """Attach client-credentials tokens and retry once after an auth failure."""

    def __init__(self, flow: ClientCredentialsFlow) -> None:
        self._flow = flow

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response]:
        token: OAuthToken = self._flow.get_token()
        request.headers["Authorization"] = f"Bearer {token.access_token}"
        response = yield request
        if response.status_code == 401:
            token = self._flow.authenticate()
            request.headers["Authorization"] = f"Bearer {token.access_token}"
            yield request


class _GraphAuth(httpx.Auth):
    """Restrict authenticated requests to Microsoft Graph before adding tokens."""

    def __init__(self, auth: httpx.Auth) -> None:
        self._auth = auth
        self.requires_response_body = getattr(auth, "requires_response_body", False)

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
        yield from self._auth.auth_flow(request)


def get_graph_client(
    asset: Asset,
    asset_id: str,
    *,
    verify: bool = True,
    force_token_refresh: bool = False,
) -> httpx.Client:
    """Return a Microsoft Graph client using the asset's selected auth method."""
    if is_client_credentials_auth(asset):
        flow = create_auth_flow(asset)
        if force_token_refresh:
            flow.authenticate()
        auth: httpx.Auth = _ClientCredentialsAuth(flow)
    else:
        redirect_uri = asset.auth_state.get(REDIRECT_URI_STATE_KEY)
        if not redirect_uri:
            raise ActionFailure(
                "Run test connectivity to authorize delegated authentication"
            )
        flow = create_delegated_auth_flow(asset, asset_id, redirect_uri)
        auth = OAuthBearerAuth(flow.client)

    return httpx.Client(
        base_url=GRAPH_BASE_URL,
        auth=_GraphAuth(auth),
        timeout=REQUEST_TIMEOUT,
        verify=verify,
    )
