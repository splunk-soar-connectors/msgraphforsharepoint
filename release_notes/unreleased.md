**Unreleased**

* Breaking (SOAR compatibility): Requires SOAR 8.7.0 or later and Python 3.13.
* Breaking (non-admin OAuth consent): Existing Microsoft app registrations must replace the legacy REST handler redirect URI with the SDK webhook callback URL shown by Test Connectivity.
* Add an authenticated generic Microsoft Graph request action for `/v1.0/` and `/beta/` endpoints.
* Change `get_list` to use the SDK built-in table renderer; nested response data remains available with a simplified table presentation.
