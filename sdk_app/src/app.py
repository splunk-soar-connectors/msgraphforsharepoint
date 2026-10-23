from typing import Union
from collections.abc import Iterator
from zoneinfo import ZoneInfo
from soar_sdk.abstract import SOARClient
from soar_sdk.app import App
from soar_sdk.params import Param, Params, OnPollParams, OnESPollParams
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.asset import BaseAsset, AssetField, FieldCategory
from soar_sdk.logging import getLogger
from soar_sdk.models.container import Container
from soar_sdk.models.artifact import Artifact
from soar_sdk.models.finding import Finding
from soar_sdk.models.attachment_input import AttachmentInput

from .actions.sites import SitesSummary, list_sites as list_sites_impl
from .actions.drives import (
    DrivesSummary,
    ListDrivesOutput,
    list_drives as list_drives_impl,
)
from .actions.drive_children import (
    DriveChildrenSummary,
    ListDriveChildrenOutput,
    list_drive_children as list_drive_children_impl,
)
from .actions.folder_items import (
    FolderItemsSummary,
    ListFolderItemsOutput,
    list_folder_items as list_folder_items_impl,
)
from .actions.copy_drive_item import (
    CopyDriveItemOutput,
    copy_drive_item as copy_drive_item_impl,
)
from .actions.create_folder import create_folder as create_folder_impl
from .actions.lists import (
    GetListSummary,
    ListListsSummary,
    get_list as get_list_impl,
    list_lists as list_lists_impl,
)
from .test_connectivity import run_test_connectivity

logger = getLogger()


class Asset(BaseAsset):
    tenant_id: str = AssetField(
        description="Tenant ID", category=FieldCategory.CONNECTIVITY
    )
    site_id: str | None = AssetField(
        description="SharePoint Site ID", category=FieldCategory.CONNECTIVITY
    )
    endpoint_test_connectivity: str | None = AssetField(
        description="Endpoint for test connectivity (Valid format: /sites/{hostname}:/{site-server-relative-url})",
        default="/sites/root",
        category=FieldCategory.CONNECTIVITY,
    )
    admin_consent: bool | None = AssetField(
        description="Admin Consent Already Provided",
        category=FieldCategory.CONNECTIVITY,
    )
    client_id: str = AssetField(
        description="Client/Application ID", category=FieldCategory.CONNECTIVITY
    )
    client_secret: str = AssetField(
        description="Client Secret",
        sensitive=True,
        category=FieldCategory.CONNECTIVITY,
    )


app = App(
    name="MS Graph for SharePoint",
    app_type="reputation",
    logo="logo_msgraphforsharepoint.svg",
    logo_dark="logo_msgraphforsharepoint_dark.svg",
    product_vendor="Microsoft",
    product_name="SharePoint",
    publisher="Splunk",
    appid="7963f3ef-b527-40e5-a704-392c56f0a88d",
    fips_compliant=True,
    python_version="3.13",
    min_phantom_version="8.7.0",
    encrypt_cache_state=True,
    encrypt_ingest_state=True,
    asset_cls=Asset,
)


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    run_test_connectivity(soar, asset)


class CopyDriveItemParams(Params):
    source_item_id: str = Param(
        description="ID for drive item that needs to be copied",
        primary=True,
        cef_types=["sharepoint drive item id"],
    )
    source_drive_id: str | None = Param(
        description="Drive ID that contains the source item to copy. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    dest_drive_id: str | None = Param(
        description="Drive ID that contains target folder to copy item to. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    dest_folder_id: str = Param(
        description="ID of target folder to copy drive item to",
        primary=True,
        cef_types=["sharepoint drive item id"],
    )
    file_name: str | None = Param(
        description="Optional new folder/file name for the copy. If not provided will use the original name"
    )


@app.action(
    description="Using SharePoint Site ID app config value, and given source_drive_id, copy source_item_id into a folder identified with dest values",
    action_type="generic",
    read_only=False,
    verbose="While copying the file if file_name is provided without file extension, the copied file will not have any extension.",
)
def copy_drive_item(
    params: CopyDriveItemParams, soar: SOARClient, asset: Asset
) -> CopyDriveItemOutput:
    return copy_drive_item_impl(params, soar, asset)


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


