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
import os
import tempfile
import unittest
from pathlib import Path

from tests.test_token_expiry import _ActionResult, _Clock, _Connector, _Phantom


CONNECTOR = Path(__file__).resolve().parents[1] / "msgraphforsharepoint_connector.py"


def _load(names):
    tree = ast.parse(CONNECTOR.read_text())
    module_functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    connector_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MsGraphForSharepointConnector")
    methods = [node for node in connector_class.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {
        "phantom": _Phantom,
        "time": _Clock,
        "urllib": __import__("urllib.parse"),
        "ActionResult": _ActionResult,
        "MS_SHAREPOINT_JSON_VAULT_ID": "vault_id",
        "MS_SHAREPOINT_JSON_FILE_PATH": "file_path",
        "MS_SHAREPOINT_JSON_FILE_NAME": "file_name",
        "MS_SHAREPOINT_JSON_DRIVE_ID": "drive_id",
        "MS_SHAREPOINT_ERROR_MISSING_SITE_ID": "Site ID required for {}",
        "MS_UPLOAD_FILE_ENDPOINT": "/root:/{path}:/content",
        "MS_DRIVE_ROOT_ENDPOINT": "/sites/{site_id}/drive",
        "MS_CUSTOM_DRIVE_ROOT_ENDPOINT": "/sites/{site_id}/drives/{drive_id}",
    }
    exec(compile(ast.fix_missing_locations(ast.Module(body=module_functions + methods, type_ignores=[])), str(CONNECTOR), "exec"), namespace)
    return namespace


_NS = _load({"_encode_graph_path_segment", "_encode_graph_path", "_handle_upload_file", "build_drive_endpoint"})


class _VaultRules:
    def __init__(self, path, name="report.docx"):
        self.path = path
        self.name = name

    def vault_info(self, vault_id, container_id):
        if vault_id != "abc":
            return False, "not found", []
        return True, "", [{"path": self.path, "name": self.name}]


class _UploadConnector(_Connector):
    _handle_upload_file = _NS["_handle_upload_file"]
    build_drive_endpoint = _NS["build_drive_endpoint"]

    def get_container_id(self):
        return 1

    def _get_error_message_from_exception(self, e):
        return str(e)


class UploadFileTests(unittest.TestCase):
    def setUp(self):
        _Clock.now = 1000
        fd, self.path = tempfile.mkstemp()
        os.write(fd, b"\x00binary")
        os.close(fd)
        _NS["ph_rules"] = _VaultRules(self.path)

    def tearDown(self):
        os.remove(self.path)

    def test_upload_sends_binary_body_to_encoded_path(self):
        connector = _UploadConnector({"access_token": "fresh", "expires_at": 5000})

        status = connector._handle_upload_file({"vault_id": "abc", "file_path": "/Reports/Oct 2026/"})

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        endpoint, headers, method, _, data = connector.calls[-1]
        self.assertEqual(endpoint, "https://graph.microsoft.com/v1.0/sites/site/drive/root:/Reports/Oct%202026/report.docx:/content")
        self.assertEqual(method, "put")
        self.assertEqual(headers["Content-Type"], "application/octet-stream")
        self.assertEqual(data, b"\x00binary")

    def test_upload_refreshes_token_on_invalid_token_lifetime(self):
        connector = _UploadConnector({"access_token": "stale"})

        status = connector._handle_upload_file({"vault_id": "abc", "file_name": "renamed.docx"})

        self.assertEqual(status, _Phantom.APP_SUCCESS)
        self.assertEqual(connector.calls[0][1]["Authorization"], "Bearer stale")
        self.assertEqual(connector.calls[-1][1]["Authorization"], "Bearer fresh")
        self.assertTrue(connector.calls[-1][0].endswith("/root:/renamed.docx:/content"))

    def test_upload_rejects_traversal_in_file_name(self):
        connector = _UploadConnector({"access_token": "fresh", "expires_at": 5000})

        status = connector._handle_upload_file({"vault_id": "abc", "file_name": "../x"})

        self.assertEqual(status, _Phantom.APP_ERROR)
        self.assertEqual(connector.calls, [])

    def test_upload_fails_for_unknown_vault_id(self):
        connector = _UploadConnector({"access_token": "fresh", "expires_at": 5000})

        status = connector._handle_upload_file({"vault_id": "missing"})

        self.assertEqual(status, _Phantom.APP_ERROR)
        self.assertEqual(connector.calls, [])


if __name__ == "__main__":
    unittest.main()
