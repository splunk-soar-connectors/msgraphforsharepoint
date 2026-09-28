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

import ast
import unittest
from pathlib import Path


CONNECTOR = Path(__file__).resolve().parents[1] / "msgraphforsharepoint_connector.py"


class _Phantom:
    APP_ERROR = -1
    APP_SUCCESS = 0

    @staticmethod
    def is_fail(status):
        return status != _Phantom.APP_SUCCESS


class _Clock:
    now = 1000

    @classmethod
    def time(cls):
        return cls.now


class _ActionResult:
    def __init__(self):
        self.status = _Phantom.APP_SUCCESS

    def set_status(self, status, _message=None):
        self.status = status
        return status

    def get_status(self):
        return self.status


def _load_methods():
    tree = ast.parse(CONNECTOR.read_text())
    connector_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MsGraphForSharepointConnector")
    methods = [
        node for node in connector_class.body if isinstance(node, ast.FunctionDef) and node.name in {"_get_token", "_make_rest_call_helper"}
    ]
    namespace = {
        "phantom": _Phantom,
        "time": _Clock,
        "MS_SERVER_TOKEN_URL": "https://login.microsoftonline.com/{0}/oauth2/v2.0/token",
        "MS_SHAREPOINT_JSON_TOKEN": "token",
        "MS_SHAREPOINT_JSON_ACCESS_TOKEN": "access_token",
        "MS_SHAREPOINT_JSON_EXPIRES_IN": "expires_in",
        "MS_SHAREPOINT_JSON_EXPIRES_AT": "expires_at",
        "MS_SHAREPOINT_TOKEN_EXPIRY_BUFFER": 60,
    }
    exec(compile(ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[])), str(CONNECTOR), "exec"), namespace)
    return namespace["_get_token"], namespace["_make_rest_call_helper"]


_GET_TOKEN, _MAKE_REST_CALL_HELPER = _load_methods()


class _Connector:
    _get_token = _GET_TOKEN
    _make_rest_call_helper = _MAKE_REST_CALL_HELPER
    _tenant = "tenant"
    _client_id = "client"
    _client_secret = ""
    _base_url = "https://graph.microsoft.com/v1.0"

    def __init__(self, token=None, token_error=False):
        self._state = {"token": token or {}}
        self._access_token = self._state["token"].get("access_token")
        self.token_error = token_error
        self.calls = []

    def save_progress(self, _message):
        pass

    def _make_rest_call(
        self, endpoint, action_result, verify=True, headers=None, params=None, data=None, json=None, method="get", download=False
    ):
        self.calls.append((endpoint, dict(headers or {})))
        if method == "post":
            if self.token_error:
                return action_result.set_status(_Phantom.APP_ERROR, "Token request failed"), None
            return _Phantom.APP_SUCCESS, {"access_token": "fresh", "expires_in": 3600}
        if headers["Authorization"] != "Bearer fresh":
            return action_result.set_status(
                _Phantom.APP_ERROR, "Error from server. Status Code: 401 Data from server: InvalidAuthenticationToken. Invalid token lifetime."
            ), None
        return _Phantom.APP_SUCCESS, {"value": "ok"}


class TokenExpiryTests(unittest.TestCase):
    def setUp(self):
        _Clock.now = 1000

    def test_expired_token_is_replaced_before_graph_request(self):
        connector = _Connector({"access_token": "stale", "expires_at": 999})

        status, response = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, {"value": "ok"})
        self.assertEqual(connector._state["token"]["expires_at"], 4540)
        self.assertEqual(len(connector.calls), 2)
        self.assertEqual(connector.calls[1][1]["Authorization"], "Bearer fresh")

    def test_legacy_token_without_expiry_is_replaced(self):
        connector = _Connector({"access_token": "stale", "expires_in": 3600})

        status, _ = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(connector.calls[1][1]["Authorization"], "Bearer fresh")

    def test_valid_token_is_reused_until_expiry(self):
        connector = _Connector({"access_token": "fresh", "expires_at": 4540})

        status, _ = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(len(connector.calls), 1)
        _Clock.now = 4540
        status, _ = connector._make_rest_call_helper("/sites/root", _ActionResult())
        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(len(connector.calls), 3)

    def test_token_request_failure_stops_before_graph_request(self):
        connector = _Connector({"access_token": "stale", "expires_at": 999}, token_error=True)

        status, response = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_ERROR)
        self.assertIsNone(response)
        self.assertEqual(len(connector.calls), 1)


if __name__ == "__main__":
    unittest.main()