class CommentingdisabledOutput(ActionOutput):
    isDisabled: bool


class CommentsettingsOutput(ActionOutput):
    commentingDisabled: CommentingdisabledOutput


class ApplicationOutput(ActionOutput):
    displayName: str = OutputField(example_values=["sharepoint_test"])
    id: str = OutputField(example_values=["71b307af-1dcb-4e39-9640-5129afc83162"])


class UserOutput(ActionOutput):
    displayName: str = OutputField(example_values=["SharePoint App"])


class CreatedbyOutput(ActionOutput):
    application: ApplicationOutput
    user: UserOutput


class FilesysteminfoOutput(ActionOutput):
    createdDateTime: str = OutputField(example_values=["2023-10-25T08:55:48Z"])
    lastModifiedDateTime: str = OutputField(example_values=["2023-10-25T08:55:48Z"])


class FolderOutput(ActionOutput):
    childCount: float = OutputField(example_values=[0])


class LastmodifiedbyOutput(ActionOutput):
    application: ApplicationOutput
    user: UserOutput


class SharepointidsOutput(ActionOutput):
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


class ParentreferenceOutput(ActionOutput):
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


class SharedOutput(ActionOutput):
    scope: str = OutputField(example_values=["unknown"])


class CreateFolderOutput(ActionOutput):
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


@app.action(
    description="Create new Drive item Folder using SharePoint site in asset config and provided Parent Item ID",
    action_type="generic",
    read_only=False,
)
def create_folder(
    params: CreateFolderParams, soar: SOARClient, asset: Asset
) -> CreateFolderOutput:
    return create_folder_impl(params, soar, asset)


class ListFolderItemsParams(Params):
    drive_id: str | None = Param(
        description="ID for drive that folder lives in. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    folder_path: str = Param(description="Path of the folder to query", primary=True)




@app.action(
    description="List items in a folder",
    action_type="investigate",
    verbose="List all direct children in a folder.",
    summary_type=FolderItemsSummary,
)
def list_folder_items(
    params: ListFolderItemsParams, soar: SOARClient, asset: Asset
) -> list[ListFolderItemsOutput]:
    return list_folder_items_impl(params, soar, asset)


class ListDrivesParams(Params):
    limit: float | None = Param(description="Maximum number of drives to return")




@app.action(
    description="Fetch the available drives (libraries) under a SharePoint site",
    action_type="investigate",
    verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
    summary_type=DrivesSummary,
)
def list_drives(
    params: ListDrivesParams, soar: SOARClient, asset: Asset
) -> list[ListDrivesOutput]:
    return list_drives_impl(params, soar, asset)


class ListDriveChildrenParams(Params):
    drive_id: str | None = Param(
        description="ID of drive to list. If no id is specified the default drive will be queried",
        primary=True,
        cef_types=["sharepoint drive id"],
    )




@app.action(
    description="List the items in a drive folder by drive ID or search for a specific file name if provided",
    action_type="investigate",
    summary_type=DriveChildrenSummary,
)
def list_drive_children(
    params: ListDriveChildrenParams, soar: SOARClient, asset: Asset
) -> list[ListDriveChildrenOutput]:
    return list_drive_children_impl(params, soar, asset)


class ListSitesParams(Params):
    limit: float | None = Param(description="Maximum number of sites to return")


class SitecollectionOutput(ActionOutput):
    hostname: str = OutputField(
        cef_types=["host name"], example_values=["tenant-name.sharepoint.com"]
    )


class ListSitesOutput(ActionOutput):
    createdDateTime: str = OutputField(example_values=["2016-10-31T20:25:06Z"])
    displayName: str = OutputField(example_values=["Test Site Name"])
    id: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,595384ee-13aa-49d1-814b-00ed3e024cde,70abfe37-8aa1-4168-b83e-41b6e9721509"
        ]
    )
    isPersonalSite: bool
    lastModifiedDateTime: str = OutputField(
        example_values=["2022-02-16T12:12:25.9162131Z"]
    )
    name: str = OutputField(example_values=["Test Site Name"])
    siteCollection: SitecollectionOutput
    webUrl: str = OutputField(
        cef_types=["url"],
        example_values=["https://test-tenant-name.sharepoint.com/search"],
    )


