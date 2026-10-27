"""Explicit registration for ordinary SharePoint connector actions."""

from soar_sdk.app import App
from .copy_drive_item import copy_drive_item
from .create_folder import create_folder
from .folder_items import list_folder_items, FolderItemsSummary
from .drives import list_drives, DrivesSummary
from .drive_children import list_drive_children, DriveChildrenSummary
from .sites import list_sites, SitesSummary
from .list_lists import list_lists, ListListsSummary
from .get_list import get_list, GetListSummary
from .add_item import add_item, ListItemSummary as AddItemSummary
from .update_item import update_item, ListItemSummary as UpdateItemSummary
from .get_file import get_file, GetFileSummary
from .remove_file import remove_file
from .remove_folder import remove_folder


def register_actions(app: App) -> App:
    app.register_action(
        action=copy_drive_item,
        description="Using SharePoint Site ID app config value, and given source_drive_id, copy source_item_id into a folder identified with dest values",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose="While copying the file if file_name is provided without file extension, the copied file will not have any extension.",
    )
    app.register_action(
        action=create_folder,
        description="Create new Drive item Folder using SharePoint site in asset config and provided Parent Item ID",
        action_type="generic",
        read_only=False,
        render_as="table",
    )
    app.register_action(
        action=list_folder_items,
        description="List items in a folder",
        action_type="investigate",
        render_as="table",
        verbose="List all direct children in a folder.",
        summary_type=FolderItemsSummary,
    )
    app.register_action(
        action=list_drives,
        description="Fetch the available drives (libraries) under a SharePoint site",
        action_type="investigate",
        render_as="table",
        verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
        summary_type=DrivesSummary,
    )
    app.register_action(
        action=list_drive_children,
        description="List the items in a drive folder by drive ID or search for a specific file name if provided",
        action_type="investigate",
        render_as="table",
        summary_type=DriveChildrenSummary,
    )
    app.register_action(
        action=list_sites,
        description="Fetch the details of the SharePoint sites",
        action_type="investigate",
        render_as="table",
        verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
        summary_type=SitesSummary,
    )
    app.register_action(
        action=list_lists,
        description="Fetch the available lists under a SharePoint site",
        action_type="investigate",
        render_as="table",
        verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
        summary_type=ListListsSummary,
    )
    app.register_action(
        action=get_list,
        description="Retrieves a list from a SharePoint Site",
        action_type="investigate",
        render_as="table",
        verbose="The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.",
        summary_type=GetListSummary,
    )
    app.register_action(
        action=add_item,
        description="Add an item to a list on a SharePoint Site",
        action_type="generic",
        read_only=False,
        render_as="table",
        summary_type=AddItemSummary,
    )
    app.register_action(
        action=update_item,
        description="Update an item in a list on a SharePoint Site",
        action_type="generic",
        read_only=False,
        render_as="table",
        summary_type=UpdateItemSummary,
    )
    app.register_action(
        action=get_file,
        description="Retrieves a file from a SharePoint site",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose="The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.",
        summary_type=GetFileSummary,
    )
    app.register_action(
        action=remove_file,
        description="Removes a file from a SharePoint site",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose="The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.",
    )
    app.register_action(
        action=remove_folder,
        description="Removes a folder from a SharePoint site",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose="The 'folder path' parameter will be considered from the root of the document library specified in drive_id.",
    )
    return app
