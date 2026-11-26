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
"""SDK action boundary for the SharePoint upload_file action."""

from collections.abc import Iterator
from typing import BinaryIO

from pydantic import ValidationError
from soar_sdk.abstract import SOARClient
from soar_sdk.auth import OAuthClientError
from soar_sdk.action_results import (
    ActionOutput,
    ActionResult,
    OutputField,
    PermissiveActionOutput,
)
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..auth import get_graph_client
from ._graph import _request_graph
from ._paths import encode_path, encode_path_segment
from .drives import drive_root_endpoint

# Microsoft documents the simple-upload limit as 250 MB; use decimal MB bytes.
_GRAPH_SIMPLE_UPLOAD_LIMIT = 250_000_000
_UPLOAD_CHUNK_SIZE = 1024 * 1024


class UploadFileSummary(ActionOutput):
    file_name: str = OutputField()
    web_url: str = OutputField(cef_types=["url"])


class UploadFileParams(Params):
    vault_id: str = Param(
        description="Vault ID of the file to upload",
        cef_types=["vault id"],
    )
    file_path: str | None = Param(
        description="Folder path on the site. Leave blank to upload to the library root.",
        default=None,
    )
    file_name: str | None = Param(
        description="Optional destination file name. Defaults to the vault attachment name.",
        default=None,
    )
    drive_id: str | None = Param(
        description="Drive ID to upload to. If omitted, the default drive is used.",
        cef_types=["sharepoint drive id"],
        default=None,
    )


class UploadFileOutput(PermissiveActionOutput):
    id: str = OutputField(cef_types=["sharepoint drive item id"])
    name: str = OutputField()
    size: int = OutputField()
    webUrl: str = OutputField(cef_types=["url"])


def _upload_endpoint(
    site_id: str, drive_id: str | None, file_path: str | None, file_name: str
) -> str:
    """Build the Graph simple-upload endpoint with validated path components."""
    try:
        encoded_path = encode_path(file_path or "", allow_empty=True)
        encoded_name = encode_path_segment(file_name)
    except ValueError as exc:
        raise ValueError(f"Invalid file path or name: {exc}") from exc

    try:
        root = drive_root_endpoint(site_id, drive_id)
    except ValueError as exc:
        raise ValueError(f"Invalid drive ID: {exc}") from exc
    destination = f"{encoded_path}/{encoded_name}" if encoded_path else encoded_name
    return f"{root}/root:/{destination}:/content"


def _file_chunks(
    file_object: BinaryIO, chunk_size: int = _UPLOAD_CHUNK_SIZE
) -> Iterator[bytes]:
    """Yield bounded chunks so uploads do not read the whole attachment into memory."""
    while chunk := file_object.read(chunk_size):
        yield chunk


def upload_file(
    params: UploadFileParams, soar: SOARClient, asset: Asset
) -> UploadFileOutput:
    """Upload a SOAR vault attachment to a SharePoint document library."""
    if not asset.site_id:
        return ActionResult(
            False,
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for uploading a file to a specific site",
            params.model_dump(by_alias=True),
        )

    try:
        attachments = soar.vault.get_attachment(
            vault_id=params.vault_id,
            container_id=soar.get_executing_container_id(),
        )
    except Exception:
        return ActionResult(
            False,
            "Unable to retrieve the file from the SOAR vault",
            params.model_dump(by_alias=True),
        )

    if len(attachments) != 1:
        return ActionResult(
            False,
            "The vault ID must identify exactly one file in the current container",
            params.model_dump(by_alias=True),
        )

    attachment = attachments[0]
    file_name = params.file_name or attachment.name
    if attachment.size > _GRAPH_SIMPLE_UPLOAD_LIMIT:
        return ActionResult(
            False,
            "Microsoft Graph simple upload supports files up to 250 MB (250,000,000 bytes)",
            params.model_dump(by_alias=True),
        )

    try:
        endpoint = _upload_endpoint(
            asset.site_id, params.drive_id, params.file_path, file_name
        )
    except ValueError as exc:
        return ActionResult(False, str(exc), params.model_dump(by_alias=True))

    try:
        with attachment.open("rb") as content, get_graph_client(asset) as graph:
            response = _request_graph(
                graph,
                "PUT",
                endpoint,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(attachment.size),
                },
                content=_file_chunks(content),
            )
    except ActionFailure as exc:
        exc.set_action_name("upload_file")
        return ActionResult(False, str(exc), params.model_dump(by_alias=True))
    except (OAuthClientError, ValueError):
        return ActionResult(
            False,
            "Unable to authenticate or send the file to Microsoft Graph",
            params.model_dump(by_alias=True),
        )
    except OSError:
        return ActionResult(
            False,
            "Unable to read the file from the SOAR vault",
            params.model_dump(by_alias=True),
        )

    if not isinstance(response, dict):
        return ActionResult(
            False,
            "Microsoft Graph returned an invalid file upload response",
            params.model_dump(by_alias=True),
        )

    try:
        output = UploadFileOutput.model_validate(response)
    except ValidationError:
        return ActionResult(
            False,
            "Microsoft Graph returned an invalid file upload response",
            params.model_dump(by_alias=True),
        )
    soar.set_message("Successfully uploaded file")
    soar.set_summary(
        UploadFileSummary(file_name=file_name, web_url=output.webUrl)
    )
    return output