@app.action(
    description="Fetch the details of the SharePoint sites",
    action_type="investigate",
    verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
    summary_type=SitesSummary,
)
def list_sites(
    params: ListSitesParams, soar: SOARClient, asset: Asset
) -> list[ListSitesOutput]:
    return list_sites_impl(params, soar, asset)


class ListListsParams(Params):
    limit: float | None = Param(description="Maximum number of sites to return")


class UserOutput(ActionOutput):
    displayName: str = OutputField(example_values=["Test User"])
    email: str = OutputField(
        cef_types=["email"], example_values=["test_user@tenant-name.ontest.com"]
    )
    id: str = OutputField(example_values=["eeb3645f-df19-47a1-8e8c-fcd234cb5f6f"])


class CreatedbyOutput(ActionOutput):
    user: UserOutput


class LastmodifiedbyOutput(ActionOutput):
    user: UserOutput


class ListOutput(ActionOutput):
    contentTypesEnabled: bool
    hidden: bool
    template: str = OutputField(example_values=["genericList"])


class ParentreferenceOutput(ActionOutput):
    siteId: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa"
        ]
    )


class ListListsOutput(ActionOutput):
    etag: str = OutputField(alias="@odata.etag")
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2022-02-24T05:38:53Z"])
    description: str = OutputField(example_values=["Test List Description"])
    displayName: str = OutputField(
        cef_types=["sharepoint list name"], example_values=["ListName"]
    )
    eTag: str = OutputField(example_values=['"4896b66a-659c-4fce-a148-0b26bd718f68,5"'])
    id: str = OutputField(
        cef_types=["sharepoint list id"],
        example_values=["4896b66a-659c-4fce-a148-0b26bd718f68"],
    )
    lastModifiedBy: LastmodifiedbyOutput
    lastModifiedDateTime: str = OutputField(example_values=["2022-03-03T13:43:06Z"])
    list: ListOutput
    name: str = OutputField(example_values=["ListName"])
    parentReference: ParentreferenceOutput
    webUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/SiteName/Lists/ListName"
        ],
    )


@app.action(
    description="Fetch the available lists under a SharePoint site",
    action_type="investigate",
    verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
    summary_type=ListListsSummary,
)
def list_lists(
    params: ListListsParams, soar: SOARClient, asset: Asset
) -> list[ListListsOutput]:
    return list_lists_impl(params, soar, asset)


class GetListParams(Params):
    list: str = Param(
        description="Title or ID of the list to retrieve",
        primary=True,
        cef_types=["sharepoint list id", "sharepoint list name"],
    )
    limit: float | None = Param(description="Maximum number of list items to return")


class CalculatedOutput(ActionOutput):
    format: str = OutputField(example_values=["dateTime"])
    formula: str = OutputField(example_values=["=[test]"])
    outputType: str = OutputField(example_values=["dateTime"])


class ChoiceOutput(ActionOutput):
    allowTextEntry: bool = OutputField(example_values=[False])
    displayAs: str = OutputField(example_values=["dropDownMenu"])


class DatetimeOutput(ActionOutput):
    displayAs: str = OutputField(example_values=["default"])
    format: str = OutputField(example_values=["dateTime"])


class LookupOutput(ActionOutput):
    allowMultipleValues: bool | None = OutputField()
    allowUnlimitedLength: bool | None = OutputField()
    columnName: str | None = OutputField(example_values=["ItemChildCount"])
    listId: str | None = OutputField()
    primaryLookupColumnId: str | None = OutputField(example_values=["ID"])


class PersonorgroupOutput(ActionOutput):
    allowMultipleSelection: bool | None = OutputField()
    chooseFromType: str | None = OutputField(example_values=["peopleAndGroups"])
    displayAs: str | None = OutputField(example_values=["nameWithPresence"])


class TextOutput(ActionOutput):
    allowMultipleLines: bool | None = OutputField()
    appendChangesToExistingText: bool | None = OutputField()
    linesForEditing: float | None = OutputField(example_values=[0])
    maxLength: float | None = OutputField(example_values=[255])
    textType: str | None = OutputField(example_values=["plain"])


class ColumnsOutput(ActionOutput):
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


