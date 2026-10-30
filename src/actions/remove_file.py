"""SDK action boundary for the SharePoint remove_file action."""

from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _request_graph
from ._paths import encode_path, encode_path_segment
from .drives import drive_root_endpoint
from ..asset import Asset


class RemoveFileParams(Params):
    file_name: str = Param(description="File name to remove")
    file_path: str = Param(description="Folder path on site")
    drive_id: str | None = Param(
        description="The file is searched in this drive. If no drive is specified, the default drive will be used"
    )


def _file_endpoint(
    site_id: str, drive_id: str | None, file_path: str, file_name: str
) -> tuple[str, str]:
    try:
        encoded_path = encode_path(file_path, allow_empty=True)
        encoded_name = encode_path_segment(file_name)
    except ValueError as exc:
        raise ActionFailure(f"Invalid file path: {exc}") from exc
    if drive_id:
        try:
            encode_path_segment(drive_id)
        except ValueError as exc:
            raise ActionFailure(f"Invalid drive id: {exc}") from exc
    metadata_endpoint = (
        f"{drive_root_endpoint(site_id, drive_id)}/root:/{encoded_path}/{encoded_name}"
    )
    return metadata_endpoint, encoded_name


def remove_file(
    params: RemoveFileParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    """Delete a file using the legacy metadata endpoint and success message."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for removing a file from specific site"
        )

    metadata_endpoint, _ = _file_endpoint(
        asset.site_id, params.drive_id, params.file_path, params.file_name
    )
    with get_graph_client(asset) as graph:
        _request_graph(graph, "DELETE", metadata_endpoint)

    soar.set_message("Successfully deleted file")
    return ActionOutput()
