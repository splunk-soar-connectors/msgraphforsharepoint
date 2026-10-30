"""SDK action boundary for the SharePoint remove_folder action."""

from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _request_graph
from ._paths import encode_path, encode_path_segment
from .drives import drive_root_endpoint
from ..asset import Asset


class RemoveFolderParams(Params):
    folder_path: str = Param(description="Folder path on site")
    drive_id: str | None = Param(
        description="The file is searched in this drive. If no drive is specified, the default drive will be used"
    )


def remove_folder(
    params: RemoveFolderParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    """Delete a folder using the legacy root path and success message."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for removing a file from specific site"
        )

    try:
        encoded_path = encode_path(params.folder_path)
    except ValueError as exc:
        raise ActionFailure(f"Invalid folder path: {exc}") from exc
    if params.drive_id:
        try:
            encode_path_segment(params.drive_id)
        except ValueError as exc:
            raise ActionFailure(f"Invalid drive id: {exc}") from exc
    endpoint = (
        f"{drive_root_endpoint(asset.site_id, params.drive_id)}/root:/{encoded_path}"
    )
    with get_graph_client(asset) as graph:
        _request_graph(graph, "DELETE", endpoint)

    soar.set_message("Successfully deleted folder")
    return ActionOutput()
