"""List direct children of a folder in a SharePoint drive."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure

from ..client import GraphClient, encode_path, encode_path_segment

if TYPE_CHECKING:
    from ..app import Asset, ListFolderItemsParams


class FolderItemsSummary(ActionOutput):
    items_count: int = OutputField(example_values=[1])


class FileOutput(ActionOutput):
    mimeType: str | None = OutputField(example_values=["video/mp4"])


class FolderOutput(ActionOutput):
    childCount: float | None = OutputField(example_values=[5])


class SharedOutput(ActionOutput):
    scope: str | None = OutputField(example_values=["users"])
    webUrl: str | None = OutputField(cef_types=["url"])


class ParentReferenceOutput(ActionOutput):
    driveType: str | None = OutputField(example_values=["documentLibrary"])
    id: str | None = OutputField(cef_types=["sharepoint drive item id"])
    name: str | None = OutputField(example_values=["Shared Documents"])
    path: str | None = OutputField()
    siteId: str | None = OutputField()


class FileSystemInfoOutput(ActionOutput):
    createdDateTime: str | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()


class UserOutput(ActionOutput):
    displayName: str | None = OutputField(example_values=["Test User"])
    email: str | None = OutputField(cef_types=["email"])
    id: str | None = OutputField()


class CreatedByOutput(ActionOutput):
    user: UserOutput | None = OutputField()


class LastModifiedByOutput(ActionOutput):
    user: UserOutput | None = OutputField()


class ListFolderItemsOutput(ActionOutput):
    id: str | None = OutputField()
    cTag: str | None = OutputField()
    eTag: str | None = OutputField()
    file: FileOutput | None = OutputField()
    folder: FolderOutput | None = OutputField()
    name: str | None = OutputField()
    size: float | None = OutputField()
    shared: SharedOutput | None = OutputField()
    parentReference: ParentReferenceOutput | None = OutputField()
    fileSystemInfo: FileSystemInfoOutput | None = OutputField()
    createdBy: CreatedByOutput | None = OutputField()
    lastModifiedBy: LastModifiedByOutput | None = OutputField()
    createdDateTime: str | None = OutputField()
    download_url: str | None = OutputField(
        alias="@microsoft.graph.downloadUrl",
        cef_types=["url"],
        example_values=["https://graph.microsoft.com/v1.0/download"],
    )
    lastModifiedDateTime: str | None = OutputField()


def list_folder_items(
    params: ListFolderItemsParams, soar: SOARClient, asset: Asset
) -> list[ListFolderItemsOutput]:
    """List direct children at a path within the configured site drive."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for removing a file from specific site"
        )

    try:
        encoded_path = encode_path(params.folder_path)
        encoded_drive_id = (
            encode_path_segment(params.drive_id) if params.drive_id else None
        )
    except ValueError as exc:
        raise ActionFailure(f"Invalid folder path: {exc}") from exc

    drive_endpoint = (
        f"/sites/{asset.site_id}/drives/{encoded_drive_id}"
        if encoded_drive_id
        else f"/sites/{asset.site_id}/drive"
    )
    endpoint = f"{drive_endpoint}/root:/{encoded_path}:/children"
    with GraphClient(asset) as graph:
        items = graph.paginate(endpoint)

    outputs = [ListFolderItemsOutput.model_validate(item) for item in items]
    soar.set_summary(FolderItemsSummary(items_count=len(outputs)))
    return outputs
