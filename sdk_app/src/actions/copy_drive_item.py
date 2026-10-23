"""Copy an item between SharePoint drive folders."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure

from ..client import GraphClient, encode_path_segment
from .drives import drive_root_endpoint

if TYPE_CHECKING:
    from ..app import Asset, CopyDriveItemParams


class CopyDriveItemOutput(PermissiveActionOutput):
    """Preserve the legacy action's unstructured Graph response payload."""


def copy_drive_item(
    params: CopyDriveItemParams, soar: SOARClient, asset: Asset
) -> CopyDriveItemOutput:
    """Copy a drive item using the legacy request body and success message."""
    try:
        source_item_id = encode_path_segment(params.source_item_id)
    except ValueError as exc:
        raise ActionFailure(f"Invalid source item ID: {exc}") from exc

    endpoint = (
        f"{drive_root_endpoint(str(asset.site_id), params.source_drive_id)}"
        f"/items/{source_item_id}/copy"
    )
    parent_reference: dict[str, Any] = {"id": params.dest_folder_id}
    if params.dest_drive_id:
        parent_reference["driveId"] = params.dest_drive_id
    request_body: dict[str, Any] = {"parentReference": parent_reference}
    if params.file_name:
        request_body["name"] = params.file_name

    with GraphClient(asset) as graph:
        response = graph.request("POST", endpoint, data=json.dumps(request_body))

    soar.set_message("Successfully copied an item")
    return CopyDriveItemOutput(**response)
