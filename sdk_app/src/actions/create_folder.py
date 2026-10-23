"""Create a folder in a SharePoint drive."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure

from ..client import GraphClient, encode_path_segment
from .drives import drive_root_endpoint

if TYPE_CHECKING:
    from ..app import Asset, CreateFolderOutput, CreateFolderParams


def create_folder(
    params: CreateFolderParams, soar: SOARClient, asset: Asset
) -> CreateFolderOutput:
    """Create a folder and return the Graph response as legacy data."""
    try:
        parent_item_id = encode_path_segment(params.parent_item_id)
    except ValueError as exc:
        raise ActionFailure(f"Invalid parent item ID: {exc}") from exc

    drive_endpoint = drive_root_endpoint(str(asset.site_id), params.drive_id)
    endpoint = f"{drive_endpoint}/items/{parent_item_id}/children"
    request_body = {
        "name": params.folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename",
    }

    with GraphClient(asset) as graph:
        response = graph.request("POST", endpoint, data=json.dumps(request_body))

    from ..app import CreateFolderOutput

    soar.set_message("Successfully created a folder")
    return CreateFolderOutput.model_validate(response)
