# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Connector constants shared by the Microsoft Graph integration."""

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

AUTH_METHOD_DELEGATED = "Delegated"
AUTH_METHOD_CLIENT_CREDENTIALS = "Client Credentials"
DELEGATED_GRAPH_SCOPES = ["Sites.ReadWrite.All", "offline_access"]
OAUTH_START_ROUTE = "oauth/start"
OAUTH_CALLBACK_ROUTE = "oauth/callback"
AUTHORIZATION_URL_STATE_KEY = "msgraphforsharepoint_authorization_url"
AUTHORIZATION_ERROR_STATE_KEY = "msgraphforsharepoint_authorization_error"
REDIRECT_URI_STATE_KEY = "msgraphforsharepoint_redirect_uri"
OAUTH_SUCCESS_MESSAGE = "Authorization successful! You can close this window."
MAX_PAGINATION_PAGES = 1000
