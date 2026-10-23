"""List direct children of a SharePoint drive root."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField

from ..client import GraphClient
from .drives import drive_children_endpoint

if TYPE_CHECKING:
    from ..app import Asset, ListDriveChildrenParams


class DriveChildrenSummary(ActionOutput):
    drive_children_count: int = OutputField(example_values=[1])


class HashesOutput(ActionOutput):
    quickXorHash: str | None = OutputField(
        example_values=["8JpxaQB3wX1/FkQ5Gt3prUbUUFU="]
    )


class FileOutput(ActionOutput):
    hashes: HashesOutput | None = OutputField()
    mimeType: str | None = OutputField(example_values=["application/vnd.ms-excel"])


class FolderOutput(ActionOutput):
    childCount: float | None = OutputField(example_values=[1])


class ImageOutput(ActionOutput):
    width: float | None = OutputField(example_values=[1752])
    height: float | None = OutputField(example_values=[1244])


class UserOutput(ActionOutput):
    displayName: str | None = OutputField(example_values=["SharePoint App"])
    email: str | None = OutputField()
    id: str | None = OutputField()


class CreatedByOutput(ActionOutput):
    user: UserOutput | None = OutputField()


class DecoratorOutput(ActionOutput):
    iconColor: str | None = OutputField(example_values=["darkGreen"])


class FileSystemInfoOutput(ActionOutput):
    createdDateTime: str | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()


class ApplicationOutput(ActionOutput):
    displayName: str | None = OutputField()
    id: str | None = OutputField()


class LastModifiedByOutput(ActionOutput):
    application: ApplicationOutput | None = OutputField()
    user: UserOutput | None = OutputField()


class ParentReferenceOutput(ActionOutput):
    driveId: str | None = OutputField(cef_types=["sharepoint drive id"])
    driveType: str | None = OutputField()
    id: str | None = OutputField(cef_types=["sharepoint drive item id"])
    name: str | None = OutputField()
    path: str | None = OutputField()
    siteId: str | None = OutputField()


class SharedOutput(ActionOutput):
    scope: str | None = OutputField(example_values=["users"])


class SpecialFolderOutput(ActionOutput):
    name: str | None = OutputField(example_values=["apps"])


class ListDriveChildrenOutput(ActionOutput):
    download_url: str | None = OutputField(
        alias="@microsoft.graph.downloadUrl",
        cef_types=["url"],
        example_values=["https://graph.microsoft.com/v1.0/download"],
    )
    image: ImageOutput | None = OutputField()
    cTag: str | None = OutputField()
    createdBy: CreatedByOutput | None = OutputField()
    createdDateTime: str | None = OutputField()
    decorator: DecoratorOutput | None = OutputField()
    eTag: str | None = OutputField()
    file: FileOutput | None = OutputField()
    fileSystemInfo: FileSystemInfoOutput | None = OutputField()
    folder: FolderOutput | None = OutputField()
    id: str | None = OutputField(cef_types=["sharepoint drive item id"])
    lastModifiedBy: LastModifiedByOutput | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()
    name: str | None = OutputField()
    parentReference: ParentReferenceOutput | None = OutputField()
    shared: SharedOutput | None = OutputField()
    size: float | None = OutputField(example_values=[775])
    specialFolder: SpecialFolderOutput | None = OutputField()
    webUrl: str | None = OutputField(cef_types=["url"])


def list_drive_children(
    params: ListDriveChildrenParams, soar: SOARClient, asset: Asset
) -> list[ListDriveChildrenOutput]:
    """List items directly under a drive's root folder."""
    endpoint = drive_children_endpoint(str(asset.site_id), params.drive_id)
    with GraphClient(asset) as graph:
        children = graph.paginate(endpoint)

    outputs = [ListDriveChildrenOutput.model_validate(item) for item in children]
    soar.set_summary(DriveChildrenSummary(drive_children_count=len(outputs)))
    return outputs
