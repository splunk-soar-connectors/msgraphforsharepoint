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
"""Microsoft Graph connectivity check."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import httpx
from soar_sdk.auth import OAuthClientError
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger

from .auth import (
    create_delegated_auth_flow,
    get_graph_client,
    is_client_credentials_auth,
)
from .consts import (
    AUTHORIZATION_ERROR_STATE_KEY,
    AUTHORIZATION_URL_STATE_KEY,
    REDIRECT_URI_STATE_KEY,
)
from .graph_response import GraphResponseError, get_graph_response

if TYPE_CHECKING:
    from soar_sdk.abstract import SOARClient

    from .asset import Asset


ADMIN_CONSENT_STATE_KEY = "msgraphforsharepoint_admin_consent_result"
logger = getLogger()


def run_test_connectivity(
    soar: SOARClient,
    asset: Asset,
    *,
    consent_callback_url: str,
    oauth_callback_url: str,
    oauth_start_url: str,
) -> None:
    """Verify the configured SharePoint Graph endpoint using the selected flow."""
    if is_client_credentials_auth(asset):
        _run_client_credentials_test(soar, asset, consent_callback_url)
    else:
        _run_delegated_test(soar, asset, oauth_callback_url, oauth_start_url)

    endpoint = asset.endpoint_test_connectivity or "/sites/root"
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    try:
        with get_graph_client(
            asset,
            str(soar.get_asset_id()),
            force_token_refresh=is_client_credentials_auth(asset),
        ) as graph:
            response = graph.get(endpoint)
            get_graph_response(response)
    except GraphResponseError as exc:
        raise ActionFailure(str(exc)) from exc
    except httpx.RequestError as exc:
        raise ActionFailure("Error connecting to Microsoft Graph") from exc
    soar.set_message("Test Connectivity Passed")


def _run_client_credentials_test(
    soar: SOARClient, asset: Asset, consent_callback_url: str
) -> None:
    """Preserve the existing admin-consent and app-only token setup."""
    if asset.admin_consent:
        return

    redirect_uri = consent_callback_url
    logger.progress("Getting App REST endpoint URL")
    logger.progress("Using OAuth Redirect URL as:")
    logger.progress(redirect_uri)
    consent_url = (
        f"https://login.microsoftonline.com/{asset.tenant_id}/adminconsent?"
        + urlencode(
            {
                "client_id": asset.client_id,
                "redirect_uri": redirect_uri,
                "state": soar.get_asset_id(),
            }
        )
    )
    logger.progress(
        "Please connect to the following URL from a different tab to continue the connectivity process"
    )
    logger.progress(consent_url)
    logger.progress("Waiting for Admin Consent to complete")

    for iteration in range(60):
        time.sleep(5)
        logger.progress("." * (iteration % 10))
        state = asset.auth_state.get_all(force_reload=True)
        result = state.pop(ADMIN_CONSENT_STATE_KEY, None)
        if result is None:
            continue
        asset.auth_state.put_all(state)
        if result.get("error"):
            logger.progress("Admin consent not received or not given")
            raise ActionFailure("Admin consent not received or not given")

        logger.progress("Admin consent received")
        logger.progress(
            "Waiting for 30 seconds before generating token. If action fails with '403: AccessDenied' error, "
            "please check permissions and re-run the 'test connectivity' after some time."
        )
        logger.progress(
            "Admin consent is already received. You can mark 'Admin Consent Already Provided' to True, "
            "unless you make changes in the permissions."
        )
        time.sleep(30)
        break
    else:
        logger.progress("Timed out waiting for login, please try again")
        raise ActionFailure("Timed out waiting for login, please try again")


def _run_delegated_test(
    soar: SOARClient,
    asset: Asset,
    oauth_callback_url: str,
    oauth_start_url: str,
) -> None:
    """Use SDK authorization-code handling for delegated access."""
    asset.auth_state.pop(AUTHORIZATION_ERROR_STATE_KEY, None)
    asset.auth_state[REDIRECT_URI_STATE_KEY] = oauth_callback_url
    flow = create_delegated_auth_flow(
        asset,
        str(soar.get_asset_id()),
        oauth_callback_url,
    )
    asset.auth_state[AUTHORIZATION_URL_STATE_KEY] = flow.get_authorization_url()
    start_url = f"{oauth_start_url}?{urlencode({'asset_id': soar.get_asset_id()})}"

    logger.progress("Using OAuth URL:")
    logger.progress(oauth_callback_url)
    logger.progress("Please authorize user in a separate tab using URL")
    logger.progress(start_url)
    logger.progress("Waiting for authorization to complete")

    def report_wait(iteration: int) -> None:
        error = asset.auth_state.get(AUTHORIZATION_ERROR_STATE_KEY)
        if error:
            raise ActionFailure("Delegated authorization was not completed")
        logger.progress("." * (iteration % 10))

    try:
        flow.wait_for_authorization(on_progress=report_wait)
    except OAuthClientError as exc:
        raise ActionFailure("Delegated authorization timed out or failed") from exc
    asset.auth_state.pop(AUTHORIZATION_URL_STATE_KEY, None)
    asset.auth_state.pop(AUTHORIZATION_ERROR_STATE_KEY, None)
