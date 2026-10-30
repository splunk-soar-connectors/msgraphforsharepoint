"""Microsoft Graph connectivity check."""

from __future__ import annotations

import time

import httpx
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from .auth import get_graph_client
from .graph_response import GraphResponseError, get_graph_response
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger

if TYPE_CHECKING:
    from soar_sdk.abstract import SOARClient

    from .asset import Asset


ADMIN_CONSENT_STATE_KEY = "msgraphforsharepoint_admin_consent_result"
logger = getLogger()


def run_test_connectivity(
    soar: SOARClient, asset: Asset, *, consent_callback_url: str
) -> None:
    """Complete the legacy admin-consent flow, then request the Graph endpoint."""
    if not asset.admin_consent:
        logger.progress("Getting App REST endpoint URL")
        redirect_uri = consent_callback_url
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

    endpoint = asset.endpoint_test_connectivity or "/sites/root"
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    try:
        with get_graph_client(asset, force_token_refresh=True) as graph:
            response = graph.get(endpoint)
            get_graph_response(response)
    except GraphResponseError as exc:
        raise ActionFailure(str(exc)) from exc
    except httpx.RequestError as exc:
        raise ActionFailure("Error connecting to Microsoft Graph") from exc
    soar.set_message("Test Connectivity Passed")
