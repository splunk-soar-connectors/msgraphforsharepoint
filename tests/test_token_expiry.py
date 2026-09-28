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
        self.message = ""

    def set_status(self, status, message=None):
        self.status = status
        self.message = message or ""
        return status

    def get_status(self):
        return self.status

    def get_message(self):
        return self.message


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

    def __init__(
        self,
        token=None,
        token_error=False,
        graph_error_message=None,
        valid_authorizations=("Bearer fresh",),
        token_response=None,
    ):
        self._state = {"token": token or {}}
        self._access_token = self._state["token"].get("access_token")
        self.token_error = token_error
        self.graph_error_message = graph_error_message or (
            "Error from server. Status Code: 401 Data from server: InvalidAuthenticationToken. Invalid token lifetime."
        )
        self.valid_authorizations = valid_authorizations
        self.token_response = token_response or {"access_token": "fresh", "expires_in": 3600}
        self.calls = []

    def save_progress(self, _message):
        pass

    def _make_rest_call(
        self, endpoint, action_result, verify=True, headers=None, params=None, data=None, json=None, method="get", download=False
    ):
        self.calls.append((endpoint, dict(headers or {}), method, download, data))
        if endpoint.startswith("https://login.microsoftonline.com/"):
            if self.token_error:
                return action_result.set_status(_Phantom.APP_ERROR, "Token request failed"), None
            return _Phantom.APP_SUCCESS, self.token_response
        if headers["Authorization"] not in self.valid_authorizations:
            return action_result.set_status(_Phantom.APP_ERROR, self.graph_error_message), None
        if download:
            return _Phantom.APP_SUCCESS, "/tmp/sharepoint-download"
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

    def test_legacy_token_without_expiry_is_refreshed_after_graph_rejects_it(self):
        connector = _Connector({"access_token": "stale", "expires_in": 3600})

        status, _ = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(len(connector.calls), 3)
        self.assertEqual(connector.calls[0][1]["Authorization"], "Bearer stale")
        self.assertEqual(connector.calls[2][1]["Authorization"], "Bearer fresh")

    def test_valid_legacy_token_is_used_without_refresh(self):
        connector = _Connector(
            {"access_token": "legacy", "expires_in": 3600},
            token_error=True,
            valid_authorizations=("Bearer fresh", "Bearer legacy"),
        )

        status, response = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, {"value": "ok"})
        self.assertEqual(len(connector.calls), 1)
        self.assertEqual(connector.calls[0][1]["Authorization"], "Bearer legacy")

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

    def test_failed_refresh_after_graph_rejection_returns_error(self):
        connector = _Connector({"access_token": "stale", "expires_at": 4540}, token_error=True)
        action_result = _ActionResult()

        status, response = connector._make_rest_call_helper("/sites/root", action_result)

        self.assertEqual(status, _Phantom.APP_ERROR)
        self.assertEqual(action_result.get_status(), _Phantom.APP_ERROR)
        self.assertIsNone(response)
        self.assertEqual(len(connector.calls), 2)

    def test_graph_failure_after_retry_remains_an_error(self):
        connector = _Connector({"access_token": "stale", "expires_at": 4540}, valid_authorizations=())
        action_result = _ActionResult()

        status, response = connector._make_rest_call_helper("/sites/root", action_result)

        self.assertEqual(status, _Phantom.APP_ERROR)
        self.assertEqual(action_result.get_status(), _Phantom.APP_ERROR)
        self.assertIsNone(response)
        self.assertEqual(len(connector.calls), 3)

    def test_force_refreshes_before_graph_request(self):
        connector = _Connector({"access_token": "stale", "expires_at": 4540})

        status, response = connector._make_rest_call_helper("/sites/root", _ActionResult(), is_force=True)

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, {"value": "ok"})
        self.assertEqual(len(connector.calls), 2)
        self.assertEqual(connector.calls[0][2], "post")
        self.assertEqual(connector.calls[1][1]["Authorization"], "Bearer fresh")

    def test_download_retries_with_download_enabled(self):
        connector = _Connector({"access_token": "stale", "expires_at": 4540})

        status, response = connector._make_rest_call_helper("/content", _ActionResult(), download=True)

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, "/tmp/sharepoint-download")
        self.assertEqual(len(connector.calls), 3)
        self.assertTrue(connector.calls[0][3])
        self.assertTrue(connector.calls[2][3])

    def test_write_retry_preserves_payload(self):
        connector = _Connector({"access_token": "stale", "expires_at": 4540})
        payload = b'{"name":"item"}'

        status, response = connector._make_rest_call_helper("/items", _ActionResult(), data=payload, method="post")

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, {"value": "ok"})
        self.assertEqual(len(connector.calls), 3)
        self.assertEqual(connector.calls[0][2:], ("post", False, payload))
        self.assertEqual(connector.calls[2][2:], ("post", False, payload))

    def test_invalid_token_lifetime_does_not_discard_access_token(self):
        connector = _Connector(token_response={"access_token": "fresh", "expires_in": "invalid"})

        status, response = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, {"value": "ok"})
        self.assertEqual(len(connector.calls), 2)

    def test_invalid_saved_expiry_uses_cached_token(self):
        connector = _Connector({"access_token": "legacy", "expires_at": "invalid"}, valid_authorizations=("Bearer fresh", "Bearer legacy"))

        status, response = connector._make_rest_call_helper("/sites/root", _ActionResult())

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, {"value": "ok"})
        self.assertEqual(len(connector.calls), 1)

    def test_graph_token_failure_refreshes_and_retries(self):
        messages = (
            "Error from server. Status Code: 401 Data from server: token expired",
            "Error from server. Status Code: 401 Data from server: InvalidAuthenticationToken. Invalid token lifetime.",
        )
        for message in messages:
            with self.subTest(message=message):
                connector = _Connector({"access_token": "stale", "expires_at": 4540}, graph_error_message=message)
                action_result = _ActionResult()

                status, response = connector._make_rest_call_helper("/sites/root", action_result)

                self.assertEqual(status, _Phantom.APP_SUCCESS)
                self.assertEqual(action_result.get_status(), _Phantom.APP_SUCCESS)
                self.assertEqual(response, {"value": "ok"})
                self.assertEqual(len(connector.calls), 3)
                self.assertEqual(connector.calls[0][1]["Authorization"], "Bearer stale")
                self.assertEqual(connector.calls[2][1]["Authorization"], "Bearer fresh")

    def test_successful_graph_call_does_not_retry_stale_error_message(self):
        connector = _Connector({"access_token": "fresh", "expires_at": 4540})
        action_result = _ActionResult()
        action_result.set_status(_Phantom.APP_SUCCESS, "token expired")

        status, response = connector._make_rest_call_helper("/sites/root", action_result)

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(response, {"value": "ok"})
        self.assertEqual(len(connector.calls), 1)


if __name__ == "__main__":
    unittest.main()
