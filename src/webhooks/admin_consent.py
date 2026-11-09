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
"""Microsoft admin-consent callback endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.webhooks.models import WebhookRequest, WebhookResponse

from ..test_connectivity import ADMIN_CONSENT_STATE_KEY

if TYPE_CHECKING:
    from soar_sdk.app import App


def register_webhooks(app: App) -> None:
    """Register the unauthenticated Microsoft redirect callback."""
    app.enable_webhooks(default_requires_auth=False)

    @app.webhook("/admin-consent", allowed_methods=["GET"])
    def handle_admin_consent(request: WebhookRequest) -> WebhookResponse:
        query = request.query
        state_id = (query.get("state") or [None])[0]
        if not state_id:
            return WebhookResponse.text_response(
                "Error handling request: missing state", status_code=400
            )

        if state_id != str(request.asset_id):
            return WebhookResponse.text_response(
                "Error handling request: invalid state", status_code=400
            )

        error = (query.get("error") or [None])[0]
        error_description = (query.get("error_description") or [None])[0]
        request.asset.auth_state[ADMIN_CONSENT_STATE_KEY] = {
            "error": bool(error),
            "error_description": error_description,
        }
        if error:
            return WebhookResponse.text_response(
                error_description or "", status_code=401
            )
        return WebhookResponse.text_response("You can now close this page")
