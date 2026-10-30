"""SDK action boundary for the SharePoint copy_drive_item action."""

from soar_sdk.params import Params, Param
import json
from typing import Any
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _request_graph
from ._paths import encode_path_segment
from .drives import drive_root_endpoint
from ..asset import Asset


class CopyDriveItemOutput(PermissiveActionOutput):
    """Preserve the legacy action's unstructured Graph response payload."""


class CopyDriveItemParams(Params):
    source_item_id: str = Param(
        description="ID for drive item that needs to be copied",
        primary=True,
        cef_types=["sharepoint drive item id"],
    )
    source_drive_id: str | None = Param(
        description="Drive ID that contains the source item to copy. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    dest_drive_id: str | None = Param(
        description="Drive ID that contains target folder to copy item to. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    dest_folder_id: str = Param(
        description="ID of target folder to copy drive item to",
        primary=True,
        cef_types=["sharepoint drive item id"],
    )
    file_name: str | None = Param(
        description="Optional new folder/file name for the copy. If not provided will use the original name"
    )


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

    with get_graph_client(asset) as graph:
        response = _request_graph(
            graph, "POST", endpoint, content=json.dumps(request_body)
        )

    soar.set_message("Successfully copied an item")
    return CopyDriveItemOutput(**response)
