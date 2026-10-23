"""Download and delete files and folders in SharePoint drives."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput
from soar_sdk.exceptions import ActionFailure

from ..client import GraphClient, encode_path, encode_path_segment
from .drives import drive_root_endpoint

if TYPE_CHECKING:
    from ..app import (
        Asset,
        GetFileOutput,
        GetFileParams,
        RemoveFileParams,
        RemoveFolderParams,
    )


class GetFileSummary(ActionOutput):
    vault_id: str


def _vault_exception_detail(exc: Exception) -> str:
    error_code = None
    error_message = "Unknown error occurred. Please check the asset configuration and|or action parameters"
    try:
        if len(exc.args) > 1:
            error_code, error_message = exc.args[:2]
        elif len(exc.args) == 1:
            error_message = exc.args[0]
    except Exception:
        pass
    return f"Error Code: {error_code}. Error Message: {error_message}"


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
    metadata_endpoint = f"{drive_root_endpoint(site_id, drive_id)}/root:/{encoded_path}/{encoded_name}"
    return metadata_endpoint, encoded_name


def get_file(
    params: GetFileParams, soar: SOARClient, asset: Asset
) -> GetFileOutput:
    """Retrieve file metadata and store the file content in the SOAR vault."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving a file from specific site"
        )

    metadata_endpoint, encoded_name = _file_endpoint(
        asset.site_id, params.drive_id, params.file_path, params.file_name
    )
    temporary_path: str | None = None
    try:
        descriptor, temporary_path = tempfile.mkstemp(
            dir=soar.vault.get_vault_tmp_dir()
        )
        os.close(descriptor)
        with GraphClient(asset) as graph:
            metadata = graph.request("GET", metadata_endpoint)
            graph.download_to_file(f"{metadata_endpoint}:/content", temporary_path)

        try:
            vault_id = soar.vault.add_attachment(
                container_id=soar.get_executing_container_id(),
                file_location=temporary_path,
                file_name=encoded_name,
            )
        except Exception as exc:
            raise ActionFailure(
                "Unable to add file to the vault for attachment name: "
                f"{encoded_name}. Error: {_vault_exception_detail(exc)}"
            ) from exc
    finally:
        if temporary_path is not None:
            Path(temporary_path).unlink(missing_ok=True)

    from ..app import GetFileOutput

    output = GetFileOutput.model_validate(metadata)
    soar.set_summary(GetFileSummary(vault_id=vault_id))
    return output


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
    with GraphClient(asset) as graph:
        graph.request("DELETE", metadata_endpoint)

    soar.set_message("Successfully deleted file")
    return ActionOutput()


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
    endpoint = f"{drive_root_endpoint(asset.site_id, params.drive_id)}/root:/{encoded_path}"
    with GraphClient(asset) as graph:
        graph.request("DELETE", endpoint)

    soar.set_message("Successfully deleted folder")
    return ActionOutput()