class UserOutput(ActionOutput):
    displayName: str = OutputField(example_values=["Test User"])
    email: str = OutputField(
        cef_types=["email"], example_values=["test_user@tenant-name.ontest.com"]
    )
    id: str = OutputField(example_values=["eeb3645f-df19-47a1-8e8c-fcd234cb5f6f"])


class CreatedbyOutput(ActionOutput):
    user: UserOutput


class ContenttypeOutput(ActionOutput):
    id: str = OutputField(
        example_values=[
            "0x01008C9AE9AA9A043D48B717AB18E1E7180E00F8FCD4A1A57C3043B42193515148F5EC"
        ]
    )
    name: str = OutputField(example_values=["Item"])


class InterviewersOutput(ActionOutput):
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


class ApplicationOutput(ActionOutput):
    displayName: str = OutputField(example_values=["test"])
    id: str = OutputField(example_values=["71b307af-1dcb-4e39-9640-5129afc83162"])


class LastmodifiedbyOutput(ActionOutput):
    user: UserOutput


class ItemLastModifiedByOutput(ActionOutput):
    application: ApplicationOutput
    user: UserOutput


class ParentreferenceOutput(ActionOutput):
    siteId: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa"
        ]
    )


class ItemParentReferenceOutput(ActionOutput):
    id: str = OutputField(cef_types=["sharepoint item id"])
    siteId: str = OutputField()


class ItemsOutput(ActionOutput):
    etag: str = OutputField(alias="@odata.etag")
    contentType: ContenttypeOutput
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2022-02-08T12:29:27Z"])
    eTag: str = OutputField(example_values=['"fe7e1a7c-a66a-4944-b1f1-2b7c7499603c,1"'])
    fields: FieldsOutput
    fields_context: str = OutputField(
        alias="fields@odata.context", cef_types=["url"]
    )
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


class ListOutput(ActionOutput):
    contentTypesEnabled: bool
    hidden: bool
    template: str = OutputField(example_values=["genericList"])


class GetListOutput(ActionOutput):
    context: str = OutputField(alias="@odata.context", cef_types=["url"])
    etag: str = OutputField(alias="@odata.etag")
    columns: list[ColumnsOutput]
    columns_context: str = OutputField(
        alias="columns@odata.context", cef_types=["url"]
    )
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


@app.action(
    description="Retrieves a list from a SharePoint Site",
    action_type="investigate",
    verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
    summary_type=GetListSummary,
)
def get_list(params: GetListParams, soar: SOARClient, asset: Asset) -> GetListOutput:
    return get_list_impl(params, soar, asset)


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


class FieldsOutput(ActionOutput):
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


@app.action(
    description="Add an item to a list on a SharePoint Site",
    action_type="generic",
    read_only=False,
)
def add_item(params: AddItemParams, soar: SOARClient, asset: Asset) -> AddItemOutput:
    raise NotImplementedError()


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


class FieldsOutput(ActionOutput):
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


@app.action(
    description="Update an item in a list on a SharePoint Site",
    action_type="generic",
    read_only=False,
)
def update_item(
    params: UpdateItemParams, soar: SOARClient, asset: Asset
) -> UpdateItemOutput:
    raise NotImplementedError()


class GetFileParams(Params):
    file_name: str = Param(description="File name to retrieve")
    file_path: str = Param(description="Folder path on site")
    drive_id: str | None = Param(
        description="The file is searched in this drive. If no drive is specified, the default drive will be used",
        cef_types=["sharepoint drive id"],
    )


class GraphOutput(ActionOutput):
    downloadUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/TestSiteName/_layouts/15/download.aspx?UniqueId=c743b2e0-36ec-4c8a-9ce0-190c2fd4dd97&Translate=false&tempauth=eyJ0eXAiOiJKV1QiLCJhbGciOiJub0&ApiVersion=2.0"
        ],
    )


class MicrosoftOutput(ActionOutput):
    graph: GraphOutput


class OdataOutput(ActionOutput):
    context: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://graph.test.com/v1.0/$metadata#sites('tenant-name.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fb')/drive/root/$entity"
        ],
    )


class ImageOutput(ActionOutput):
    width: float = OutputField(example_values=[256])
    height: float = OutputField(example_values=[266])


