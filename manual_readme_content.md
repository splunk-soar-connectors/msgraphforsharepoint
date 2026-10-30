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
