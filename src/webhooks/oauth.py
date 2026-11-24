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
"""Microsoft delegated OAuth webhooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.auth import create_oauth_callback_handler
from soar_sdk.webhooks.models import WebhookRequest, WebhookResponse

from ..auth import get_oauth_client
from ..consts import (
    AUTHORIZATION_ERROR_STATE_KEY,
    AUTHORIZATION_URL_STATE_KEY,
    OAUTH_CALLBACK_ROUTE,
    OAUTH_START_ROUTE,
    OAUTH_SUCCESS_MESSAGE,
)

if TYPE_CHECKING:
    from soar_sdk.app import App


def register_oauth_webhooks(app: App) -> None:
    """Register the SDK OAuth start and callback routes."""
    callback_handler = create_oauth_callback_handler(
        get_oauth_client,
        success_message=OAUTH_SUCCESS_MESSAGE,
    )

    @app.webhook(OAUTH_START_ROUTE, allowed_methods=["GET"])
    def oauth_start(request: WebhookRequest) -> WebhookResponse:
        authorization_url = request.asset.auth_state.get(AUTHORIZATION_URL_STATE_KEY)
        if not authorization_url:
            return WebhookResponse.text_response(
                "Authorization is not pending. Run test connectivity again.",
                status_code=400,
            )
        return WebhookResponse(
            status_code=302,
            headers=[("Location", authorization_url)],
            content="",
        )

    @app.webhook(OAUTH_CALLBACK_ROUTE, allowed_methods=["GET"])
    def oauth_callback(request: WebhookRequest) -> WebhookResponse:
        if (request.query.get("error") or [None])[0]:
            request.asset.auth_state[AUTHORIZATION_ERROR_STATE_KEY] = True
        return callback_handler(request)
