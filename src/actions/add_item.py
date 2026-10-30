"""SDK action boundary for the SharePoint add_item action."""

from typing import Annotated
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _request_graph
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


class ContenttypeOutput(PermissiveActionOutput):
    id: str
    name: str


class UserOutput(PermissiveActionOutput):
    displayName: str


class CreatedbyOutput(PermissiveActionOutput):
    user: UserOutput


class FieldsOutput(PermissiveActionOutput):
    etag: Annotated[str | None, OutputField(alias="@odata.etag")] = None
    AppAuthorLookupId: Annotated[str | None, OutputField()] = None
    AppEditorLookupId: Annotated[str | None, OutputField()] = None
    Approved: Annotated[bool | None, OutputField()] = None
    AssetType: Annotated[str | None, OutputField(example_values=["Laptop"])] = None
    Attachments: Annotated[bool | None, OutputField()] = None
    AuthorLookupId: Annotated[str | None, OutputField()] = None
    Color: Annotated[str | None, OutputField(example_values=["Color of the Asset"])] = (
        None
    )
    Complete: Annotated[bool | None, OutputField(example_values=[False])] = None
    ConditionNotes: Annotated[
        str | None, OutputField(example_values=["Note for the Asset"])
    ] = None
    ContentType: Annotated[str | None, OutputField()] = None
    Created: Annotated[str | None, OutputField()] = None
    CurrentOwnerLookupId: Annotated[str | None, OutputField(example_values=["17"])] = (
        None
    )
    DueDate: Annotated[
        str | None, OutputField(example_values=["2022-08-04T12:38:45Z"])
    ] = None
    Duration: Annotated[str | None, OutputField()] = None
    Edit: Annotated[str | None, OutputField()] = None
    EditorLookupId: Annotated[str | None, OutputField()] = None
    FolderChildCount: Annotated[str | None, OutputField()] = None
    ItemChildCount: Annotated[str | None, OutputField()] = None
    LinkTitle: Annotated[str | None, OutputField()] = None
    LinkTitleNoMenu: Annotated[str | None, OutputField()] = None
    Manufacturer: Annotated[
        str | None, OutputField(example_values=["Test-Manufacturer-Asset"])
    ] = None
    Model: Annotated[str | None, OutputField(example_values=["Model of the Asset"])] = (
        None
    )
    Modified: Annotated[str | None, OutputField()] = None
    OrderNumber: Annotated[str | None, OutputField(example_values=["1"])] = None
    PreviousOwnerLookupId: Annotated[str | None, OutputField(example_values=["18"])] = (
        None
    )
    PurchaseDate: Annotated[
        str | None, OutputField(example_values=["2022-08-04T12:38:45Z"])
    ] = None
    PurchasePrice: Annotated[float | None, OutputField(example_values=[1])] = None
    SerialNumber: Annotated[
        str | None, OutputField(example_values=["Test-SerialNumber-Asset"])
    ] = None
    Status: Annotated[
        str | None, OutputField(example_values=["Status of the Asset"])
    ] = None
    Title: Annotated[str | None, OutputField(example_values=["Test Title"])] = None
    TravelDuration: Annotated[str | None, OutputField(example_values=["0"])] = None
    ComplianceFlags: Annotated[str | None, OutputField(alias="_ComplianceFlags")] = None
    ComplianceTag: Annotated[str | None, OutputField(alias="_ComplianceTag")] = None
    ComplianceTagUserId: Annotated[
        str | None, OutputField(alias="_ComplianceTagUserId")
    ] = None
    ComplianceTagWrittenTime: Annotated[
        str | None, OutputField(alias="_ComplianceTagWrittenTime")
    ] = None
    UIVersionString: Annotated[str | None, OutputField(alias="_UIVersionString")] = None
    id: Annotated[str | None, OutputField()] = None


class ApplicationOutput(PermissiveActionOutput):
    displayName: str
    id: str


class LastmodifiedbyOutput(PermissiveActionOutput):
    application: ApplicationOutput
    user: UserOutput


class ParentreferenceOutput(PermissiveActionOutput):
    id: str = OutputField(example_values=["a86797a9-c9a9-47e7-891b-8413b2d758fc"])
    siteId: str


class AddItemOutput(PermissiveActionOutput):
    odata_context: Annotated[
        str | None, OutputField(alias="@odata.context", cef_types=["url"])
    ] = None
    odata_etag: Annotated[str | None, OutputField(alias="@odata.etag")] = None
    contentType: ContenttypeOutput
    createdBy: CreatedbyOutput
    createdDateTime: str
    eTag: str
    fields: FieldsOutput
    fields_odata_context: Annotated[
        str | None, OutputField(alias="fields@odata.context", cef_types=["url"])
    ] = None
    id: str = OutputField(cef_types=["sharepoint item id"], column_name="ID")
    lastModifiedBy: LastmodifiedbyOutput
    lastModifiedDateTime: str
    parentReference: ParentreferenceOutput
    webUrl: str = OutputField(cef_types=["url"])


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