class UserOutput(ActionOutput):
    displayName: str = OutputField(example_values=["Test User"])
    email: str = OutputField(
        cef_types=["email"], example_values=["test_user@tenant-name.ontest.com"]
    )
    id: str = OutputField(example_values=["eeb3645f-df19-47a1-8e8c-fcd234cb5f6f"])


class CreatedbyOutput(ActionOutput):
    user: UserOutput


class HashesOutput(ActionOutput):
    quickXorHash: str = OutputField(example_values=["EIDYEgye8dEx3XhA7xc12GqSwxk="])


class FileOutput(ActionOutput):
    hashes: HashesOutput
    mimeType: str = OutputField(example_values=["text/plain"])


class FilesysteminfoOutput(ActionOutput):
    createdDateTime: str = OutputField(example_values=["2022-02-10T15:25:21Z"])
    lastModifiedDateTime: str = OutputField(example_values=["2022-02-10T15:25:21Z"])


class LastmodifiedbyOutput(ActionOutput):
    user: UserOutput


class ParentreferenceOutput(ActionOutput):
    driveId: str = OutputField(
        cef_types=["sharepoint drive id"],
        example_values=[
            "b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi"
        ],
    )
    driveType: str = OutputField(example_values=["documentLibrary"])
    id: str = OutputField(
        cef_types=["sharepoint drive item id"],
        example_values=["01SNFLYIRDSQLQVWP7EVDKSL3YYUNW6I4G"],
    )
    name: str = OutputField(example_values=["Playbook-Folder"])
    path: str = OutputField(example_values=["/drive/root:/test_folder_name"])
    siteId: str = OutputField(example_values=["dc6f43e9-54fa-4a39-8783-314e3bbbed41"])


class SharedOutput(ActionOutput):
    scope: str = OutputField(example_values=["users"])


class GetFileOutput(ActionOutput):
    microsoft: MicrosoftOutput
    odata: OdataOutput
    image: ImageOutput
    cTag: str = OutputField(
        example_values=['"c:{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1"']
    )
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2022-02-10T15:25:21Z"])
    eTag: str = OutputField(
        example_values=['"{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1"']
    )
    file: FileOutput
    fileSystemInfo: FilesysteminfoOutput
    id: str = OutputField(
        cef_types=["sharepoint drive item id"],
        example_values=["01SNFLYIXAWJB4P2ZWTJGJZYAZBQX5JXMX"],
    )
    lastModifiedBy: LastmodifiedbyOutput
    lastModifiedDateTime: str = OutputField(example_values=["2022-02-10T15:25:21Z"])
    name: str = OutputField(example_values=["test_file_name.txt"])
    parentReference: ParentreferenceOutput
    shared: SharedOutput
    size: float = OutputField(example_values=[1422])
    webUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/TestSiteName/Shared%20Documents/test_folder_name/test_file_name.txt"
        ],
    )


@app.action(
    description="Retrieves a file from a SharePoint site",
    action_type="generic",
    read_only=False,
    verbose="The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.",
)
def get_file(params: GetFileParams, soar: SOARClient, asset: Asset) -> GetFileOutput:
    raise NotImplementedError()


class RemoveFileParams(Params):
    file_name: str = Param(description="File name to remove")
    file_path: str = Param(description="Folder path on site")
    drive_id: str | None = Param(
        description="The file is searched in this drive. If no drive is specified, the default drive will be used"
    )


@app.action(
    description="Removes a file from a SharePoint site",
    action_type="generic",
    read_only=False,
    verbose="The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.",
)
def remove_file(
    params: RemoveFileParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    raise NotImplementedError()


class RemoveFolderParams(Params):
    folder_path: str = Param(description="Folder path on site")
    drive_id: str | None = Param(
        description="The file is searched in this drive. If no drive is specified, the default drive will be used"
    )


@app.action(
    description="Removes a folder from a SharePoint site",
    action_type="generic",
    read_only=False,
    verbose="The 'folder path' parameter will be considered from the root of the document library specified in drive_id.",
)
def remove_folder(
    params: RemoveFolderParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    raise NotImplementedError()


if __name__ == "__main__":
    app.cli()
