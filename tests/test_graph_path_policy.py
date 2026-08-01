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
import urllib.parse
from pathlib import Path


CONNECTOR = Path(__file__).resolve().parents[1] / "msgraphforsharepoint_connector.py"


def _load_path_helpers():
    source = CONNECTOR.read_text()
    tree = ast.parse(source)
    helpers = [
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {"_encode_graph_path_segment", "_encode_graph_path"}
    ]
    namespace = {"urllib": urllib}
    exec(compile(ast.fix_missing_locations(ast.Module(body=helpers, type_ignores=[])), str(CONNECTOR), "exec"), namespace)
    return namespace["_encode_graph_path_segment"], namespace["_encode_graph_path"]


class GraphPathPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encode_segment, cls.encode_path = map(staticmethod, _load_path_helpers())

    def test_encodes_each_path_component(self):
        self.assertEqual(self.encode_path("reports/July 2026"), "reports/July%202026")
        self.assertEqual(self.encode_segment("item id"), "item%20id")
        self.assertEqual(self.encode_path("/", allow_empty=True), "")

    def test_rejects_dot_segments_and_encoded_separators(self):
        payloads = (".", "..", "%2e%2e", "%252e%252e", "a%2fb", "a%255cb", "a?x", "a#x")
        for payload in payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    self.encode_segment(payload)

    def test_rejects_dot_segments_inside_paths(self):
        for payload in ("reports/../admin", "reports/%2e%2e/admin", "reports//admin"):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    self.encode_path(payload)


if __name__ == "__main__":
    unittest.main()
