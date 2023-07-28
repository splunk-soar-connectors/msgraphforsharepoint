[comment]: # "Auto-generated SOAR connector documentation"
# MS Graph for SharePoint

Publisher: Splunk  
Connector Version: 1.2.1  
Product Vendor: Microsoft  
Product Name: SharePoint  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 5.3.5  

This app connects to SharePoint using the MS Graph API to support investigate and generic actions

[comment]: # "File: README.md"
[comment]: # "Copyright (c) 2022-2023 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
## Authentication

You will first need to create an application on the Azure AD Admin Portal. Follow the steps outlined
below to do this:

-   Navigate to <https://portal.azure.com> in a browser and log in with a Microsoft account

-   Select **Azure Active Directory** from the left side menu

-   From the left panel, select **App Registrations**

-   At the top of the middle section, select **New registration**

-   On the next page, give your application a name and click **Register**

-   Once the app is created, the below steps need to be taken on the next page:

      

    -   Under **Certificates & secrets** select **New client secret** . Note down this key somewhere
        secure, as it cannot be retrieved after closing the window.

    -   Under **Authentication** , select **Add a platform** . In the **Add a platform** window,
        select **Web** . The **Redirect URLs** should be filled right here. We will get **Redirect
        URLs** from the Phantom asset we create below in the section titled **Phantom Asset for
        SharePoint** . This step is required only if you are a non-admin user.

    -   Under **API Permissions** Click on **Add a permission** .

    -   Under the **Microsoft API** section, select **Microsoft Graph** .

    -   There are two ways to gives the Application and Delegated permissions to the app.

          

        1.  Permissive mode
            -   Sites.Read.All
            -   Files.Read.All
            -   Files.ReadWrite.All
            -   Sites.ReadWrite.All
        2.  Restrictive mode
            -   Sites.Selected (only Application permission)

            The user will have to configure permissions for each of the sites that they are working
            with. You can find more information
            [here](https://devblogs.microsoft.com/microsoft365dev/controlling-app-access-on-specific-sharepoint-site-collections/)
            . Also, while using this mode 'list sites' action will return the empty list.  
            **Note:** You need **Sites.FullControl.All** Application permission while using the site
            permission endpoint.

    -   After making these changes, click **Add permissions** at the bottom of the screen.

-   If you are an admin user, then click **Grant admin consent for Phantom** and provide admin
    consent. And configure asset configuration parameter **Admin Consent Already Provided** with
    value **True** .

-   If you are a non-admin user, then follow the steps listed below to grant admin consent:

      

    -   Configure an asset configuration parameter **Admin Consent Already Provided** with value
        **False** .
    -   You must have configured the **Redirect URLs** mentioned in the above steps.To configure
        **Redirect URLs** , checkout the section titled **Phantom Asset for SharePoint** below.
    -   Run the **Test Connectivity** .
    -   You will be asked to open a link in a new tab. Open the link in the same browser so that you
        are logged into Splunk Phantom for the redirect. If you wish to use a different browser, log
        in to the Splunk Phantom first, and then open the provided link.
    -   Proceed to log in to the Microsoft site with the admin user.
    -   You will be prompted to agree to the permissions requested by the App.
    -   If all goes well the browser should instruct you to close the tab.
    -   Now go back and check the message on the Test Connectivity dialog box, it should say **Test
        Connectivity Passed** .

## Phantom Asset for SharePoint

When creating an asset for the **MS Graph for SharePoint** app, place the **Application ID** and
**Client secret** of the app created during the previous step in the **Client/Application ID** and
**Client Secret** fields respectively. You can also find **Tenant ID** on the application overview
page. After filling in all the required values, click **SAVE** .  
  
After saving, a new field will appear in the **Asset Settings** tab. Take the URL found in the
**POST incoming for MS Graph for SharePoint to this location** field and place it in the **Redirect
URLs** field mentioned in a previous step. After doing so the URL should look something like:  

https://\<phantom_host>/rest/handler/msgraphforsharepoint_7963f3ef-b527-40e5-a704-392c56f0a88d/\<asset_name>

  
Additionally, updating the Base URL in the Company Settings is also required. Navigate to
**Administration \> Company Settings \> Info** to configure the **Base URL For Splunk SOAR** . Then,
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
documentation](https://support.microsoft.com/en-us/kb/905231) .  
As a workaround for lists, we can use the list_id instead of the list_name. Run the 'list lists'
action to get the list_id.

## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the Microsoft servers. Below are the
default ports used by Splunk SOAR.

|         Service Name | Transport Protocol | Port |
|----------------------|--------------------|------|
|         http         | tcp                | 80   |
|         https        | tcp                | 443  |


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a SharePoint asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**tenant_id** |  required  | string | Tenant ID
**site_id** |  optional  | string | SharePoint Site ID
**endpoint_test_connectivity** |  optional  | string | Endpoint for test connectivity
**admin_consent** |  optional  | boolean | Admin Consent Already Provided
**client_id** |  required  | string | Client/Application ID
**client_secret** |  required  | password | Client Secret

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[list sites](#action-list-sites) - Fetch the details of the SharePoint sites  
[list lists](#action-list-lists) - Fetch the available lists under a SharePoint site  
[get list](#action-get-list) - Retrieves a list from a SharePoint Site  
[add item](#action-add-item) - Add an item to a list on a SharePoint Site  
[update item](#action-update-item) - Update an item in a list on a SharePoint Site  
[get file](#action-get-file) - Retrieves a file from a SharePoint site  
[remove file](#action-remove-file) - Removes a file from a SharePoint site  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'list sites'
Fetch the details of the SharePoint sites

Type: **investigate**  
Read only: **True**

The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**limit** |  optional  | Maximum number of sites to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.limit | numeric |  |   500 
action_result.data.\*.createdDateTime | string |  |   2016-10-31T20:25:06Z 
action_result.data.\*.displayName | string |  |   Test Site Name 
action_result.data.\*.id | string |  |   tenant-name.sharepoint.com,595384ee-13aa-49d1-814b-00ed3e024cde,70abfe37-8aa1-4168-b83e-41b6e9721509 
action_result.data.\*.lastModifiedDateTime | string |  |   2022-02-16T12:12:25.9162131Z 
action_result.data.\*.name | string |  |   Test Site Name 
action_result.data.\*.siteCollection.hostname | string |  `host name`  |   tenant-name.sharepoint.com 
action_result.data.\*.webUrl | string |  `url`  |   https://test-tenant-name.sharepoint.com/search 
action_result.summary.sites_count | numeric |  |   23 
action_result.message | string |  |   Sites count: 23 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list lists'
Fetch the available lists under a SharePoint site

Type: **investigate**  
Read only: **True**

The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**limit** |  optional  | Maximum number of sites to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.limit | numeric |  |   500 
action_result.data.\*.@odata.etag | string |  |   "4896b66a-659c-4fce-a148-0b26bd718f68,5" 
action_result.data.\*.createdBy.user.displayName | string |  |   Test User 
action_result.data.\*.createdBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.createdBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.createdDateTime | string |  |   2022-02-24T05:38:53Z 
action_result.data.\*.description | string |  |   Test List Description 
action_result.data.\*.displayName | string |  `sharepoint list name`  |   ListName 
action_result.data.\*.eTag | string |  |   "4896b66a-659c-4fce-a148-0b26bd718f68,5" 
action_result.data.\*.id | string |  `sharepoint list id`  |   4896b66a-659c-4fce-a148-0b26bd718f68 
action_result.data.\*.lastModifiedBy.user.displayName | string |  |   Test User 
action_result.data.\*.lastModifiedBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.lastModifiedBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.lastModifiedDateTime | string |  |   2022-03-03T13:43:06Z 
action_result.data.\*.list.contentTypesEnabled | boolean |  |   True  False 
action_result.data.\*.list.hidden | boolean |  |   True  False 
action_result.data.\*.list.template | string |  |   genericList 
action_result.data.\*.name | string |  |   ListName 
action_result.data.\*.parentReference.siteId | string |  |   tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa 
action_result.data.\*.webUrl | string |  `url`  |   https://test-tenant-name.sharepoint.com/sites/SiteName/Lists/ListName 
action_result.summary.lists_count | numeric |  |   25 
action_result.message | string |  |   Lists count: 25 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get list'
Retrieves a list from a SharePoint Site

Type: **investigate**  
Read only: **True**

The 'limit' parameter controls the number of records to return. Leave the parameter value blank in order to fetch all the records.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list** |  required  | Title or ID of the list to retrieve | string |  `sharepoint list id`  `sharepoint list name` 
**limit** |  optional  | Maximum number of list items to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.limit | numeric |  |   500 
action_result.parameter.list | string |  `sharepoint list id`  `sharepoint list name`  |   4961c496-52c1-49bd-b1fa-e1b2e976256c  Test List Name 
action_result.data.\*.@odata.context | string |  `url`  |   https://graph.test.com/v1.0/$metadata#sites('tenant-name.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fb')/lists/$entity 
action_result.data.\*.@odata.etag | string |  |   "4961c496-52c1-49bd-b1fa-e1b2e976256c,5" 
action_result.data.\*.columns.\*.calculated.format | string |  |   dateTime 
action_result.data.\*.columns.\*.calculated.formula | string |  |   =[test] 
action_result.data.\*.columns.\*.calculated.outputType | string |  |   dateTime 
action_result.data.\*.columns.\*.choice.allowTextEntry | boolean |  |   False 
action_result.data.\*.columns.\*.choice.displayAs | string |  |   dropDownMenu 
action_result.data.\*.columns.\*.columnGroup | string |  |   Custom Columns 
action_result.data.\*.columns.\*.dateTime.displayAs | string |  |   default 
action_result.data.\*.columns.\*.dateTime.format | string |  |   dateTime 
action_result.data.\*.columns.\*.description | string |  |   Test List Description 
action_result.data.\*.columns.\*.displayName | string |  |   ID 
action_result.data.\*.columns.\*.enforceUniqueValues | boolean |  |   True  False 
action_result.data.\*.columns.\*.hidden | boolean |  |   True  False 
action_result.data.\*.columns.\*.id | string |  |   1d22ea11-1e32-424e-89ab-9fedbadb6ce1 
action_result.data.\*.columns.\*.indexed | boolean |  |   True  False 
action_result.data.\*.columns.\*.lookup.allowMultipleValues | boolean |  |   True  False 
action_result.data.\*.columns.\*.lookup.allowUnlimitedLength | boolean |  |   True  False 
action_result.data.\*.columns.\*.lookup.columnName | string |  |   ItemChildCount 
action_result.data.\*.columns.\*.lookup.listId | string |  |  
action_result.data.\*.columns.\*.lookup.primaryLookupColumnId | string |  |   ID 
action_result.data.\*.columns.\*.name | string |  |   ID 
action_result.data.\*.columns.\*.personOrGroup.allowMultipleSelection | boolean |  |   True  False 
action_result.data.\*.columns.\*.personOrGroup.chooseFromType | string |  |   peopleAndGroups 
action_result.data.\*.columns.\*.personOrGroup.displayAs | string |  |   nameWithPresence 
action_result.data.\*.columns.\*.readOnly | boolean |  |   True  False 
action_result.data.\*.columns.\*.required | boolean |  |   True  False 
action_result.data.\*.columns.\*.text.allowMultipleLines | boolean |  |   True  False 
action_result.data.\*.columns.\*.text.appendChangesToExistingText | boolean |  |   True  False 
action_result.data.\*.columns.\*.text.linesForEditing | numeric |  |   0 
action_result.data.\*.columns.\*.text.maxLength | numeric |  |   255 
action_result.data.\*.columns.\*.text.textType | string |  |   plain 
action_result.data.\*.columns@odata.context | string |  `url`  |   https://graph.test.com/v1.0/$metadata#sites('tenant-name.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fb')/lists('4961c496-52c1-49bd-b1fa-e1b2e976256c')/columns 
action_result.data.\*.createdBy.user.displayName | string |  |   Test User 
action_result.data.\*.createdBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.createdBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.createdDateTime | string |  |   2022-02-08T12:29:09Z 
action_result.data.\*.description | string |  |   Test List Description 
action_result.data.\*.displayName | string |  `sharepoint list name`  |   Test List Name 
action_result.data.\*.eTag | string |  |   "4961c496-52c1-49bd-b1fa-e1b2e976256c,5" 
action_result.data.\*.id | string |  `sharepoint list id`  |   4961c496-52c1-49bd-b1fa-e1b2e976256c 
action_result.data.\*.items.\*.@odata.etag | string |  |   "fe7e1a7c-a66a-4944-b1f1-2b7c7499603c,1" 
action_result.data.\*.items.\*.contentType.id | string |  |   0x01008C9AE9AA9A043D48B717AB18E1E7180E00F8FCD4A1A57C3043B42193515148F5EC 
action_result.data.\*.items.\*.contentType.name | string |  |   Item 
action_result.data.\*.items.\*.createdBy.user.displayName | string |  |   Test User 
action_result.data.\*.items.\*.createdBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.items.\*.createdBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.items.\*.createdDateTime | string |  |   2022-02-08T12:29:27Z 
action_result.data.\*.items.\*.eTag | string |  |   "fe7e1a7c-a66a-4944-b1f1-2b7c7499603c,1" 
action_result.data.\*.items.\*.fields.@odata.etag | string |  |   "fe7e1a7c-a66a-4944-b1f1-2b7c7499603c,1" 
action_result.data.\*.items.\*.fields.AppAuthorLookupId | string |  |   8 
action_result.data.\*.items.\*.fields.AppEditorLookupId | string |  |   8 
action_result.data.\*.items.\*.fields.ApplicationDate | string |  |   2022-02-03T08:00:00Z 
action_result.data.\*.items.\*.fields.Attachments | boolean |  |   True  False 
action_result.data.\*.items.\*.fields.AuthorLookupId | string |  |   9 
action_result.data.\*.items.\*.fields.ContentType | string |  |   Item 
action_result.data.\*.items.\*.fields.Conversation | string |  |   I'd like access, please. 
action_result.data.\*.items.\*.fields.Created | string |  |   2022-02-08T12:29:27Z 
action_result.data.\*.items.\*.fields.Edit | string |  |  
action_result.data.\*.items.\*.fields.EditorLookupId | string |  |   9 
action_result.data.\*.items.\*.fields.FolderChildCount | string |  |   0 
action_result.data.\*.items.\*.fields.InterviewDate | string |  |   2022-02-28T11:30:00Z 
action_result.data.\*.items.\*.fields.Interviewers.\*.Email | string |  |   test@testuser.com 
action_result.data.\*.items.\*.fields.Interviewers.\*.LookupId | numeric |  |   18 
action_result.data.\*.items.\*.fields.Interviewers.\*.LookupValue | string |  |   test 
action_result.data.\*.items.\*.fields.ItemChildCount | string |  |   0 
action_result.data.\*.items.\*.fields.LinkTitle | string |  |   List Item 1 
action_result.data.\*.items.\*.fields.LinkTitleNoMenu | string |  |   List Item 1 
action_result.data.\*.items.\*.fields.Modified | string |  |   2022-02-08T12:29:27Z 
action_result.data.\*.items.\*.fields.Notes | string |  |   Test Notes 
action_result.data.\*.items.\*.fields.PermissionLevelRequested | numeric |  |   8 
action_result.data.\*.items.\*.fields.PhoneScreenDate | string |  |   2022-02-15T14:00:00Z 
action_result.data.\*.items.\*.fields.PhoneScreenerLookupId | string |  |   17 
action_result.data.\*.items.\*.fields.Position | string |  |   Designer 
action_result.data.\*.items.\*.fields.Progress | string |  |   Active 
action_result.data.\*.items.\*.fields.PropagateAcl | boolean |  |   False 
action_result.data.\*.items.\*.fields.RecruiterLookupId | string |  |   19 
action_result.data.\*.items.\*.fields.ReqByUserLookupId | string |  |   10 
action_result.data.\*.items.\*.fields.ReqForUserLookupId | string |  |   10 
action_result.data.\*.items.\*.fields.RequestDate | string |  |   2022-08-04T12:14:03Z 
action_result.data.\*.items.\*.fields.RequestedByDisplayNameDisp | string |  |   Test User 
action_result.data.\*.items.\*.fields.RequestedForDisplayNameDisp | string |  |   Test User 
action_result.data.\*.items.\*.fields.StatusDisp | string |  |   0 
action_result.data.\*.items.\*.fields.Title | string |  |   List Item 1 
action_result.data.\*.items.\*.fields._ComplianceFlags | string |  |  
action_result.data.\*.items.\*.fields._ComplianceTag | string |  |  
action_result.data.\*.items.\*.fields._ComplianceTagUserId | string |  |  
action_result.data.\*.items.\*.fields._ComplianceTagWrittenTime | string |  |  
action_result.data.\*.items.\*.fields._UIVersionString | string |  |   1.0 
action_result.data.\*.items.\*.fields.id | string |  |   1 
action_result.data.\*.items.\*.fields@odata.context | string |  `url`  |   https://graph.test.com/v1.0/$metadata#sites('tenant-name.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fb')/lists('4961c496-52c1-49bd-b1fa-e1b2e976256c')/items('1')/fields/$entity 
action_result.data.\*.items.\*.id | string |  |   1 
action_result.data.\*.items.\*.lastModifiedBy.application.displayName | string |  |   test 
action_result.data.\*.items.\*.lastModifiedBy.application.id | string |  |   71b307af-1dcb-4e39-9640-5129afc83162 
action_result.data.\*.items.\*.lastModifiedBy.user.displayName | string |  |   Test User 
action_result.data.\*.items.\*.lastModifiedBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.items.\*.lastModifiedBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.items.\*.lastModifiedDateTime | string |  |   2022-02-08T12:29:27Z 
action_result.data.\*.items.\*.parentReference.id | string |  |   49f4a5c5-4c09-4ad0-b0fe-d8d27dfb9cb2 
action_result.data.\*.items.\*.parentReference.siteId | string |  |   tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa 
action_result.data.\*.items.\*.webUrl | string |  `url`  |   https://test-tenant-name.sharepoint.com/sites/TestSiteName/Lists/Test%20List%20Name/1_.000 
action_result.data.\*.items@odata.context | string |  `url`  |   https://graph.test.com/v1.0/$metadata#sites('tenant-name.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fb')/lists('4961c496-52c1-49bd-b1fa-e1b2e976256c')/items 
action_result.data.\*.lastModifiedBy.user.displayName | string |  |   Test User 
action_result.data.\*.lastModifiedBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.lastModifiedBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.lastModifiedDateTime | string |  |   2022-02-16T06:03:09Z 
action_result.data.\*.list.contentTypesEnabled | boolean |  |   True  False 
action_result.data.\*.list.hidden | boolean |  |   True  False 
action_result.data.\*.list.template | string |  |   genericList 
action_result.data.\*.name | string |  |   Test List Name 
action_result.data.\*.parentReference.siteId | string |  |   tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa 
action_result.data.\*.webUrl | string |  `url`  |   https://test-tenant-name.sharepoint.com/sites/TestSiteName/Lists/Test%20List%20Name 
action_result.summary.item_count | numeric |  |   2 
action_result.message | string |  |   Item count: 2 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add item'
Add an item to a list on a SharePoint Site

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list** |  required  | Title or ID of the list to add an item | string |  `sharepoint list id`  `sharepoint list name` 
**item** |  required  | JSON string of item | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.item | string |  |   {"fields": {"Title": "Test"}} 
action_result.parameter.list | string |  `sharepoint list id`  `sharepoint list name`  |   d52a6552-2884-4f77-9707-1badc7300ae3 
action_result.data.\*.@odata.context | string |  `url`  |  
action_result.data.\*.@odata.etag | string |  |  
action_result.data.\*.contentType.id | string |  |  
action_result.data.\*.contentType.name | string |  |  
action_result.data.\*.createdBy.user.displayName | string |  |  
action_result.data.\*.createdDateTime | string |  |  
action_result.data.\*.eTag | string |  |  
action_result.data.\*.fields.@odata.etag | string |  |  
action_result.data.\*.fields.AppAuthorLookupId | string |  |  
action_result.data.\*.fields.AppEditorLookupId | string |  |  
action_result.data.\*.fields.AssetType | string |  |   Laptop 
action_result.data.\*.fields.Attachments | numeric |  |  
action_result.data.\*.fields.AuthorLookupId | string |  |  
action_result.data.\*.fields.Color | string |  |   Color of the Asset 
action_result.data.\*.fields.Complete | boolean |  |   False 
action_result.data.\*.fields.ConditionNotes | string |  |   Note for the Asset 
action_result.data.\*.fields.ContentType | string |  |  
action_result.data.\*.fields.Created | string |  |  
action_result.data.\*.fields.CurrentOwnerLookupId | string |  |   17 
action_result.data.\*.fields.DueDate | string |  |   2022-08-04T12:38:45Z 
action_result.data.\*.fields.Duration | string |  |  
action_result.data.\*.fields.Edit | string |  |  
action_result.data.\*.fields.EditorLookupId | string |  |  
action_result.data.\*.fields.FolderChildCount | string |  |  
action_result.data.\*.fields.ItemChildCount | string |  |  
action_result.data.\*.fields.LinkTitle | string |  |  
action_result.data.\*.fields.LinkTitleNoMenu | string |  |  
action_result.data.\*.fields.Manufacturer | string |  |   Test-Manufacturer-Asset 
action_result.data.\*.fields.Model | string |  |   Model of the Asset 
action_result.data.\*.fields.Modified | string |  |  
action_result.data.\*.fields.OrderNumber | string |  |   1 
action_result.data.\*.fields.PreviousOwnerLookupId | string |  |   18 
action_result.data.\*.fields.PurchaseDate | string |  |   2022-08-04T12:38:45Z 
action_result.data.\*.fields.PurchasePrice | numeric |  |   1 
action_result.data.\*.fields.SerialNumber | string |  |   Test-SerialNumber-Asset 
action_result.data.\*.fields.Status | string |  |   Status of the Asset 
action_result.data.\*.fields.Title | string |  |   Test Title 
action_result.data.\*.fields._ComplianceFlags | string |  |  
action_result.data.\*.fields._ComplianceTag | string |  |  
action_result.data.\*.fields._ComplianceTagUserId | string |  |  
action_result.data.\*.fields._ComplianceTagWrittenTime | string |  |  
action_result.data.\*.fields._UIVersionString | string |  |  
action_result.data.\*.fields.id | string |  |  
action_result.data.\*.fields@odata.context | string |  `url`  |  
action_result.data.\*.id | string |  `sharepoint item id`  |  
action_result.data.\*.lastModifiedBy.application.displayName | string |  |  
action_result.data.\*.lastModifiedBy.application.id | string |  |  
action_result.data.\*.lastModifiedBy.user.displayName | string |  |  
action_result.data.\*.lastModifiedDateTime | string |  |  
action_result.data.\*.parentReference.id | string |  |   a86797a9-c9a9-47e7-891b-8413b2d758fc 
action_result.data.\*.parentReference.siteId | string |  |  
action_result.data.\*.webUrl | string |  `url`  |  
action_result.summary.sites_count | numeric |  |  
action_result.message | string |  |   Sites count: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'update item'
Update an item in a list on a SharePoint Site

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list** |  required  | Title or ID of the list to which the item belongs | string |  `sharepoint list id`  `sharepoint list name` 
**item_id** |  required  | ID of the item to update | numeric |  `sharepoint item id` 
**item** |  required  | JSON string of item | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.item | string |  |   {"fields": {"Title": "Test"}} 
action_result.parameter.item_id | numeric |  `sharepoint item id`  |   37 
action_result.parameter.list | string |  `sharepoint list id`  `sharepoint list name`  |   075d79f1-a11f-44ed-a794-331a1d9138f0 
action_result.data.\*.@odata.context | string |  `url`  |  
action_result.data.\*.@odata.etag | string |  |  
action_result.data.\*.contentType.id | string |  |  
action_result.data.\*.contentType.name | string |  |  
action_result.data.\*.createdBy.user.displayName | string |  |  
action_result.data.\*.createdDateTime | string |  |  
action_result.data.\*.eTag | string |  |  
action_result.data.\*.fields.@odata.etag | string |  |  
action_result.data.\*.fields.AppAuthorLookupId | string |  |  
action_result.data.\*.fields.AppEditorLookupId | string |  |  
action_result.data.\*.fields.AssetType | string |  |   Mobile 
action_result.data.\*.fields.Attachments | numeric |  |  
action_result.data.\*.fields.AuthorLookupId | string |  |  
action_result.data.\*.fields.Color | string |  |   Red 
action_result.data.\*.fields.ConditionNotes | string |  |   Note for the Updated Asset 
action_result.data.\*.fields.ContentType | string |  |  
action_result.data.\*.fields.Created | string |  |  
action_result.data.\*.fields.CurrentOwnerLookupId | string |  |   18 
action_result.data.\*.fields.DueDate | string |  |   2023-08-05T07:00:00Z 
action_result.data.\*.fields.Edit | string |  |  
action_result.data.\*.fields.EditorLookupId | string |  |  
action_result.data.\*.fields.FolderChildCount | string |  |  
action_result.data.\*.fields.ItemChildCount | string |  |  
action_result.data.\*.fields.LinkTitle | string |  |  
action_result.data.\*.fields.LinkTitleNoMenu | string |  |  
action_result.data.\*.fields.Manufacturer | string |  |   Test-Updated-Manufacturer 
action_result.data.\*.fields.Model | string |  |   Model of the Updated Asset 
action_result.data.\*.fields.Modified | string |  |  
action_result.data.\*.fields.OrderNumber | string |  |   2 
action_result.data.\*.fields.PreviousOwnerLookupId | string |  |   17 
action_result.data.\*.fields.PurchaseDate | string |  |   2022-08-05T07:00:00Z 
action_result.data.\*.fields.PurchasePrice | numeric |  |   1 
action_result.data.\*.fields.SerialNumber | string |  |   Test-SerialNumber-Updated 
action_result.data.\*.fields.Status | string |  |   Status of the Asset 
action_result.data.\*.fields.Title | string |  |   Test-Updated-Title 
action_result.data.\*.fields._ComplianceFlags | string |  |  
action_result.data.\*.fields._ComplianceTag | string |  |  
action_result.data.\*.fields._ComplianceTagUserId | string |  |  
action_result.data.\*.fields._ComplianceTagWrittenTime | string |  |  
action_result.data.\*.fields._UIVersionString | string |  |  
action_result.data.\*.fields.id | string |  |  
action_result.data.\*.fields@odata.context | string |  `url`  |  
action_result.data.\*.id | string |  `sharepoint item id`  |  
action_result.data.\*.lastModifiedBy.application.displayName | string |  |  
action_result.data.\*.lastModifiedBy.application.id | string |  |  
action_result.data.\*.lastModifiedBy.user.displayName | string |  |  
action_result.data.\*.lastModifiedDateTime | string |  |  
action_result.data.\*.parentReference.id | string |  |   a86797a9-c9a9-47e7-891b-8413b2d758fc 
action_result.data.\*.parentReference.siteId | string |  |  
action_result.data.\*.webUrl | string |  `url`  |  
action_result.summary.sites_count | numeric |  |  
action_result.message | string |  |   Sites count: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get file'
Retrieves a file from a SharePoint site

Type: **generic**  
Read only: **False**

The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file_name** |  required  | File name to retrieve | string | 
**file_path** |  required  | Folder path on site | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.file_name | string |  |   test_file_name.txt 
action_result.parameter.file_path | string |  |   /test_folder_name/ 
action_result.data.\*.@microsoft.graph.downloadUrl | string |  `url`  |   https://test-tenant-name.sharepoint.com/sites/TestSiteName/_layouts/15/download.aspx?UniqueId=c743b2e0-36ec-4c8a-9ce0-190c2fd4dd97&Translate=false&tempauth=eyJ0eXAiOiJKV1QiLCJhbGciOiJub0&ApiVersion=2.0 
action_result.data.\*.@odata.context | string |  `url`  |   https://graph.test.com/v1.0/$metadata#sites('tenant-name.sharepoint.com%2Cdc6f43e9-54fa-4a39-8783-314e3bbbed41%2Cc42b48c4-59b9-48f1-b96e-e8145b5539fb')/drive/root/$entity 
action_result.data.\*.cTag | string |  |   "c:{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1" 
action_result.data.\*.createdBy.user.displayName | string |  |   Test User 
action_result.data.\*.createdBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.createdBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.createdDateTime | string |  |   2022-02-10T15:25:21Z 
action_result.data.\*.eTag | string |  |   "{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1" 
action_result.data.\*.file.hashes.quickXorHash | string |  |   EIDYEgye8dEx3XhA7xc12GqSwxk= 
action_result.data.\*.file.mimeType | string |  |   text/plain 
action_result.data.\*.fileSystemInfo.createdDateTime | string |  |   2022-02-10T15:25:21Z 
action_result.data.\*.fileSystemInfo.lastModifiedDateTime | string |  |   2022-02-10T15:25:21Z 
action_result.data.\*.id | string |  |   01SNFLYIXAWJB4P2ZWTJGJZYAZBQX5JXMX 
action_result.data.\*.lastModifiedBy.user.displayName | string |  |   Test User 
action_result.data.\*.lastModifiedBy.user.email | string |  `email`  |   test_user@tenant-name.ontest.com 
action_result.data.\*.lastModifiedBy.user.id | string |  |   eeb3645f-df19-47a1-8e8c-fcd234cb5f6f 
action_result.data.\*.lastModifiedDateTime | string |  |   2022-02-10T15:25:21Z 
action_result.data.\*.name | string |  |   test_file_name.txt 
action_result.data.\*.parentReference.driveId | string |  |   b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi 
action_result.data.\*.parentReference.driveType | string |  |   documentLibrary 
action_result.data.\*.parentReference.id | string |  |   01SNFLYIRDSQLQVWP7EVDKSL3YYUNW6I4G 
action_result.data.\*.parentReference.path | string |  |   /drive/root:/test_folder_name 
action_result.data.\*.size | numeric |  |   1422 
action_result.data.\*.webUrl | string |  `url`  |   https://test-tenant-name.sharepoint.com/sites/TestSiteName/Shared%20Documents/test_folder_name/test_file_name.txt 
action_result.summary.vault_id | string |  `sha1`  `vault id`  |   8b11ac28c0e276a4f9fa8a2fd2a17b499a415786 
action_result.message | string |  |   Vault id: 8b11ac28c0e276a4f9fa8a2fd2a17b499a415786 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'remove file'
Removes a file from a SharePoint site

Type: **generic**  
Read only: **False**

The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file_name** |  required  | File name to remove | string | 
**file_path** |  required  | Folder path on site | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.file_name | string |  |   test_file_name.txt 
action_result.parameter.file_path | string |  |   /test_folder_name/ 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully deleted file 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 