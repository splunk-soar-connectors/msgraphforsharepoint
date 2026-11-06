"""SDK action boundary for the SharePoint get_list action."""

from typing import Annotated

from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _paginate, _request_graph
from ._paths import encode_path_segment
from ._limits import validate_limit
from ..asset import Asset


class GetListSummary(ActionOutput):
    item_count: int = OutputField(example_values=[1])


class GetListParams(Params):
    list: str = Param(
        description="Title or ID of the list to retrieve",
        primary=True,
        cef_types=["sharepoint list id", "sharepoint list name"],
    )
    limit: float | None = Param(description="Maximum number of list items to return")


class CalculatedOutput(PermissiveActionOutput):
    format: str = OutputField(example_values=["dateTime"])
    formula: str = OutputField(example_values=["=[test]"])
    outputType: str = OutputField(example_values=["dateTime"])


class ChoiceOutput(PermissiveActionOutput):
    allowTextEntry: bool = OutputField(example_values=[False])
    displayAs: str = OutputField(example_values=["dropDownMenu"])


class DatetimeOutput(PermissiveActionOutput):
    displayAs: str = OutputField(example_values=["default"])
    format: str = OutputField(example_values=["dateTime"])


class LookupOutput(PermissiveActionOutput):
    allowMultipleValues: bool | None = OutputField()
    allowUnlimitedLength: bool | None = OutputField()
    columnName: str | None = OutputField(example_values=["ItemChildCount"])
    listId: str | None = OutputField()
    primaryLookupColumnId: str | None = OutputField(example_values=["ID"])


class PersonorgroupOutput(PermissiveActionOutput):
    allowMultipleSelection: bool | None = OutputField()
    chooseFromType: str | None = OutputField(example_values=["peopleAndGroups"])
    displayAs: str | None = OutputField(example_values=["nameWithPresence"])


class TextOutput(PermissiveActionOutput):
    allowMultipleLines: bool | None = OutputField()
    appendChangesToExistingText: bool | None = OutputField()
    linesForEditing: float | None = OutputField(example_values=[0])
    maxLength: float | None = OutputField(example_values=[255])
    textType: str | None = OutputField(example_values=["plain"])


class ColumnsOutput(PermissiveActionOutput):
    calculated: CalculatedOutput | None = OutputField()
    choice: ChoiceOutput | None = OutputField()
    columnGroup: str = OutputField(example_values=["Custom Columns"])
    dateTime: DatetimeOutput | None = OutputField()
    description: str = OutputField(example_values=["Test List Description"])
    displayName: str = OutputField(example_values=["ID"])
    enforceUniqueValues: bool | None = OutputField()
    hidden: bool | None = OutputField()
    id: str = OutputField(example_values=["1d22ea11-1e32-424e-89ab-9fedbadb6ce1"])
    indexed: bool | None = OutputField()
    lookup: LookupOutput | None = OutputField()
    name: str = OutputField(example_values=["ID"])
    personOrGroup: PersonorgroupOutput | None = OutputField()
    readOnly: bool | None = OutputField()
    required: bool | None = OutputField()
    text: TextOutput | None = OutputField()


class UserOutput(PermissiveActionOutput):
    displayName: str = OutputField(example_values=["Test User"])
    email: str = OutputField(
        cef_types=["email"], example_values=["test_user@tenant-name.ontest.com"]
    )
    id: str = OutputField(example_values=["eeb3645f-df19-47a1-8e8c-fcd234cb5f6f"])


class CreatedbyOutput(PermissiveActionOutput):
    user: UserOutput


class ContenttypeOutput(PermissiveActionOutput):
    id: str = OutputField(
        example_values=[
            "0x01008C9AE9AA9A043D48B717AB18E1E7180E00F8FCD4A1A57C3043B42193515148F5EC"
        ]
    )
    name: str = OutputField(example_values=["Item"])


class InterviewersOutput(PermissiveActionOutput):
    Email: str = OutputField(example_values=["test@testuser.com"])
    LookupId: float = OutputField(example_values=[18])
    LookupValue: str = OutputField(example_values=["test"])


