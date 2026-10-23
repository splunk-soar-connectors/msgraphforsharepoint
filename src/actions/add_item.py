"""SDK action boundary for the SharePoint add_item action."""

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


class AddItemParams(Params):
    list: str = Param(
        description="Title or ID of the list to add an item",
        primary=True,
        cef_types=["sharepoint list id", "sharepoint list name"],
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
    Approved: bool
    AssetType: str = OutputField(example_values=["Laptop"])
    Attachments: bool
    AuthorLookupId: str
    Color: str = OutputField(example_values=["Color of the Asset"])
    Complete: bool = OutputField(example_values=[False])
    ConditionNotes: str = OutputField(example_values=["Note for the Asset"])
    ContentType: str
    Created: str
    CurrentOwnerLookupId: str = OutputField(example_values=["17"])
    DueDate: str = OutputField(example_values=["2022-08-04T12:38:45Z"])
    Duration: str
    Edit: str
    EditorLookupId: str
    FolderChildCount: str
    ItemChildCount: str
    LinkTitle: str
    LinkTitleNoMenu: str
    Manufacturer: str = OutputField(example_values=["Test-Manufacturer-Asset"])
    Model: str = OutputField(example_values=["Model of the Asset"])
    Modified: str
    OrderNumber: str = OutputField(example_values=["1"])
    PreviousOwnerLookupId: str = OutputField(example_values=["18"])
    PurchaseDate: str = OutputField(example_values=["2022-08-04T12:38:45Z"])
    PurchasePrice: float = OutputField(example_values=[1])
    SerialNumber: str = OutputField(example_values=["Test-SerialNumber-Asset"])
    Status: str = OutputField(example_values=["Status of the Asset"])
    Title: str = OutputField(example_values=["Test Title"])
    TravelDuration: str = OutputField(example_values=["0"])
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


class AddItemOutput(ActionOutput):
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


def add_item(params: AddItemParams, soar: SOARClient, asset: Asset) -> AddItemOutput:
    """Add one list item with the legacy Graph request and summary contract."""
    try:
        list_id = encode_path_segment(params.list)
    except ValueError as exc:
        raise ActionFailure(f"Invalid list ID: {exc}") from exc

    endpoint = f"/sites/{asset.site_id}/lists/{list_id}/items"
    with get_graph_client(asset) as graph:
        response = _request_graph(
            graph, "POST", endpoint, content=params.item.encode("utf-8")
        )

    output = AddItemOutput.model_validate(response)
    soar.set_summary(ListItemSummary(sites_count=1))
    return output
