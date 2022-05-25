[comment]: # "Auto-generated SOAR connector documentation"
# MS Graph for SharePoint

Publisher: Splunk  
Connector Version: 1\.0\.1  
Product Vendor: Microsoft  
Product Name: SharePoint  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.1\.0  

This app connects to SharePoint using the MS Graph API to support investigate and generic actions

[comment]: # "File: README.md"
[comment]: # "Copyright (c) 2022 Splunk Inc."
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

    -   Provide the following Application permissions to the app.

          

        -   Sites.Read.All
        -   Files.Read.All
        -   Files.ReadWrite.All

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

For the **Sharepoint Group ID**, this should be the Group or Team subsite in your Sharepoint tenant. This is optional.

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
**tenant\_id** |  required  | string | Tenant ID
**site\_id** |  optional  | string | SharePoint Site ID
**group\_id** | optional | strong | Sharepoint Group ID
**admin\_consent** |  optional  | boolean | Admin Consent Already Provided
**client\_id** |  required  | string | Client/Application ID
**client\_secret** |  required  | password | Client Secret

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[list sites](#action-list-sites) - Fetch the details of the SharePoint sites  
[list lists](#action-list-lists) - Fetch the available lists under a SharePoint site  
[add item](#action-add-item) - Add an item to a list  
[update item](#action-update-item) - Update an item in a list  
[get list](#action-get-list) - Retrieves a list from a SharePoint Site  
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

The 'limit' parameter controls the number of records to return\. Leave the parameter value blank in order to fetch all the records\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**limit** |  optional  | Maximum number of sites to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.limit | numeric | 
action\_result\.data\.\*\.createdDateTime | string | 
action\_result\.data\.\*\.displayName | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.lastModifiedDateTime | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.siteCollection\.hostname | string |  `host name` 
action\_result\.data\.\*\.webUrl | string |  `url` 
action\_result\.summary\.sites\_count | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list lists'
Fetch the available lists under a SharePoint site

Type: **investigate**  
Read only: **True**

The 'limit' parameter controls the number of records to return\. Leave the parameter value blank in order to fetch all the records\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**limit** |  optional  | Maximum number of sites to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.limit | numeric | 
action\_result\.data\.\*\.\@odata\.etag | string | 
action\_result\.data\.\*\.createdBy\.user\.displayName | string | 
action\_result\.data\.\*\.createdBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.createdBy\.user\.id | string | 
action\_result\.data\.\*\.createdDateTime | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.displayName | string |  `sharepoint list name` 
action\_result\.data\.\*\.eTag | string | 
action\_result\.data\.\*\.id | string |  `sharepoint list id` 
action\_result\.data\.\*\.lastModifiedBy\.user\.displayName | string | 
action\_result\.data\.\*\.lastModifiedBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.lastModifiedBy\.user\.id | string | 
action\_result\.data\.\*\.lastModifiedDateTime | string | 
action\_result\.data\.\*\.list\.contentTypesEnabled | boolean | 
action\_result\.data\.\*\.list\.hidden | boolean | 
action\_result\.data\.\*\.list\.template | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.parentReference\.siteId | string | 
action\_result\.data\.\*\.webUrl | string |  `url` 
action\_result\.summary\.lists\_count | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get list'
Retrieves a list from a SharePoint Site

Type: **investigate**  
Read only: **True**

The 'limit' parameter controls the number of records to return\. Leave the parameter value blank in order to fetch all the records\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list** |  required  | Title or ID of the list to retrieve | string |  `sharepoint list id`  `sharepoint list name` 
**limit** |  optional  | Maximum number of list items to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.limit | numeric | 
action\_result\.parameter\.list | string |  `sharepoint list id`  `sharepoint list name` 
action\_result\.data\.\*\.\@odata\.context | string |  `url` 
action\_result\.data\.\*\.\@odata\.etag | string | 
action\_result\.data\.\*\.columns\.\*\.columnGroup | string | 
action\_result\.data\.\*\.columns\.\*\.dateTime\.displayAs | string | 
action\_result\.data\.\*\.columns\.\*\.dateTime\.format | string | 
action\_result\.data\.\*\.columns\.\*\.description | string | 
action\_result\.data\.\*\.columns\.\*\.displayName | string | 
action\_result\.data\.\*\.columns\.\*\.enforceUniqueValues | boolean | 
action\_result\.data\.\*\.columns\.\*\.hidden | boolean | 
action\_result\.data\.\*\.columns\.\*\.id | string | 
action\_result\.data\.\*\.columns\.\*\.indexed | boolean | 
action\_result\.data\.\*\.columns\.\*\.lookup\.allowMultipleValues | boolean | 
action\_result\.data\.\*\.columns\.\*\.lookup\.allowUnlimitedLength | boolean | 
action\_result\.data\.\*\.columns\.\*\.lookup\.columnName | string | 
action\_result\.data\.\*\.columns\.\*\.lookup\.listId | string | 
action\_result\.data\.\*\.columns\.\*\.lookup\.primaryLookupColumnId | string | 
action\_result\.data\.\*\.columns\.\*\.name | string | 
action\_result\.data\.\*\.columns\.\*\.personOrGroup\.allowMultipleSelection | boolean | 
action\_result\.data\.\*\.columns\.\*\.personOrGroup\.chooseFromType | string | 
action\_result\.data\.\*\.columns\.\*\.personOrGroup\.displayAs | string | 
action\_result\.data\.\*\.columns\.\*\.readOnly | boolean | 
action\_result\.data\.\*\.columns\.\*\.required | boolean | 
action\_result\.data\.\*\.columns\.\*\.text\.allowMultipleLines | boolean | 
action\_result\.data\.\*\.columns\.\*\.text\.appendChangesToExistingText | boolean | 
action\_result\.data\.\*\.columns\.\*\.text\.linesForEditing | numeric | 
action\_result\.data\.\*\.columns\.\*\.text\.maxLength | numeric | 
action\_result\.data\.\*\.columns\@odata\.context | string |  `url` 
action\_result\.data\.\*\.createdBy\.user\.displayName | string | 
action\_result\.data\.\*\.createdBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.createdBy\.user\.id | string | 
action\_result\.data\.\*\.createdDateTime | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.displayName | string |  `sharepoint list name` 
action\_result\.data\.\*\.eTag | string | 
action\_result\.data\.\*\.id | string |  `sharepoint list id` 
action\_result\.data\.\*\.items\.\*\.\@odata\.etag | string | 
action\_result\.data\.\*\.items\.\*\.contentType\.id | string | 
action\_result\.data\.\*\.items\.\*\.contentType\.name | string | 
action\_result\.data\.\*\.items\.\*\.createdBy\.user\.displayName | string | 
action\_result\.data\.\*\.items\.\*\.createdBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.items\.\*\.createdBy\.user\.id | string | 
action\_result\.data\.\*\.items\.\*\.createdDateTime | string | 
action\_result\.data\.\*\.items\.\*\.eTag | string | 
action\_result\.data\.\*\.items\.\*\.fields\.\@odata\.etag | string | 
action\_result\.data\.\*\.items\.\*\.fields\.Attachments | boolean | 
action\_result\.data\.\*\.items\.\*\.fields\.AuthorLookupId | string | 
action\_result\.data\.\*\.items\.\*\.fields\.ContentType | string | 
action\_result\.data\.\*\.items\.\*\.fields\.Created | string | 
action\_result\.data\.\*\.items\.\*\.fields\.Edit | string | 
action\_result\.data\.\*\.items\.\*\.fields\.EditorLookupId | string | 
action\_result\.data\.\*\.items\.\*\.fields\.FolderChildCount | string | 
action\_result\.data\.\*\.items\.\*\.fields\.ItemChildCount | string | 
action\_result\.data\.\*\.items\.\*\.fields\.LinkTitle | string | 
action\_result\.data\.\*\.items\.\*\.fields\.LinkTitleNoMenu | string | 
action\_result\.data\.\*\.items\.\*\.fields\.Modified | string | 
action\_result\.data\.\*\.items\.\*\.fields\.Title | string | 
action\_result\.data\.\*\.items\.\*\.fields\.\_ComplianceFlags | string | 
action\_result\.data\.\*\.items\.\*\.fields\.\_ComplianceTag | string | 
action\_result\.data\.\*\.items\.\*\.fields\.\_ComplianceTagUserId | string | 
action\_result\.data\.\*\.items\.\*\.fields\.\_ComplianceTagWrittenTime | string | 
action\_result\.data\.\*\.items\.\*\.fields\.\_UIVersionString | string | 
action\_result\.data\.\*\.items\.\*\.fields\.id | string | 
action\_result\.data\.\*\.items\.\*\.fields\@odata\.context | string |  `url` 
action\_result\.data\.\*\.items\.\*\.id | string | 
action\_result\.data\.\*\.items\.\*\.lastModifiedBy\.user\.displayName | string | 
action\_result\.data\.\*\.items\.\*\.lastModifiedBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.items\.\*\.lastModifiedBy\.user\.id | string | 
action\_result\.data\.\*\.items\.\*\.lastModifiedDateTime | string | 
action\_result\.data\.\*\.items\.\*\.parentReference\.siteId | string | 
action\_result\.data\.\*\.items\.\*\.webUrl | string |  `url` 
action\_result\.data\.\*\.items\@odata\.context | string |  `url` 
action\_result\.data\.\*\.lastModifiedBy\.user\.displayName | string | 
action\_result\.data\.\*\.lastModifiedBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.lastModifiedBy\.user\.id | string | 
action\_result\.data\.\*\.lastModifiedDateTime | string | 
action\_result\.data\.\*\.list\.contentTypesEnabled | boolean | 
action\_result\.data\.\*\.list\.hidden | boolean | 
action\_result\.data\.\*\.list\.template | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.parentReference\.siteId | string | 
action\_result\.data\.\*\.webUrl | string |  `url` 
action\_result\.summary\.item\_count | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'add item'
Add an item to a Sharepoint list

Type: **generic**
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list\_id** |  required  | ID of list to update | string | 
**item** |  required  | JSON post body of item to add | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
(unsure of good way to generate this)

## action: 'update item'
Update an item in a Sharepoint list

Type: **generic**
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**list\_id** |  required  | ID of list to update | string | 
**item\_id** |  required  | ID of item to update | numeric | 
**item** |  required  | JSON post body of item to add | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
(unsure of good way to generate this)

## action: 'get file'
Retrieves a file from a SharePoint site

Type: **generic**  
Read only: **True**

The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site\. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file\_name** |  required  | File name to retrieve | string | 
**file\_path** |  required  | Folder path on site | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.file\_name | string | 
action\_result\.parameter\.file\_path | string | 
action\_result\.data\.\*\.\@microsoft\.graph\.downloadUrl | string |  `url` 
action\_result\.data\.\*\.\@odata\.context | string |  `url` 
action\_result\.data\.\*\.cTag | string | 
action\_result\.data\.\*\.createdBy\.user\.displayName | string | 
action\_result\.data\.\*\.createdBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.createdBy\.user\.id | string | 
action\_result\.data\.\*\.createdDateTime | string | 
action\_result\.data\.\*\.eTag | string | 
action\_result\.data\.\*\.file\.hashes\.quickXorHash | string | 
action\_result\.data\.\*\.file\.mimeType | string | 
action\_result\.data\.\*\.fileSystemInfo\.createdDateTime | string | 
action\_result\.data\.\*\.fileSystemInfo\.lastModifiedDateTime | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.lastModifiedBy\.user\.displayName | string | 
action\_result\.data\.\*\.lastModifiedBy\.user\.email | string |  `email` 
action\_result\.data\.\*\.lastModifiedBy\.user\.id | string | 
action\_result\.data\.\*\.lastModifiedDateTime | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.parentReference\.driveId | string | 
action\_result\.data\.\*\.parentReference\.driveType | string | 
action\_result\.data\.\*\.parentReference\.id | string | 
action\_result\.data\.\*\.parentReference\.path | string | 
action\_result\.data\.\*\.size | numeric | 
action\_result\.data\.\*\.webUrl | string |  `url` 
action\_result\.summary\.vault\_id | string |  `sha1`  `vault id` 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'remove file'
Removes a file from a SharePoint site

Type: **generic**  
Read only: **False**

The 'file path' parameter will be considered from the <b>Shared Document</b> library in the configured Site\. If the file is available under the <b>Shared Document</b> library itself, then provide only the '/' value in the 'file path' parameter\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file\_name** |  required  | File name to remove | string | 
**file\_path** |  required  | Folder path on site | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.file\_name | string | 
action\_result\.parameter\.file\_path | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 