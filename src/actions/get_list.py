"""SDK action boundary for the SharePoint get_list action."""

import httpx
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
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
    etag: str = OutputField(alias="@odata.etag")
    AppAuthorLookupId: str = OutputField(example_values=["8"])
    AppEditorLookupId: str = OutputField(example_values=["8"])
    ApplicationDate: str = OutputField(example_values=["2022-02-03T08:00:00Z"])
    Attachments: bool
    AuthorLookupId: str = OutputField(example_values=["9"])
    ContentType: str = OutputField(example_values=["Item"])
    Conversation: str = OutputField(example_values=["I'd like access, please."])
    Created: str = OutputField(example_values=["2022-02-08T12:29:27Z"])
    Edit: str
    EditorLookupId: str = OutputField(example_values=["9"])
    FolderChildCount: str = OutputField(example_values=["0"])
    InterviewDate: str = OutputField(example_values=["2022-02-28T11:30:00Z"])
    Interviewers: list[InterviewersOutput]
    ItemChildCount: str = OutputField(example_values=["0"])
    LinkTitle: str = OutputField(example_values=["List Item 1"])
    LinkTitleNoMenu: str = OutputField(example_values=["List Item 1"])
    Modified: str = OutputField(example_values=["2022-02-08T12:29:27Z"])
    Notes: str = OutputField(example_values=["Test Notes"])
    PermissionLevelRequested: float = OutputField(example_values=[8])
    PhoneScreenDate: str = OutputField(example_values=["2022-02-15T14:00:00Z"])
    PhoneScreenerLookupId: str = OutputField(example_values=["17"])
    Position: str = OutputField(example_values=["Designer"])
    Progress: str = OutputField(example_values=["Active"])
    PropagateAcl: bool = OutputField(example_values=[False])
    RecruiterLookupId: str = OutputField(example_values=["19"])
    ReqByUserLookupId: str = OutputField(example_values=["10"])
    ReqForUserLookupId: str = OutputField(example_values=["10"])
    RequestDate: str = OutputField(example_values=["2022-08-04T12:14:03Z"])
    RequestedByDisplayNameDisp: str = OutputField(example_values=["Test User"])
    RequestedForDisplayNameDisp: str = OutputField(example_values=["Test User"])
    StatusDisp: str = OutputField(example_values=["0"])
    Title: str = OutputField(example_values=["List Item 1"])
    ComplianceFlags: str = OutputField(alias="_ComplianceFlags")
    ComplianceTag: str = OutputField(alias="_ComplianceTag")
    ComplianceTagUserId: str = OutputField(alias="_ComplianceTagUserId")
    ComplianceTagWrittenTime: str = OutputField(alias="_ComplianceTagWrittenTime")
    UIVersionString: str = OutputField(example_values=["1.0"], alias="_UIVersionString")
    id: str = OutputField(example_values=["1"])


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
        cef_types=["sharepoint list name"], example_values=["Test List Name"]
    )
    eTag: str = OutputField(example_values=['"4961c496-52c1-49bd-b1fa-e1b2e976256c,5"'])
    id: str = OutputField(
        cef_types=["sharepoint list id"],
        example_values=["4961c496-52c1-49bd-b1fa-e1b2e976256c"],
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