class FieldsOutput(PermissiveActionOutput):
    etag: Annotated[str | None, OutputField(alias="@odata.etag")] = None
    AppAuthorLookupId: Annotated[str | None, OutputField(example_values=["8"])] = None
    AppEditorLookupId: Annotated[str | None, OutputField(example_values=["8"])] = None
    ApplicationDate: Annotated[
        str | None, OutputField(example_values=["2022-02-03T08:00:00Z"])
    ] = None
    Attachments: Annotated[bool | None, OutputField()] = None
    AuthorLookupId: Annotated[str | None, OutputField(example_values=["9"])] = None
    ContentType: Annotated[str | None, OutputField(example_values=["Item"])] = None
    Conversation: Annotated[
        str | None, OutputField(example_values=["I'd like access, please."])
    ] = None
    Created: Annotated[
        str | None, OutputField(example_values=["2022-02-08T12:29:27Z"])
    ] = None
    Edit: Annotated[str | None, OutputField()] = None
    EditorLookupId: Annotated[str | None, OutputField(example_values=["9"])] = None
    FolderChildCount: Annotated[str | None, OutputField(example_values=["0"])] = None
    InterviewDate: Annotated[
        str | None, OutputField(example_values=["2022-02-28T11:30:00Z"])
    ] = None
    Interviewers: Annotated[list[InterviewersOutput] | None, OutputField()] = None
    ItemChildCount: Annotated[str | None, OutputField(example_values=["0"])] = None
    LinkTitle: Annotated[str | None, OutputField(example_values=["List Item 1"])] = None
    LinkTitleNoMenu: Annotated[
        str | None, OutputField(example_values=["List Item 1"])
    ] = None
    Modified: Annotated[
        str | None, OutputField(example_values=["2022-02-08T12:29:27Z"])
    ] = None
    Notes: Annotated[str | None, OutputField(example_values=["Test Notes"])] = None
    PermissionLevelRequested: Annotated[
        float | None, OutputField(example_values=[8])
    ] = None
    PhoneScreenDate: Annotated[
        str | None, OutputField(example_values=["2022-02-15T14:00:00Z"])
    ] = None
    PhoneScreenerLookupId: Annotated[str | None, OutputField(example_values=["17"])] = (
        None
    )
    Position: Annotated[str | None, OutputField(example_values=["Designer"])] = None
    Progress: Annotated[str | None, OutputField(example_values=["Active"])] = None
    PropagateAcl: Annotated[bool | None, OutputField(example_values=[False])] = None
    RecruiterLookupId: Annotated[str | None, OutputField(example_values=["19"])] = None
    ReqByUserLookupId: Annotated[str | None, OutputField(example_values=["10"])] = None
    ReqForUserLookupId: Annotated[str | None, OutputField(example_values=["10"])] = None
    RequestDate: Annotated[
        str | None, OutputField(example_values=["2022-08-04T12:14:03Z"])
    ] = None
    RequestedByDisplayNameDisp: Annotated[
        str | None, OutputField(example_values=["Test User"])
    ] = None
    RequestedForDisplayNameDisp: Annotated[
        str | None, OutputField(example_values=["Test User"])
    ] = None
    StatusDisp: Annotated[str | None, OutputField(example_values=["0"])] = None
    Title: Annotated[str | None, OutputField(example_values=["List Item 1"])] = None
    ComplianceFlags: Annotated[str | None, OutputField(alias="_ComplianceFlags")] = None
    ComplianceTag: Annotated[str | None, OutputField(alias="_ComplianceTag")] = None
    ComplianceTagUserId: Annotated[
        str | None, OutputField(alias="_ComplianceTagUserId")
    ] = None
    ComplianceTagWrittenTime: Annotated[
        str | None, OutputField(alias="_ComplianceTagWrittenTime")
    ] = None
    UIVersionString: Annotated[
        str | None, OutputField(example_values=["1.0"], alias="_UIVersionString")
    ] = None
    id: Annotated[str | None, OutputField(example_values=["1"])] = None


