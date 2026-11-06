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
"""Copy operation monitor contract tests using a real local HTTP server."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

import httpx
import pytest
from soar_sdk.exceptions import ActionFailure

from src.actions.copy_drive_item import (
    _validate_copy_monitor_url,
    _wait_for_copy_completion,
)


class CopyStatusHandler(BaseHTTPRequestHandler):
    statuses: list[tuple[int, dict[str, Any]]] = []

    def do_GET(self) -> None:
        status_code, payload = self.statuses.pop(0)
        body = json.dumps(payload).encode()
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture
def monitor_server():
    handler = type(
        "TestCopyStatusHandler",
        (CopyStatusHandler,),
        {"statuses": []},
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/monitor/operation-id", handler
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_copy_monitor_waits_until_operation_completes(monitor_server) -> None:
    monitor_url, handler = monitor_server
    handler.statuses = [
        (202, {"status": "inProgress"}),
        (200, {"status": "completed", "resourceId": "copied-item"}),
    ]

    with httpx.Client() as client:
        result = _wait_for_copy_completion(
            monitor_url,
            client,
            initial_poll_interval_seconds=0,
            allowed_hosts={"127.0.0.1"},
        )

    assert result == {"status": "completed", "resourceId": "copied-item"}
    assert handler.statuses == []


def test_copy_monitor_raises_when_operation_fails(monitor_server) -> None:
    monitor_url, handler = monitor_server
    handler.statuses = [
        (200, {"status": "failed", "error": {"code": "copyFailed"}})
    ]

    with httpx.Client() as client, pytest.raises(
        ActionFailure, match="copy operation failed"
    ) as failure:
        _wait_for_copy_completion(
            monitor_url,
            client,
            allowed_hosts={"127.0.0.1"},
        )

    assert "127.0.0.1" not in str(failure.value)


@pytest.mark.parametrize(
    "location",
    [
        "http://example.com/monitor/id",
        "https://example.com/monitor/id",
        "https://user:password@tenant.sharepoint.com/monitor/id",
        "https://tenant.sharepoint.com/not-a-monitor/id",
    ],
)
def test_copy_monitor_rejects_untrusted_urls(location: str) -> None:
    with pytest.raises(ActionFailure):
        _validate_copy_monitor_url(location)


def test_copy_monitor_accepts_trailing_slash_after_operation_id() -> None:
    assert _validate_copy_monitor_url(
        "http://127.0.0.1:8123/_api/v2.1/monitor/operation-id/",
        allowed_hosts={"127.0.0.1"},
    ) == "http://127.0.0.1:8123/_api/v2.1/monitor/operation-id/"
