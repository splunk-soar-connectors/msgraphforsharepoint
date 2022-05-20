# File: msgraphforsharepoint_consts.py
#
# Copyright (c) 2022 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

# JSONs used in params, result, summary etc.
MS_SHAREPOINT_CONFIG_TENANT = 'tenant_id'
MS_SHAREPOINT_CONFIG_CLIENT_ID = 'client_id'
MS_SHAREPOINT_CONFIG_CLIENT_SECRET = 'client_secret'  # pragma: allowlist secret
MS_SHAREPOINT_JSON_TOKEN = 'token'
MS_SHAREPOINT_JSON_ACCESS_TOKEN = 'access_token'
MS_SHAREPOINT_JSON_FILE_PATH = 'file_path'
MS_SHAREPOINT_JSON_FILE_NAME = 'file_name'
MS_SHAREPOINT_JSON_LIST = 'list'
MS_SHAREPOINT_JSON_LIMIT = 'limit'
MS_SHAREPOINT_JSON_VAULT_ID = 'vault_id'
MS_SHAREPOINT_JSON_SITES_COUNT = 'sites_count'
MS_SHAREPOINT_JSON_LISTS_COUNT = 'lists_count'
MS_SHAREPOINT_JSON_ITEM_COUNT = 'item_count'

# URLs and Endpoints
MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'
MS_SERVER_TOKEN_URL = 'https://login.microsoftonline.com/{0}/oauth2/v2.0/token'
MS_TEST_CONNECTIVITY_ENDPOINT = '/sites/root'
MS_LIST_SITES_ENDPOINT = '/sites'
MS_LIST_LISTS_ENDPOINT = '/sites/{0}/lists'
MS_GET_LIST_ENDPOINT = '/sites/{0}/lists/{1}'
MS_GET_FILE_METADATA_ENDPOINT = '/sites/{0}/drive/root:/{1}/{2}'
MS_GET_FILE_CONTENT_ENDPOINT = '{0}:/content'
MS_GROUPS_ENDPOINT = '/groups/{0}'
MS_AUTH_FAILURE_MSGS = ['token is invalid', 'token has expired', 'ExpiredAuthenticationToken', 'AuthenticationFailed']

# Splunk SOAR Endpoints
SOAR_SYS_INFO_URL = "{url}rest/system_info"
SOAR_ASSET_INFO_URL = "{url}rest/asset/{asset_id}"

DEFAULT_REQUEST_TIMEOUT = 30  # in seconds
STATE_FILE_PATH = '{0}/{1}_state.json'
MS_SHAREPOINT_PER_PAGE_COUNT = 1000

# Status/Progress Messages
MS_SHAREPOINT_ERR_CODE_MSG = 'Error code unavailable'
MS_SHAREPOINT_ERR_MSG = 'Unknown error occurred. Please check the asset configuration and|or action parameters'
MS_SHAREPOINT_ERR_MISSING_SITE_ID = "The asset configuration parameter 'Sharepoint Site ID' is required for {0} from specific site"
MS_SHAREPOINT_ERR_STATE_FILE_CORRUPT = 'Error occurred while loading the state file due to its unexpected format. ' \
                                       'Resetting the state file with the default format. Please try again.'
MS_SHAREPOINT_VALID_INTEGER_MSG = "Please provide a valid integer value in the {}"
MS_SHAREPOINT_NON_NEGATIVE_INTEGER_MSG = "Please provide a valid non-zero positive integer value in the {}"
MS_SHAREPOINT_POSITIVE_INTEGER_MSG = "Please provide non-zero positive integer in {}"
MS_SHAREPOINT_LIMIT_KEY = "'limit' action parameter"
