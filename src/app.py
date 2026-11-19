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
"""Composition root for Microsoft Graph for SharePoint."""

from soar_sdk.abstract import SOARClient
from soar_sdk.app import App

from .actions import register_actions
from .asset import Asset
from .test_connectivity import run_test_connectivity
from .webhooks.admin_consent import register_webhooks


def create_msgraphforsharepoint_app() -> App:
    app = App(
        name="MS Graph for SharePoint",
        app_type="reputation",
        logo="logo_msgraphforsharepoint.svg",
        logo_dark="logo_msgraphforsharepoint_dark.svg",
        product_vendor="Microsoft",
        product_name="SharePoint",
        publisher="Splunk",
        appid="7963f3ef-b527-40e5-a704-392c56f0a88d",
        fips_compliant=True,
        python_version="3.13",
        min_phantom_version="8.7.0",
        encrypt_cache_state=True,
        encrypt_ingest_state=True,
        asset_cls=Asset,
    )

    register_webhooks(app)

    @app.test_connectivity()
    def test_connectivity(soar: SOARClient, asset: Asset) -> None:
        consent_callback_url = (
            app.get_webhook_url("admin-consent") if not asset.admin_consent else ""
        )
        run_test_connectivity(
            soar,
            asset,
            consent_callback_url=consent_callback_url,
        )

    return register_actions(app)


app: App = create_msgraphforsharepoint_app()

if __name__ == "__main__":
    app.cli()
