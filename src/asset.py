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
