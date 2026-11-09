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
"""Typed asset configuration for Microsoft Graph for SharePoint."""

from soar_sdk.asset import BaseAsset, AssetField, FieldCategory


class Asset(BaseAsset):
    tenant_id: str = AssetField(
        description="Tenant ID", category=FieldCategory.CONNECTIVITY
    )
    site_id: str | None = AssetField(
        description="SharePoint Site ID", category=FieldCategory.CONNECTIVITY
    )
    endpoint_test_connectivity: str | None = AssetField(
        description="Endpoint for test connectivity (Valid format: /sites/{hostname}:/{site-server-relative-url})",
        default="/sites/root",
        category=FieldCategory.CONNECTIVITY,
    )
    admin_consent: bool | None = AssetField(
        description="Admin Consent Already Provided",
        category=FieldCategory.CONNECTIVITY,
    )
    client_id: str = AssetField(
        description="Client/Application ID", category=FieldCategory.CONNECTIVITY
    )
    client_secret: str = AssetField(
        description="Client Secret",
        sensitive=True,
        category=FieldCategory.CONNECTIVITY,
    )
