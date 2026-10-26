"""SDK action boundary for the SharePoint create_folder action."""

import httpx
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.params import Params, Param
import json
from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
from ._paths import encode_path_segment
from .drives import drive_root_endpoint
from ..asset import Asset


class CreateFolderParams(Params):
    parent_item_id: str = Param(
        description="Parent Drive Item ID",
        primary=True,
        cef_types=["sharepoint drive item id"],
    )
    folder_name: str = Param(description="Name of newly created folder")
    drive_id: str | None = Param(
        description="ID of drive to create folder in. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )


class CommentingdisabledOutput(PermissiveActionOutput):
    isDisabled: bool


class CommentsettingsOutput(PermissiveActionOutput):
    commentingDisabled: CommentingdisabledOutput


class ApplicationOutput(PermissiveActionOutput):
    displayName: str = OutputField(example_values=["sharepoint_test"])
    id: str = OutputField(example_values=["71b307af-1dcb-4e39-9640-5129afc83162"])


class UserOutput(PermissiveActionOutput):
    displayName: str = OutputField(example_values=["SharePoint App"])


class CreatedbyOutput(PermissiveActionOutput):
    application: ApplicationOutput
    user: UserOutput


class FilesysteminfoOutput(PermissiveActionOutput):
    createdDateTime: str = OutputField(example_values=["2023-10-25T08:55:48Z"])
    lastModifiedDateTime: str = OutputField(example_values=["2023-10-25T08:55:48Z"])


class FolderOutput(PermissiveActionOutput):
    childCount: float = OutputField(example_values=[0])


class LastmodifiedbyOutput(PermissiveActionOutput):
    application: ApplicationOutput
    user: UserOutput


class SharepointidsOutput(PermissiveActionOutput):
    listId: str = OutputField(example_values=["498fd15d-ef79-4c0b-8ac4-c4ea27ed8be2"])
    listItemUniqueId: str = OutputField(
        example_values=["916162a1-5e65-41c9-9ebe-a4bb86d8d76d"]
    )
    siteId: str = OutputField(example_values=["dc6f43e9-54fa-4a39-8783-314e3bbbed41"])
    siteUrl: str = OutputField(
        cef_types=["url"], example_values=["https://test.sharepoint.com/sites/TestSite"]
    )
    tenantId: str = OutputField(example_values=["140fe46d-819d-4b6d-b7ef-1c0a8270f4f0"])
    webId: str = OutputField(example_values=["c42b48c4-59b9-48f1-b96e-e8145b5539fa"])


class ParentreferenceOutput(PermissiveActionOutput):
    driveId: str = OutputField(
        cef_types=["sharepoint drive id"],
        example_values=[
            "b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi"
        ],
    )
    driveType: str = OutputField(example_values=["documentLibrary"])
    id: str = OutputField(
        cef_types=["sharepoint drive item id"],
        example_values=["01SNFLYIVBMJQZCZK6ZFAZ5PVEXODNRV3N"],
    )
    path: str = OutputField(
        example_values=[
            "/drives/b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi/root:/SizeTest-Playbook-Don't Delete"
        ]
    )
    sharepointIds: SharepointidsOutput


class SharedOutput(PermissiveActionOutput):
    scope: str = OutputField(example_values=["unknown"])


class CreateFolderOutput(PermissiveActionOutput):
    context: str = OutputField(
        alias="@odata.context",
        example_values=[
            "https://test.microsoft.com/v1.0/$metadata#sites('test.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fa')/drive/items('01SNFLYIVBMJQZCZK6ZFAZ5PVEXODNRV3N')/children/$entity"
        ],
    )
    etag: str = OutputField(
        alias="@odata.etag",
        example_values=['"{24A7DBF0-E193-4E0A-A960-ECF5DB994FFF},1"'],
    )
    cTag: str = OutputField(
        example_values=['"c:{24A7DBF0-E193-4E0A-A960-ECF5DB994FFF},0"']
    )
    commentSettings: CommentsettingsOutput
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2023-10-25T08:55:48Z"])
    eTag: str = OutputField(
        example_values=['"{24A7DBF0-E193-4E0A-A960-ECF5DB994FFF},1"']
    )
    fileSystemInfo: FilesysteminfoOutput
    folder: FolderOutput
    id: str = OutputField(cef_types=["sharepoint drive item id"])
    lastModifiedBy: LastmodifiedbyOutput
    lastModifiedDateTime: str = OutputField(example_values=["2023-10-25T08:55:48Z"])
    name: str = OutputField(example_values=["test2"])
    parentReference: ParentreferenceOutput
    shared: SharedOutput
    size: float = OutputField(example_values=[0])
    webUrl: str = OutputField(cef_types=["url"])


def _request_graph(client: httpx.Client, method: str, endpoint: str, **kwargs):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request_headers = kwargs.pop("headers", {})
    headers.update(request_headers)
    try:
        response = client.request(
            method, endpoint, headers=headers, follow_redirects=False, **kwargs
        )
    except httpx.RequestError as exc:
        raise ActionFailure("Error connecting to Microsoft Graph") from exc
    try:
        return get_graph_response(response)
    except GraphResponseError as exc:
        raise ActionFailure(str(exc)) from exc


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

    with get_graph_client(asset) as graph:
        response = _request_graph(
            graph, "POST", endpoint, content=json.dumps(request_body)
        )

    soar.set_message("Successfully created a folder")
    return CreateFolderOutput.model_validate(response)
