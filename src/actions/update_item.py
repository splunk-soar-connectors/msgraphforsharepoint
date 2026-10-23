"""SDK action boundary for the SharePoint update_item action."""

import httpx
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
from ._paths import encode_path_segment
from ..asset import Asset


class ListItemSummary(ActionOutput):
    sites_count: int = OutputField(example_values=[1])


class UpdateItemParams(Params):
    list: str = Param(
        description="Title or ID of the list to which the item belongs",
        primary=True,
        cef_types=["sharepoint list id", "sharepoint list name"],
    )
    item_id: float = Param(
        description="ID of the item to update",
        primary=True,
        cef_types=["sharepoint item id"],
    )
    item: str = Param(description="JSON string of item")


class OdataOutput(ActionOutput):
    etag: str


class ContenttypeOutput(ActionOutput):
    id: str
    name: str


class UserOutput(ActionOutput):
    displayName: str


class CreatedbyOutput(ActionOutput):
    user: UserOutput


class FieldsOutput(PermissiveActionOutput):
    odata: OdataOutput
    AppAuthorLookupId: str
    AppEditorLookupId: str
    AssetType: str = OutputField(example_values=["Mobile"])
    Attachments: bool
    AuthorLookupId: str
    Color: str = OutputField(example_values=["Red"])
    ConditionNotes: str = OutputField(example_values=["Note for the Updated Asset"])
    ContentType: str
    Created: str
    CurrentOwnerLookupId: str = OutputField(example_values=["18"])
    DueDate: str = OutputField(example_values=["2023-08-05T07:00:00Z"])
    Edit: str
    EditorLookupId: str
    FolderChildCount: str
    ItemChildCount: str
    LinkTitle: str
    LinkTitleNoMenu: str
    Manufacturer: str = OutputField(example_values=["Test-Updated-Manufacturer"])
    Model: str = OutputField(example_values=["Model of the Updated Asset"])
    Modified: str
    OrderNumber: str = OutputField(example_values=["2"])
    PreviousOwnerLookupId: str = OutputField(example_values=["17"])
    PurchaseDate: str = OutputField(example_values=["2022-08-05T07:00:00Z"])
    PurchasePrice: float = OutputField(example_values=[1])
    SerialNumber: str = OutputField(example_values=["Test-SerialNumber-Updated"])
    Status: str = OutputField(example_values=["Status of the Asset"])
    Title: str = OutputField(example_values=["Test-Updated-Title"])
    ComplianceFlags: str = OutputField(alias="_ComplianceFlags")
    ComplianceTag: str = OutputField(alias="_ComplianceTag")
    ComplianceTagUserId: str = OutputField(alias="_ComplianceTagUserId")
    ComplianceTagWrittenTime: str = OutputField(alias="_ComplianceTagWrittenTime")
    UIVersionString: str = OutputField(alias="_UIVersionString")
    id: str


class Fields_OdataOutput(ActionOutput):
    context: str = OutputField(cef_types=["url"])


class ApplicationOutput(ActionOutput):
    displayName: str
    id: str


class LastmodifiedbyOutput(ActionOutput):
    application: ApplicationOutput
    user: UserOutput


class ParentreferenceOutput(ActionOutput):
    id: str = OutputField(example_values=["a86797a9-c9a9-47e7-891b-8413b2d758fc"])
    siteId: str


class UpdateItemOutput(ActionOutput):
    odata: OdataOutput
    contentType: ContenttypeOutput
    createdBy: CreatedbyOutput
    createdDateTime: str
    eTag: str
    fields: FieldsOutput
    fields_odata: Fields_OdataOutput
    id: str = OutputField(cef_types=["sharepoint item id"])
    lastModifiedBy: LastmodifiedbyOutput
    lastModifiedDateTime: str
    parentReference: ParentreferenceOutput
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


def update_item(
    params: UpdateItemParams, soar: SOARClient, asset: Asset
) -> UpdateItemOutput:
    """Update one list item with the existing legacy request contract."""
    try:
        list_id = encode_path_segment(params.list)
        item_id = encode_path_segment(params.item_id)
    except ValueError as exc:
        raise ActionFailure(f"Invalid list or item ID: {exc}") from exc

    endpoint = f"/sites/{asset.site_id}/lists/{list_id}/items/{item_id}"
    with get_graph_client(asset) as graph:
        response = _request_graph(
            graph, "PATCH", endpoint, content=params.item.encode("utf-8")
        )

    output = UpdateItemOutput.model_validate(response)
    soar.set_summary(ListItemSummary(sites_count=1))
    return output
