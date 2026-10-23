"""SDK action boundary for the SharePoint list_drive_children action."""

import httpx
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
from .drives import drive_children_endpoint
from ..asset import Asset


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


class ListDriveChildrenParams(Params):
    drive_id: str | None = Param(
        description="ID of drive to list. If no id is specified the default drive will be queried",
        primary=True,
        cef_types=["sharepoint drive id"],
    )


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


def _paginate(
    client: httpx.Client,
    endpoint: str,
    *,
    limit: int | None = None,
    params: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    """Follow Graph pages for this action, guarding against loops and runaway pages."""
    page_params = dict(params or {})
    page_params["$top"] = min(limit, 1000) if limit else 1000
    results: list[dict[str, object]] = []
    next_link: str | None = None
    seen_links: set[str] = set()
    for _ in range(1000):
        page = _request_graph(
            client,
            "GET",
            next_link or endpoint,
            **({} if next_link else {"params": page_params}),
        )
        if not isinstance(page, dict):
            raise ActionFailure("Microsoft Graph returned an invalid page")
        value = page.get("value", [])
        if not isinstance(value, list) or not all(
            isinstance(item, dict) for item in value
        ):
            raise ActionFailure("Microsoft Graph returned an invalid page value")
        results.extend(value)
        if limit is not None and len(results) >= limit:
            return results[:limit]
        next_link = page.get("@odata.nextLink")
        if not next_link:
            return results
        if not isinstance(next_link, str) or next_link in seen_links:
            raise ActionFailure(
                "Rejected repeated or invalid Microsoft Graph pagination URL"
            )
        seen_links.add(next_link)
    raise ActionFailure("Microsoft Graph pagination exceeded its safety limit")


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
