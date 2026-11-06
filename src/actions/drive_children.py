"""SDK action boundary for the SharePoint list_drive_children action."""

from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from ..auth import get_graph_client
from ._graph import _paginate
from .drives import drive_children_endpoint
from ..asset import Asset


class DriveChildrenSummary(ActionOutput):
    drive_children_count: int = OutputField(example_values=[1])


class HashesOutput(PermissiveActionOutput):
    quickXorHash: str | None = OutputField(
        example_values=["8JpxaQB3wX1/FkQ5Gt3prUbUUFU="]
    )


class FileOutput(PermissiveActionOutput):
    hashes: HashesOutput | None = OutputField()
    mimeType: str | None = OutputField(example_values=["application/vnd.ms-excel"])


class FolderOutput(PermissiveActionOutput):
    childCount: float | None = OutputField(example_values=[1])


class ImageOutput(PermissiveActionOutput):
    width: float | None = OutputField(example_values=[1752])
    height: float | None = OutputField(example_values=[1244])


class UserOutput(PermissiveActionOutput):
    displayName: str | None = OutputField(example_values=["SharePoint App"])
    email: str | None = OutputField()
    id: str | None = OutputField()


class CreatedByOutput(PermissiveActionOutput):
    user: UserOutput | None = OutputField()


class DecoratorOutput(PermissiveActionOutput):
    iconColor: str | None = OutputField(example_values=["darkGreen"])


class FileSystemInfoOutput(PermissiveActionOutput):
    createdDateTime: str | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()


class ApplicationOutput(PermissiveActionOutput):
    displayName: str | None = OutputField()
    id: str | None = OutputField()


class LastModifiedByOutput(PermissiveActionOutput):
    application: ApplicationOutput | None = OutputField()
    user: UserOutput | None = OutputField()


class ParentReferenceOutput(PermissiveActionOutput):
    driveId: str | None = OutputField(
        cef_types=["sharepoint drive id"], column_name="Drive ID"
    )
    driveType: str | None = OutputField()
    id: str | None = OutputField(cef_types=["sharepoint drive item id"])
    name: str | None = OutputField()
    path: str | None = OutputField()
    siteId: str | None = OutputField()


class SharedOutput(PermissiveActionOutput):
    scope: str | None = OutputField(example_values=["users"])


class SpecialFolderOutput(PermissiveActionOutput):
    name: str | None = OutputField(example_values=["apps"])


class ListDriveChildrenOutput(PermissiveActionOutput):
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
    id: str | None = OutputField(
        cef_types=["sharepoint drive item id"], column_name="Drive Item ID"
    )
    name: str | None = OutputField(column_name="Item Name")
    webUrl: str | None = OutputField(cef_types=["url"], column_name="Web URL")
    lastModifiedBy: LastModifiedByOutput | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()
    parentReference: ParentReferenceOutput | None = OutputField()
    shared: SharedOutput | None = OutputField()
    size: float | None = OutputField(example_values=[775])
    specialFolder: SpecialFolderOutput | None = OutputField()


class ListDriveChildrenParams(Params):
    drive_id: str | None = Param(
        description="ID of drive to list. If no id is specified the default drive will be queried",
        primary=True,
        cef_types=["sharepoint drive id"],
    )


def list_drive_children(
    params: ListDriveChildrenParams, soar: SOARClient, asset: Asset
) -> list[ListDriveChildrenOutput]:
    """List items directly under a drive's root folder."""
    endpoint = drive_children_endpoint(str(asset.site_id), params.drive_id)
    with get_graph_client(asset) as graph:
        children = _paginate(graph, endpoint)

    outputs = [ListDriveChildrenOutput.model_validate(item) for item in children]
    soar.set_summary(DriveChildrenSummary(drive_children_count=len(outputs)))
    return outputs
