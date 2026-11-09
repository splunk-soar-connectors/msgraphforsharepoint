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
) -> list[ActionOutput]:
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
    return []
