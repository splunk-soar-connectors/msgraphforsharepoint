"""SDK action boundary for the SharePoint list_folder_items action."""

import httpx
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
from ._paths import encode_path, encode_path_segment
from ..asset import Asset


class FolderItemsSummary(ActionOutput):
    items_count: int = OutputField(example_values=[1])


class FileOutput(PermissiveActionOutput):
    mimeType: str | None = OutputField(example_values=["video/mp4"])


class FolderOutput(PermissiveActionOutput):
    childCount: float | None = OutputField(example_values=[5])


class SharedOutput(PermissiveActionOutput):
    scope: str | None = OutputField(example_values=["users"])
    webUrl: str | None = OutputField(cef_types=["url"])


class ParentReferenceOutput(PermissiveActionOutput):
    driveType: str | None = OutputField(example_values=["documentLibrary"])
    id: str | None = OutputField(cef_types=["sharepoint drive item id"])
    name: str | None = OutputField(example_values=["Shared Documents"])
    path: str | None = OutputField()
    siteId: str | None = OutputField()


class FileSystemInfoOutput(PermissiveActionOutput):
    createdDateTime: str | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()


class UserOutput(PermissiveActionOutput):
    displayName: str | None = OutputField(example_values=["Test User"])
    email: str | None = OutputField(cef_types=["email"])
    id: str | None = OutputField()


class CreatedByOutput(PermissiveActionOutput):
    user: UserOutput | None = OutputField()


class LastModifiedByOutput(PermissiveActionOutput):
    user: UserOutput | None = OutputField()


class ListFolderItemsOutput(PermissiveActionOutput):
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


class ListFolderItemsParams(Params):
    drive_id: str | None = Param(
        description="ID for drive that folder lives in. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    folder_path: str = Param(description="Path of the folder to query", primary=True)


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
    with get_graph_client(asset) as graph:
        items = _paginate(graph, endpoint)

    outputs = [ListFolderItemsOutput.model_validate(item) for item in items]
    soar.set_summary(FolderItemsSummary(items_count=len(outputs)))
    return outputs
