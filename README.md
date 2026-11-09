# MS Graph for SharePoint

Publisher: Splunk <br>
Connector Version: 1.5.7 <br>
Product Vendor: Microsoft <br>
Product Name: SharePoint <br>
Minimum Product Version: 8.7.0

This app connects to SharePoint using the MS Graph API to support investigate and generic actions

## Authentication

You will first need to create an application on the Azure AD Admin Portal. Follow the steps outlined
below to do this:

- Navigate to <https://portal.azure.com> in a browser and log in with a Microsoft account

- Select **Azure Active Directory** from the left side menu

- From the left panel, select **App Registrations**

- At the top of the middle section, select **New registration**

- On the next page, give your application a name and select **Register**

- Once the app is created, the below steps need to be taken on the next page:

  - Under **Certificates & secrets** select **New client secret** . Note down this key somewhere
    secure, as it cannot be retrieved after closing the window.

  - Under **Authentication** , select **Add a platform** . In the **Add a platform** window,
    select **Web** . For non-admin consent, add the webhook callback URL printed during **Test
    Connectivity** as a redirect URI. The test waits for consent, so register that URL before
    opening the Microsoft consent link.

  - Under **API Permissions** Click on **Add a permission** .

  - Under the **Microsoft API** section, select **Microsoft Graph** .

  - There are two ways to gives the Application and Delegated permissions to the app.

    1. Permissive mode

       - Sites.Read.All
       - Files.Read.All
       - Files.ReadWrite.All
       - Sites.ReadWrite.All

    1. Restrictive mode

       - Sites.Selected (only Application permission)

       The user will have to configure permissions for each of the sites that they are working
       with. You can find more information
       [here](https://devblogs.microsoft.com/microsoft365dev/controlling-app-access-on-specific-sharepoint-site-collections/)
       . Also, while using this mode 'list sites' action will return the empty list.\
       **Note:** You need **Sites.FullControl.All** Application permission while using the site
       permission endpoint.

  - After making these changes, click **Add permissions** at the bottom of the screen.

- If you are an admin user, then click **Grant admin consent for Phantom** and provide admin
  consent. And configure asset configuration parameter **Admin Consent Already Provided** with
  value **True** .

- If you are a non-admin user, then follow the steps listed below to grant admin consent:

  - Configure an asset configuration parameter **Admin Consent Already Provided** with value
    **False** .
  - Run the **Test Connectivity** .
  - Copy the webhook callback URL printed in the connectivity log and add it as a **Web** redirect
    URI in the app registration. Replace any legacy REST handler redirect URI with this SDK
    webhook URL.
  - Open the Microsoft consent link printed by **Test Connectivity** in a browser. The SOAR
    webhook receives the redirect; the browser does not need to be logged into SOAR.
  - Proceed to log in to the Microsoft site with the admin user.
  - You will be prompted to agree to the permissions requested by the App.
  - If all goes well the browser should instruct you to close the tab.
  - Now go back and check the message on the Test Connectivity dialog box, it should say **Test
    Connectivity Passed** .

## Phantom Asset for SharePoint

When creating an asset for the **MS Graph for SharePoint** app, place the **Application ID** and
**Client secret** of the app created during the previous step in the **Client/Application ID** and
**Client Secret** fields respectively. You can also find **Tenant ID** on the application overview
page. After filling in all the required values, click **SAVE** .

For non-admin consent, the redirect URI is the SDK webhook URL printed in the **Test Connectivity**
log. Register that URL as a **Web** redirect URI in the Microsoft app registration before opening
the consent link. Existing installations must replace the legacy REST handler redirect URI with the
SDK webhook URL.

Additionally, updating the Base URL in the Company Settings is also required. Navigate to
**Administration > Company Settings > Info** to configure the **Base URL For Splunk SOAR** . Then,
select **Save Changes** .

For the asset configuration parameter **SharePoint Site ID** , it should be in the format
**{Hostname},{SPSite-id},{SPWeb-id}** . You can get the **SharePoint Site ID** by running the
**'list site'** action. For more information check out the [Microsoft
documentation](https://docs.microsoft.com/en-us/graph/api/resources/sharepoint?view=graph-rest-1.0#note-for-existing-sharepoint-developers)
.

## Restrictions and Limitations

Some special characters aren't allowed as a SharePoint **list name** and **file/folder name** . If
you have created the list/files with these special characters, SharePoint API will not allow us to
retrieve the list information. For more information about limitations check out the [Microsoft
documentation](https://support.microsoft.com/en-us/kb/905231) .\
As a workaround for lists, we can use the list_id instead of the list_name. Run the 'list lists'
action to get the list_id.

## Generic Microsoft Graph requests

The **make request** action sends one request to Microsoft Graph using the asset's configured
authentication. Supply a relative endpoint beginning with `/v1.0/` or `/beta/`; do not include a
host name. The action returns the HTTP status code and raw response body, including for HTTP error
responses. It does not follow redirects or paginate results. Requests using write methods can
change Microsoft Graph data, subject to the permissions granted to the app registration.

## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the Microsoft servers. Below are the
default ports used by Splunk SOAR.

|         Service Name | Transport Protocol | Port |
|----------------------|--------------------|------|
|         http | tcp | 80 |
|         https | tcp | 443 |

### Configuration variables

This table lists the configuration variables required to operate MS Graph for SharePoint. These variables are specified when configuring a SharePoint asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**tenant_id** | required | string | Tenant ID |
**site_id** | optional | string | SharePoint Site ID |
**endpoint_test_connectivity** | optional | string | Endpoint for test connectivity (Valid format: /sites/{hostname}:/{site-server-relative-url}) |
**admin_consent** | optional | boolean | Admin Consent Already Provided |
**client_id** | required | string | Client/Application ID |
**client_secret** | required | password | Client Secret |

### Supported Actions

[test connectivity](#action-test-connectivity) - test connectivity <br>
[copy drive item](#action-copy-drive-item) - Using SharePoint Site ID app config value, and given source_drive_id, copy source_item_id into a folder identified with dest values <br>
[create folder](#action-create-folder) - Create new Drive item Folder using SharePoint site in asset config and provided Parent Item ID <br>
[list folder items](#action-list-folder-items) - List items in a folder <br>
[list drives](#action-list-drives) - Fetch the available drives (libraries) under a SharePoint site <br>
[list drive children](#action-list-drive-children) - List the items in a drive folder by drive ID or search for a specific file name if provided <br>
[list sites](#action-list-sites) - Fetch the details of the SharePoint sites <br>
[list lists](#action-list-lists) - Fetch the available lists under a SharePoint site <br>
[get list](#action-get-list) - Retrieves a list from a SharePoint Site <br>
[add item](#action-add-item) - Add an item to a list on a SharePoint Site <br>
[update item](#action-update-item) - Update an item in a list on a SharePoint Site <br>
[get file](#action-get-file) - Retrieves a file from a SharePoint site <br>
[remove file](#action-remove-file) - Removes a file from a SharePoint site <br>
[remove folder](#action-remove-folder) - Removes a folder from a SharePoint site <br>
[make request](#action-make-request) - Call Microsoft Graph with the asset's authentication and return status and raw body.

Supply a relative /v1.0/ or /beta/ path. Redirects are not followed. HTTP
error responses are returned as data; invalid input, authentication and
transport failures fail the action. Pagination is not followed.

## action: 'test connectivity'

test connectivity

Type: **test** <br>
Read only: **True**

Basic test for app.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'copy drive item'

Using SharePoint Site ID app config value, and given source_drive_id, copy source_item_id into a folder identified with dest values

Type: **generic** <br>
Read only: **False**

While copying the file if file_name is provided without file extension, the copied file will not have any extension.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**source_item_id** | required | ID for drive item that needs to be copied | string | `sharepoint drive item id` |
**source_drive_id** | optional | Drive ID that contains the source item to copy. If no id is specified the default drive will be used | string | `sharepoint drive id` |
**dest_drive_id** | optional | Drive ID that contains target folder to copy item to. If no id is specified the default drive will be used | string | `sharepoint drive id` |
**dest_folder_id** | required | ID of target folder to copy drive item to | string | `sharepoint drive item id` |
**file_name** | optional | Optional new folder/file name for the copy. If not provided will use the original name | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.source_item_id | string | `sharepoint drive item id` | |
action_result.parameter.source_drive_id | string | `sharepoint drive id` | |
action_result.parameter.dest_drive_id | string | `sharepoint drive id` | |
action_result.parameter.dest_folder_id | string | `sharepoint drive item id` | |
action_result.parameter.file_name | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'create folder'

Create new Drive item Folder using SharePoint site in asset config and provided Parent Item ID

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**parent_item_id** | required | Parent Drive Item ID | string | `sharepoint drive item id` |
**folder_name** | required | Name of newly created folder | string | |
**drive_id** | optional | ID of drive to create folder in. If no id is specified the default drive will be used | string | `sharepoint drive id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.parent_item_id | string | `sharepoint drive item id` | |
action_result.parameter.folder_name | string | | |
action_result.parameter.drive_id | string | `sharepoint drive id` | |
action_result.data.\*.@odata.context | string | | https://test.microsoft.com/v1.0/$metadata#sites('test.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fa')/drive/items('01SNFLYIVBMJQZCZK6ZFAZ5PVEXODNRV3N')/children/$entity |
action_result.data.\*.@odata.etag | string | | "{24A7DBF0-E193-4E0A-A960-ECF5DB994FFF},1" |
action_result.data.\*.cTag | string | | "c:{24A7DBF0-E193-4E0A-A960-ECF5DB994FFF},0" |
action_result.data.\*.commentSettings.commentingDisabled.isDisabled | boolean | | True False |
action_result.data.\*.createdBy.application.displayName | string | | sharepoint_test |
action_result.data.\*.createdBy.application.id | string | | 71b307af-1dcb-4e39-9640-5129afc83162 |
action_result.data.\*.createdBy.user.displayName | string | | SharePoint App |
action_result.data.\*.createdDateTime | string | | 2023-10-25T08:55:48Z |
action_result.data.\*.eTag | string | | "{24A7DBF0-E193-4E0A-A960-ECF5DB994FFF},1" |
action_result.data.\*.fileSystemInfo.createdDateTime | string | | 2023-10-25T08:55:48Z |
action_result.data.\*.fileSystemInfo.lastModifiedDateTime | string | | 2023-10-25T08:55:48Z |
action_result.data.\*.folder.childCount | numeric | | 0 |
action_result.data.\*.folder_name | string | | |
action_result.data.\*.id | string | `sharepoint drive item id` | |
action_result.data.\*.lastModifiedBy.application.displayName | string | | sharepoint_test |
action_result.data.\*.lastModifiedBy.application.id | string | | 71b307af-1dcb-4e39-9640-5129afc83162 |
action_result.data.\*.lastModifiedBy.user.displayName | string | | SharePoint App |
action_result.data.\*.lastModifiedDateTime | string | | 2023-10-25T08:55:48Z |
action_result.data.\*.name | string | | test2 |
action_result.data.\*.webUrl | string | `url` | |
action_result.data.\*.parentReference.driveId | string | `sharepoint drive id` | b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi |
action_result.data.\*.parentReference.driveType | string | | documentLibrary |
action_result.data.\*.parentReference.id | string | `sharepoint drive item id` | 01SNFLYIVBMJQZCZK6ZFAZ5PVEXODNRV3N |
action_result.data.\*.parentReference.path | string | | /drives/b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi/root:/SizeTest-Playbook-Don't Delete |
action_result.data.\*.parentReference.sharepointIds.listId | string | | 498fd15d-ef79-4c0b-8ac4-c4ea27ed8be2 |
action_result.data.\*.parentReference.sharepointIds.listItemUniqueId | string | | 916162a1-5e65-41c9-9ebe-a4bb86d8d76d |
action_result.data.\*.parentReference.sharepointIds.siteId | string | | dc6f43e9-54fa-4a39-8783-314e3bbbed41 |
action_result.data.\*.parentReference.sharepointIds.siteUrl | string | `url` | https://test.sharepoint.com/sites/TestSite |
action_result.data.\*.parentReference.sharepointIds.tenantId | string | | 140fe46d-819d-4b6d-b7ef-1c0a8270f4f0 |
action_result.data.\*.parentReference.sharepointIds.webId | string | | c42b48c4-59b9-48f1-b96e-e8145b5539fa |
action_result.data.\*.shared.scope | string | | unknown |
action_result.data.\*.size | numeric | | 0 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list folder items'

List items in a folder

Type: **investigate** <br>
Read only: **False**

List all direct children in a folder.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**drive_id** | optional | ID for drive that folder lives in. If no id is specified the default drive will be used | string | `sharepoint drive id` |
**folder_path** | required | Path of the folder to query | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.drive_id | string | `sharepoint drive id` | |
action_result.parameter.folder_path | string | | |
action_result.data.\*.name | string | | |
action_result.data.\*.id | string | | |
action_result.data.\*.cTag | string | | |
action_result.data.\*.eTag | string | | |
action_result.data.\*.file.mimeType | string | | video/mp4 |
action_result.data.\*.folder.childCount | numeric | | 5 |
action_result.data.\*.size | numeric | | |
action_result.data.\*.shared.scope | string | | users |
action_result.data.\*.shared.webUrl | string | `url` | |
action_result.data.\*.parentReference.driveType | string | | documentLibrary |
action_result.data.\*.parentReference.id | string | `sharepoint drive item id` | |
action_result.data.\*.parentReference.name | string | | Shared Documents |
action_result.data.\*.parentReference.path | string | | |
action_result.data.\*.parentReference.siteId | string | | |
action_result.data.\*.fileSystemInfo.createdDateTime | string | | |
action_result.data.\*.fileSystemInfo.lastModifiedDateTime | string | | |
action_result.data.\*.createdBy.user.displayName | string | | Test User |
action_result.data.\*.createdBy.user.email | string | `email` | |
action_result.data.\*.createdBy.user.id | string | | |
action_result.data.\*.lastModifiedBy.user.displayName | string | | Test User |
action_result.data.\*.lastModifiedBy.user.email | string | `email` | |
action_result.data.\*.lastModifiedBy.user.id | string | | |
action_result.data.\*.createdDateTime | string | | |
action_result.data.\*.@microsoft.graph.downloadUrl | string | `url` | https://graph.microsoft.com/v1.0/download |
action_result.data.\*.lastModifiedDateTime | string | | |
action_result.summary.items_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list drives'

Fetch the available drives (libraries) under a SharePoint site

Type: **investigate** <br>
Read only: **False**

The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**limit** | optional | Maximum number of drives to return | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.limit | numeric | | |
action_result.data.\*.name | string | | Custom Library |
action_result.data.\*.id | string | | |
action_result.data.\*.owner.user.displayName | string | | Test User |
action_result.data.\*.owner.user.email | string | `email` | |
action_result.data.\*.owner.user.id | string | | |
action_result.data.\*.owner.group.id | string | | |
action_result.data.\*.owner.group.email | string | `email` | |
action_result.data.\*.owner.group.displayName | string | | |
action_result.data.\*.quota.used | numeric | | 8546734 |
action_result.data.\*.quota.state | string | | normal |
action_result.data.\*.quota.total | numeric | | 274877685 |
action_result.data.\*.quota.deleted | numeric | | 0 |
action_result.data.\*.quota.remaining | numeric | | 266330951 |
action_result.data.\*.createdBy.user.displayName | string | | Test User |
action_result.data.\*.createdBy.user.email | string | `email` | |
action_result.data.\*.createdBy.user.id | string | | |
action_result.data.\*.createdDateTime | string | | |
action_result.data.\*.description | string | | Test List Description |
action_result.data.\*.driveType | string | | documentLibrary |
action_result.data.\*.lastModifiedBy.user.displayName | string | | Test User |
action_result.data.\*.lastModifiedBy.user.email | string | `email` | |
action_result.data.\*.lastModifiedBy.user.id | string | | |
action_result.data.\*.lastModifiedDateTime | string | | |
action_result.data.\*.webUrl | string | `url` | |
action_result.summary.drives_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list drive children'

List the items in a drive folder by drive ID or search for a specific file name if provided

Type: **investigate** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**drive_id** | optional | ID of drive to list. If no id is specified the default drive will be queried | string | `sharepoint drive id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.drive_id | string | `sharepoint drive id` | |
action_result.data.\*.@microsoft.graph.downloadUrl | string | `url` | https://graph.microsoft.com/v1.0/download |
action_result.data.\*.image.width | numeric | | 1752 |
action_result.data.\*.image.height | numeric | | 1244 |
action_result.data.\*.cTag | string | | |
action_result.data.\*.createdBy.user.displayName | string | | SharePoint App |
action_result.data.\*.createdBy.user.email | string | | |
action_result.data.\*.createdBy.user.id | string | | |
action_result.data.\*.createdDateTime | string | | |
action_result.data.\*.decorator.iconColor | string | | darkGreen |
action_result.data.\*.eTag | string | | |
action_result.data.\*.file.hashes.quickXorHash | string | | 8JpxaQB3wX1/FkQ5Gt3prUbUUFU= |
action_result.data.\*.file.mimeType | string | | application/vnd.ms-excel |
action_result.data.\*.fileSystemInfo.createdDateTime | string | | |
action_result.data.\*.fileSystemInfo.lastModifiedDateTime | string | | |
action_result.data.\*.folder.childCount | numeric | | 1 |
action_result.data.\*.id | string | `sharepoint drive item id` | |
action_result.data.\*.name | string | | |
action_result.data.\*.webUrl | string | `url` | |
action_result.data.\*.lastModifiedBy.application.displayName | string | | |
action_result.data.\*.lastModifiedBy.application.id | string | | |
action_result.data.\*.lastModifiedBy.user.displayName | string | | SharePoint App |
action_result.data.\*.lastModifiedBy.user.email | string | | |
action_result.data.\*.lastModifiedBy.user.id | string | | |
action_result.data.\*.lastModifiedDateTime | string | | |
action_result.data.\*.parentReference.driveId | string | `sharepoint drive id` | |
action_result.data.\*.parentReference.driveType | string | | |
action_result.data.\*.parentReference.id | string | `sharepoint drive item id` | |
action_result.data.\*.parentReference.name | string | | |
action_result.data.\*.parentReference.path | string | | |
action_result.data.\*.parentReference.siteId | string | | |
action_result.data.\*.shared.scope | string | | users |
action_result.data.\*.size | numeric | | 775 |
action_result.data.\*.specialFolder.name | string | | apps |
action_result.summary.drive_children_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list sites'

Fetch the details of the SharePoint sites

Type: **investigate** <br>
Read only: **False**

The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**limit** | optional | Maximum number of sites to return | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.limit | numeric | | |
action_result.data.\*.createdDateTime | string | | 2016-10-31T20:25:06Z |
action_result.data.\*.displayName | string | | Test Site Name |
action_result.data.\*.id | string | | tenant-name.sharepoint.com,595384ee-13aa-49d1-814b-00ed3e024cde,70abfe37-8aa1-4168-b83e-41b6e9721509 |
action_result.data.\*.isPersonalSite | boolean | | True False |
action_result.data.\*.lastModifiedDateTime | string | | 2022-02-16T12:12:25.9162131Z |
action_result.data.\*.name | string | | Test Site Name |
action_result.data.\*.siteCollection.hostname | string | `host name` | tenant-name.sharepoint.com |
action_result.data.\*.webUrl | string | `url` | https://test-tenant-name.sharepoint.com/search |
action_result.summary.sites_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list lists'

Fetch the available lists under a SharePoint site

Type: **investigate** <br>
Read only: **False**

The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**limit** | optional | Maximum number of sites to return | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.limit | numeric | | |
action_result.data.\*.@odata.etag | string | | |
action_result.data.\*.createdBy.user.displayName | string | | Test User |
action_result.data.\*.createdBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.createdBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.createdDateTime | string | | 2022-02-24T05:38:53Z |
action_result.data.\*.description | string | | Test List Description |
action_result.data.\*.displayName | string | `sharepoint list name` | ListName |
action_result.data.\*.eTag | string | | "4896b66a-659c-4fce-a148-0b26bd718f68,5" |
action_result.data.\*.id | string | `sharepoint list id` | 4896b66a-659c-4fce-a148-0b26bd718f68 |
action_result.data.\*.lastModifiedBy.user.displayName | string | | Test User |
action_result.data.\*.lastModifiedBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.lastModifiedBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.lastModifiedDateTime | string | | 2022-03-03T13:43:06Z |
action_result.data.\*.list.contentTypesEnabled | boolean | | True False |
action_result.data.\*.list.hidden | boolean | | True False |
action_result.data.\*.list.template | string | | genericList |
action_result.data.\*.name | string | | ListName |
action_result.data.\*.parentReference.siteId | string | | tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa |
action_result.data.\*.webUrl | string | `url` | https://test-tenant-name.sharepoint.com/sites/SiteName/Lists/ListName |
action_result.summary.lists_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get list'

Retrieves a list from a SharePoint Site

Type: **investigate** <br>
Read only: **False**

The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list** | required | Title or ID of the list to retrieve | string | `sharepoint list id` `sharepoint list name` |
**limit** | optional | Maximum number of list items to return | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.list | string | `sharepoint list id` `sharepoint list name` | |
action_result.parameter.limit | numeric | | |
action_result.data.\*.@odata.context | string | `url` | |
action_result.data.\*.@odata.etag | string | | |
action_result.data.\*.columns.\*.calculated.format | string | | dateTime |
action_result.data.\*.columns.\*.calculated.formula | string | | =[test] |
action_result.data.\*.columns.\*.calculated.outputType | string | | dateTime |
action_result.data.\*.columns.\*.choice.allowTextEntry | boolean | | True False |
action_result.data.\*.columns.\*.choice.displayAs | string | | dropDownMenu |
action_result.data.\*.columns.\*.columnGroup | string | | Custom Columns |
action_result.data.\*.columns.\*.dateTime.displayAs | string | | default |
action_result.data.\*.columns.\*.dateTime.format | string | | dateTime |
action_result.data.\*.columns.\*.description | string | | Test List Description |
action_result.data.\*.columns.\*.displayName | string | | ID |
action_result.data.\*.columns.\*.enforceUniqueValues | boolean | | True False |
action_result.data.\*.columns.\*.hidden | boolean | | True False |
action_result.data.\*.columns.\*.id | string | | 1d22ea11-1e32-424e-89ab-9fedbadb6ce1 |
action_result.data.\*.columns.\*.indexed | boolean | | True False |
action_result.data.\*.columns.\*.lookup.allowMultipleValues | boolean | | True False |
action_result.data.\*.columns.\*.lookup.allowUnlimitedLength | boolean | | True False |
action_result.data.\*.columns.\*.lookup.columnName | string | | ItemChildCount |
action_result.data.\*.columns.\*.lookup.listId | string | | |
action_result.data.\*.columns.\*.lookup.primaryLookupColumnId | string | | ID |
action_result.data.\*.columns.\*.name | string | | ID |
action_result.data.\*.columns.\*.personOrGroup.allowMultipleSelection | boolean | | True False |
action_result.data.\*.columns.\*.personOrGroup.chooseFromType | string | | peopleAndGroups |
action_result.data.\*.columns.\*.personOrGroup.displayAs | string | | nameWithPresence |
action_result.data.\*.columns.\*.readOnly | boolean | | True False |
action_result.data.\*.columns.\*.required | boolean | | True False |
action_result.data.\*.columns.\*.text.allowMultipleLines | boolean | | True False |
action_result.data.\*.columns.\*.text.appendChangesToExistingText | boolean | | True False |
action_result.data.\*.columns.\*.text.linesForEditing | numeric | | 0 |
action_result.data.\*.columns.\*.text.maxLength | numeric | | 255 |
action_result.data.\*.columns.\*.text.textType | string | | plain |
action_result.data.\*.columns@odata.context | string | `url` | |
action_result.data.\*.createdBy.user.displayName | string | | Test User |
action_result.data.\*.createdBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.createdBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.createdDateTime | string | | 2022-02-08T12:29:09Z |
action_result.data.\*.description | string | | Test List Description |
action_result.data.\*.displayName | string | `sharepoint list name` | Test List Name |
action_result.data.\*.eTag | string | | "4961c496-52c1-49bd-b1fa-e1b2e976256c,5" |
action_result.data.\*.id | string | `sharepoint list id` | 4961c496-52c1-49bd-b1fa-e1b2e976256c |
action_result.data.\*.items.\*.@odata.etag | string | | |
action_result.data.\*.items.\*.contentType.id | string | | 0x01008C9AE9AA9A043D48B717AB18E1E7180E00F8FCD4A1A57C3043B42193515148F5EC |
action_result.data.\*.items.\*.contentType.name | string | | Item |
action_result.data.\*.items.\*.createdBy.user.displayName | string | | Test User |
action_result.data.\*.items.\*.createdBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.items.\*.createdBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.items.\*.createdDateTime | string | | 2022-02-08T12:29:27Z |
action_result.data.\*.items.\*.eTag | string | | "fe7e1a7c-a66a-4944-b1f1-2b7c7499603c,1" |
action_result.data.\*.items.\*.fields.@odata.etag | string | | |
action_result.data.\*.items.\*.fields.AppAuthorLookupId | string | | 8 |
action_result.data.\*.items.\*.fields.AppEditorLookupId | string | | 8 |
action_result.data.\*.items.\*.fields.ApplicationDate | string | | 2022-02-03T08:00:00Z |
action_result.data.\*.items.\*.fields.Attachments | boolean | | True False |
action_result.data.\*.items.\*.fields.AuthorLookupId | string | | 9 |
action_result.data.\*.items.\*.fields.ContentType | string | | Item |
action_result.data.\*.items.\*.fields.Conversation | string | | I'd like access, please. |
action_result.data.\*.items.\*.fields.Created | string | | 2022-02-08T12:29:27Z |
action_result.data.\*.items.\*.fields.Edit | string | | |
action_result.data.\*.items.\*.fields.EditorLookupId | string | | 9 |
action_result.data.\*.items.\*.fields.FolderChildCount | string | | 0 |
action_result.data.\*.items.\*.fields.InterviewDate | string | | 2022-02-28T11:30:00Z |
action_result.data.\*.items.\*.fields.Interviewers.\*.Email | string | | test@testuser.com |
action_result.data.\*.items.\*.fields.Interviewers.\*.LookupId | numeric | | 18 |
action_result.data.\*.items.\*.fields.Interviewers.\*.LookupValue | string | | test |
action_result.data.\*.items.\*.fields.ItemChildCount | string | | 0 |
action_result.data.\*.items.\*.fields.LinkTitle | string | | List Item 1 |
action_result.data.\*.items.\*.fields.LinkTitleNoMenu | string | | List Item 1 |
action_result.data.\*.items.\*.fields.Modified | string | | 2022-02-08T12:29:27Z |
action_result.data.\*.items.\*.fields.Notes | string | | Test Notes |
action_result.data.\*.items.\*.fields.PermissionLevelRequested | numeric | | 8 |
action_result.data.\*.items.\*.fields.PhoneScreenDate | string | | 2022-02-15T14:00:00Z |
action_result.data.\*.items.\*.fields.PhoneScreenerLookupId | string | | 17 |
action_result.data.\*.items.\*.fields.Position | string | | Designer |
action_result.data.\*.items.\*.fields.Progress | string | | Active |
action_result.data.\*.items.\*.fields.PropagateAcl | boolean | | True False |
action_result.data.\*.items.\*.fields.RecruiterLookupId | string | | 19 |
action_result.data.\*.items.\*.fields.ReqByUserLookupId | string | | 10 |
action_result.data.\*.items.\*.fields.ReqForUserLookupId | string | | 10 |
action_result.data.\*.items.\*.fields.RequestDate | string | | 2022-08-04T12:14:03Z |
action_result.data.\*.items.\*.fields.RequestedByDisplayNameDisp | string | | Test User |
action_result.data.\*.items.\*.fields.RequestedForDisplayNameDisp | string | | Test User |
action_result.data.\*.items.\*.fields.StatusDisp | string | | 0 |
action_result.data.\*.items.\*.fields.Title | string | | List Item 1 |
action_result.data.\*.items.\*.fields.\_ComplianceFlags | string | | |
action_result.data.\*.items.\*.fields.\_ComplianceTag | string | | |
action_result.data.\*.items.\*.fields.\_ComplianceTagUserId | string | | |
action_result.data.\*.items.\*.fields.\_ComplianceTagWrittenTime | string | | |
action_result.data.\*.items.\*.fields._UIVersionString | string | | 1.0 |
action_result.data.\*.items.\*.fields.id | string | | 1 |
action_result.data.\*.items.\*.fields@odata.context | string | `url` | |
action_result.data.\*.items.\*.id | string | | 1 |
action_result.data.\*.items.\*.lastModifiedBy.application.displayName | string | | test |
action_result.data.\*.items.\*.lastModifiedBy.application.id | string | | 71b307af-1dcb-4e39-9640-5129afc83162 |
action_result.data.\*.items.\*.lastModifiedBy.user.displayName | string | | Test User |
action_result.data.\*.items.\*.lastModifiedBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.items.\*.lastModifiedBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.items.\*.lastModifiedDateTime | string | | 2022-02-08T12:29:27Z |
action_result.data.\*.items.\*.parentReference.id | string | `sharepoint item id` | |
action_result.data.\*.items.\*.parentReference.siteId | string | | |
action_result.data.\*.items.\*.webUrl | string | `url` | https://test-tenant-name.sharepoint.com/sites/TestSiteName/Lists/Test%20List%20Name/1_.000 |
action_result.data.\*.items@odata.context | string | `url` | |
action_result.data.\*.lastModifiedBy.user.displayName | string | | Test User |
action_result.data.\*.lastModifiedBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.lastModifiedBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.lastModifiedDateTime | string | | 2022-02-16T06:03:09Z |
action_result.data.\*.list.contentTypesEnabled | boolean | | True False |
action_result.data.\*.list.hidden | boolean | | True False |
action_result.data.\*.list.template | string | | genericList |
action_result.data.\*.name | string | | Test List Name |
action_result.data.\*.parentReference.siteId | string | | tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa |
action_result.data.\*.webUrl | string | `url` | https://test-tenant-name.sharepoint.com/sites/TestSiteName/Lists/Test%20List%20Name |
action_result.summary.item_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'add item'

Add an item to a list on a SharePoint Site

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list** | required | Title or ID of the list to add an item | string | `sharepoint list id` `sharepoint list name` |
**item** | required | JSON string of item | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.list | string | `sharepoint list id` `sharepoint list name` | |
action_result.parameter.item | string | | |
action_result.data.\*.@odata.context | string | `url` | |
action_result.data.\*.@odata.etag | string | | |
action_result.data.\*.contentType.id | string | | |
action_result.data.\*.contentType.name | string | | |
action_result.data.\*.createdBy.user.displayName | string | | |
action_result.data.\*.createdDateTime | string | | |
action_result.data.\*.eTag | string | | |
action_result.data.\*.fields.@odata.etag | string | | |
action_result.data.\*.fields.AppAuthorLookupId | string | | |
action_result.data.\*.fields.AppEditorLookupId | string | | |
action_result.data.\*.fields.Approved | boolean | | True False |
action_result.data.\*.fields.AssetType | string | | Laptop |
action_result.data.\*.fields.Attachments | boolean | | True False |
action_result.data.\*.fields.AuthorLookupId | string | | |
action_result.data.\*.fields.Color | string | | Color of the Asset |
action_result.data.\*.fields.Complete | boolean | | True False |
action_result.data.\*.fields.ConditionNotes | string | | Note for the Asset |
action_result.data.\*.fields.ContentType | string | | |
action_result.data.\*.fields.Created | string | | |
action_result.data.\*.fields.CurrentOwnerLookupId | string | | 17 |
action_result.data.\*.fields.DueDate | string | | 2022-08-04T12:38:45Z |
action_result.data.\*.fields.Duration | string | | |
action_result.data.\*.fields.Edit | string | | |
action_result.data.\*.fields.EditorLookupId | string | | |
action_result.data.\*.fields.FolderChildCount | string | | |
action_result.data.\*.fields.ItemChildCount | string | | |
action_result.data.\*.fields.LinkTitle | string | | |
action_result.data.\*.fields.LinkTitleNoMenu | string | | |
action_result.data.\*.fields.Manufacturer | string | | Test-Manufacturer-Asset |
action_result.data.\*.fields.Model | string | | Model of the Asset |
action_result.data.\*.fields.Modified | string | | |
action_result.data.\*.fields.OrderNumber | string | | 1 |
action_result.data.\*.fields.PreviousOwnerLookupId | string | | 18 |
action_result.data.\*.fields.PurchaseDate | string | | 2022-08-04T12:38:45Z |
action_result.data.\*.fields.PurchasePrice | numeric | | 1 |
action_result.data.\*.fields.SerialNumber | string | | Test-SerialNumber-Asset |
action_result.data.\*.fields.Status | string | | Status of the Asset |
action_result.data.\*.fields.Title | string | | Test Title |
action_result.data.\*.fields.TravelDuration | string | | 0 |
action_result.data.\*.fields.\_ComplianceFlags | string | | |
action_result.data.\*.fields.\_ComplianceTag | string | | |
action_result.data.\*.fields.\_ComplianceTagUserId | string | | |
action_result.data.\*.fields.\_ComplianceTagWrittenTime | string | | |
action_result.data.\*.fields.\_UIVersionString | string | | |
action_result.data.\*.fields.id | string | | |
action_result.data.\*.fields@odata.context | string | `url` | |
action_result.data.\*.id | string | `sharepoint item id` | |
action_result.data.\*.lastModifiedBy.application.displayName | string | | |
action_result.data.\*.lastModifiedBy.application.id | string | | |
action_result.data.\*.lastModifiedBy.user.displayName | string | | |
action_result.data.\*.lastModifiedDateTime | string | | |
action_result.data.\*.parentReference.id | string | | a86797a9-c9a9-47e7-891b-8413b2d758fc |
action_result.data.\*.parentReference.siteId | string | | |
action_result.data.\*.webUrl | string | `url` | |
action_result.summary.sites_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'update item'

Update an item in a list on a SharePoint Site

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list** | required | Title or ID of the list to which the item belongs | string | `sharepoint list id` `sharepoint list name` |
**item_id** | required | ID of the item to update | numeric | `sharepoint item id` |
**item** | required | JSON string of item | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.list | string | `sharepoint list id` `sharepoint list name` | |
action_result.parameter.item_id | numeric | `sharepoint item id` | |
action_result.parameter.item | string | | |
action_result.data.\*.@odata.context | string | `url` | |
action_result.data.\*.@odata.etag | string | | |
action_result.data.\*.contentType.id | string | | |
action_result.data.\*.contentType.name | string | | |
action_result.data.\*.createdBy.user.displayName | string | | |
action_result.data.\*.createdDateTime | string | | |
action_result.data.\*.eTag | string | | |
action_result.data.\*.fields.@odata.etag | string | | |
action_result.data.\*.fields.AppAuthorLookupId | string | | |
action_result.data.\*.fields.AppEditorLookupId | string | | |
action_result.data.\*.fields.AssetType | string | | Mobile |
action_result.data.\*.fields.Attachments | boolean | | True False |
action_result.data.\*.fields.AuthorLookupId | string | | |
action_result.data.\*.fields.Color | string | | Red |
action_result.data.\*.fields.ConditionNotes | string | | Note for the Updated Asset |
action_result.data.\*.fields.ContentType | string | | |
action_result.data.\*.fields.Created | string | | |
action_result.data.\*.fields.CurrentOwnerLookupId | string | | 18 |
action_result.data.\*.fields.DueDate | string | | 2023-08-05T07:00:00Z |
action_result.data.\*.fields.Edit | string | | |
action_result.data.\*.fields.EditorLookupId | string | | |
action_result.data.\*.fields.FolderChildCount | string | | |
action_result.data.\*.fields.ItemChildCount | string | | |
action_result.data.\*.fields.LinkTitle | string | | |
action_result.data.\*.fields.LinkTitleNoMenu | string | | |
action_result.data.\*.fields.Manufacturer | string | | Test-Updated-Manufacturer |
action_result.data.\*.fields.Model | string | | Model of the Updated Asset |
action_result.data.\*.fields.Modified | string | | |
action_result.data.\*.fields.OrderNumber | string | | 2 |
action_result.data.\*.fields.PreviousOwnerLookupId | string | | 17 |
action_result.data.\*.fields.PurchaseDate | string | | 2022-08-05T07:00:00Z |
action_result.data.\*.fields.PurchasePrice | numeric | | 1 |
action_result.data.\*.fields.SerialNumber | string | | Test-SerialNumber-Updated |
action_result.data.\*.fields.Status | string | | Status of the Asset |
action_result.data.\*.fields.Title | string | | Test-Updated-Title |
action_result.data.\*.fields.\_ComplianceFlags | string | | |
action_result.data.\*.fields.\_ComplianceTag | string | | |
action_result.data.\*.fields.\_ComplianceTagUserId | string | | |
action_result.data.\*.fields.\_ComplianceTagWrittenTime | string | | |
action_result.data.\*.fields.\_UIVersionString | string | | |
action_result.data.\*.fields.id | string | | |
action_result.data.\*.fields@odata.context | string | `url` | |
action_result.data.\*.id | string | `sharepoint item id` | |
action_result.data.\*.lastModifiedBy.application.displayName | string | | |
action_result.data.\*.lastModifiedBy.application.id | string | | |
action_result.data.\*.lastModifiedBy.user.displayName | string | | |
action_result.data.\*.lastModifiedDateTime | string | | |
action_result.data.\*.parentReference.id | string | | a86797a9-c9a9-47e7-891b-8413b2d758fc |
action_result.data.\*.parentReference.siteId | string | | |
action_result.data.\*.webUrl | string | `url` | |
action_result.summary.sites_count | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get file'

Retrieves a file from a SharePoint site

Type: **generic** <br>
Read only: **False**

The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file_name** | required | File name to retrieve | string | |
**file_path** | required | Folder path on site | string | |
**drive_id** | optional | The file is searched in this drive. If no drive is specified, the default drive will be used | string | `sharepoint drive id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.file_name | string | | |
action_result.parameter.file_path | string | | |
action_result.parameter.drive_id | string | `sharepoint drive id` | |
action_result.data.\*.@microsoft.graph.downloadUrl | string | `url` | https://test-tenant-name.sharepoint.com/sites/TestSiteName/\_layouts/15/download.aspx?UniqueId=c743b2e0-36ec-4c8a-9ce0-190c2fd4dd97&Translate=false&tempauth=eyJ0eXAiOiJKV1QiLCJhbGciOiJub0&ApiVersion=2.0 |
action_result.data.\*.@odata.context | string | `url` | |
action_result.data.\*.image.width | numeric | | 256 |
action_result.data.\*.image.height | numeric | | 266 |
action_result.data.\*.cTag | string | | "c:{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1" |
action_result.data.\*.id | string | `sharepoint drive item id` | 01SNFLYIXAWJB4P2ZWTJGJZYAZBQX5JXMX |
action_result.data.\*.createdBy.user.displayName | string | | Test User |
action_result.data.\*.createdBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.createdBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.createdDateTime | string | | 2022-02-10T15:25:21Z |
action_result.data.\*.eTag | string | | "{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1" |
action_result.data.\*.file.hashes.quickXorHash | string | | EIDYEgye8dEx3XhA7xc12GqSwxk= |
action_result.data.\*.file.mimeType | string | | text/plain |
action_result.data.\*.fileSystemInfo.createdDateTime | string | | 2022-02-10T15:25:21Z |
action_result.data.\*.fileSystemInfo.lastModifiedDateTime | string | | 2022-02-10T15:25:21Z |
action_result.data.\*.lastModifiedBy.user.displayName | string | | Test User |
action_result.data.\*.lastModifiedBy.user.email | string | `email` | test_user@tenant-name.ontest.com |
action_result.data.\*.lastModifiedBy.user.id | string | | eeb3645f-df19-47a1-8e8c-fcd234cb5f6f |
action_result.data.\*.lastModifiedDateTime | string | | 2022-02-10T15:25:21Z |
action_result.data.\*.name | string | | test_file_name.txt |
action_result.data.\*.parentReference.driveId | string | `sharepoint drive id` | b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi |
action_result.data.\*.parentReference.driveType | string | | documentLibrary |
action_result.data.\*.parentReference.id | string | `sharepoint drive item id` | 01SNFLYIRDSQLQVWP7EVDKSL3YYUNW6I4G |
action_result.data.\*.parentReference.name | string | | Playbook-Folder |
action_result.data.\*.parentReference.path | string | | /drive/root:/test_folder_name |
action_result.data.\*.parentReference.siteId | string | | dc6f43e9-54fa-4a39-8783-314e3bbbed41 |
action_result.data.\*.shared.scope | string | | users |
action_result.data.\*.size | numeric | | 1422 |
action_result.data.\*.webUrl | string | `url` | https://test-tenant-name.sharepoint.com/sites/TestSiteName/Shared%20Documents/test_folder_name/test_file_name.txt |
action_result.summary.vault_id | string | `sha1` `vault id` | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'remove file'

Removes a file from a SharePoint site

Type: **generic** <br>
Read only: **False**

The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file_name** | required | File name to remove | string | |
**file_path** | required | Folder path on site | string | |
**drive_id** | optional | The file is searched in this drive. If no drive is specified, the default drive will be used | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.file_name | string | | |
action_result.parameter.file_path | string | | |
action_result.parameter.drive_id | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'remove folder'

Removes a folder from a SharePoint site

Type: **generic** <br>
Read only: **False**

The 'folder path' parameter will be considered from the root of the document library specified in drive_id.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**folder_path** | required | Folder path on site | string | |
**drive_id** | optional | The file is searched in this drive. If no drive is specified, the default drive will be used | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.folder_path | string | | |
action_result.parameter.drive_id | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'make request'

Call Microsoft Graph with the asset's authentication and return status and raw body.

Supply a relative /v1.0/ or /beta/ path. Redirects are not followed. HTTP
error responses are returned as data; invalid input, authentication and
transport failures fail the action. Pagination is not followed.

Type: **generic** <br>
Read only: **False**

'make request' action for the app. Used to handle arbitrary HTTP requests with the app's asset

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**http_method** | required | The HTTP method to use for the request. | string | |
**endpoint** | required | Microsoft Graph path beginning with /v1.0/ or /beta/. Do not include the base URL. | string | |
**headers** | optional | The headers to send with the request (JSON object). An example is {'Content-Type': 'application/json'} | string | |
**query_parameters** | optional | Parameters to append to the URL (JSON object or query string). An example is ?key=value&key2=value2 | string | |
**body** | optional | The body to send with the request (JSON object). An example is {'key': 'value', 'key2': 'value2'} | string | |
**timeout** | optional | The timeout for the request in seconds. | numeric | |
**verify_ssl** | optional | Whether to verify the SSL certificate. Default is True. | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.http_method | string | | |
action_result.parameter.endpoint | string | | |
action_result.parameter.headers | string | | |
action_result.parameter.query_parameters | string | | |
action_result.parameter.body | string | | |
action_result.parameter.timeout | numeric | | |
action_result.parameter.verify_ssl | boolean | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"key": "value"} |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