class ApplicationOutput(PermissiveActionOutput):
    displayName: str = OutputField(example_values=["test"])
    id: str = OutputField(example_values=["71b307af-1dcb-4e39-9640-5129afc83162"])


class LastmodifiedbyOutput(PermissiveActionOutput):
    user: UserOutput


class ItemLastModifiedByOutput(PermissiveActionOutput):
    application: ApplicationOutput
    user: UserOutput


class ParentreferenceOutput(PermissiveActionOutput):
    siteId: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa"
        ]
    )


class ItemParentReferenceOutput(PermissiveActionOutput):
    id: str = OutputField(cef_types=["sharepoint item id"])
    siteId: str = OutputField()


class ItemsOutput(PermissiveActionOutput):
    etag: str = OutputField(alias="@odata.etag")
    contentType: ContenttypeOutput
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2022-02-08T12:29:27Z"])
    eTag: str = OutputField(example_values=['"fe7e1a7c-a66a-4944-b1f1-2b7c7499603c,1"'])
    fields: FieldsOutput
    fields_context: str = OutputField(alias="fields@odata.context", cef_types=["url"])
    id: str = OutputField(example_values=["1"])
    lastModifiedBy: ItemLastModifiedByOutput
    lastModifiedDateTime: str = OutputField(example_values=["2022-02-08T12:29:27Z"])
    parentReference: ItemParentReferenceOutput
    webUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/TestSiteName/Lists/Test%20List%20Name/1_.000"
        ],
    )


class ListOutput(PermissiveActionOutput):
    contentTypesEnabled: bool
    hidden: bool
    template: str = OutputField(example_values=["genericList"])


class GetListOutput(PermissiveActionOutput):
    context: str = OutputField(alias="@odata.context", cef_types=["url"])
    etag: str = OutputField(alias="@odata.etag")
    columns: list[ColumnsOutput]
    columns_context: str = OutputField(alias="columns@odata.context", cef_types=["url"])
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2022-02-08T12:29:09Z"])
    description: str = OutputField(example_values=["Test List Description"])
    displayName: str = OutputField(
        cef_types=["sharepoint list name"],
        example_values=["Test List Name"],
        column_name="List Name",
    )
    eTag: str = OutputField(example_values=['"4961c496-52c1-49bd-b1fa-e1b2e976256c,5"'])
    id: str = OutputField(
        cef_types=["sharepoint list id"],
        example_values=["4961c496-52c1-49bd-b1fa-e1b2e976256c"],
        column_name="List ID",
    )
    items: list[ItemsOutput]
    items_context: str = OutputField(alias="items@odata.context", cef_types=["url"])
    lastModifiedBy: LastmodifiedbyOutput
    lastModifiedDateTime: str = OutputField(example_values=["2022-02-16T06:03:09Z"])
    list: ListOutput
    name: str = OutputField(example_values=["Test List Name"])
    parentReference: ParentreferenceOutput
    webUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/TestSiteName/Lists/Test%20List%20Name"
        ],
    )


def get_list(params: GetListParams, soar: SOARClient, asset: Asset) -> GetListOutput:
    """Retrieve one list, its columns, and its fields-expanded items."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving a list from specific site"
        )

    try:
        limit = validate_limit(params.limit)
    except ValueError as exc:
        raise ActionFailure(str(exc)) from exc
    try:
        encoded_list_id = encode_path_segment(params.list)
    except ValueError as exc:
        raise ActionFailure(f"Invalid list ID: {exc}") from exc

    endpoint = f"/sites/{asset.site_id}/lists/{encoded_list_id}"
    with get_graph_client(asset) as graph:
        list_info = _request_graph(graph, "GET", endpoint, params={"expand": "columns"})
        items = _paginate(
            graph,
            f"{endpoint}/items",
            params={"expand": "fields"},
            limit=limit,
        )

    list_info["items"] = items

    output = GetListOutput.model_validate(list_info)
    soar.set_summary(GetListSummary(item_count=len(items)))
    return output
