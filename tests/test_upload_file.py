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
"""Focused tests for SharePoint upload path and streaming behavior."""

from io import BytesIO

import pytest

from src.actions.upload_file import _file_chunks, _upload_endpoint


def test_upload_endpoint_targets_default_drive_library_root() -> None:
    assert (
        _upload_endpoint("site-id", None, None, "report.pdf")
        == "/sites/site-id/drive/root:/report.pdf:/content"
    )


def test_upload_endpoint_targets_drive_and_encoded_folder_path() -> None:
    assert (
        _upload_endpoint("site-id", "drive-id", "Shared Documents/Reports", "Q1 report.pdf")
        == "/sites/site-id/drives/drive-id/root:/Shared%20Documents/Reports/Q1%20report.pdf:/content"
    )


@pytest.mark.parametrize(
    ("file_path", "file_name"),
    [("../outside", "report.pdf"), ("Reports", "../report.pdf"), ("Reports", "bad/name.pdf")],
)
def test_upload_endpoint_rejects_traversal_and_path_delimiters(
    file_path: str, file_name: str
) -> None:
    with pytest.raises(ValueError, match="Invalid file path or name"):
        _upload_endpoint("site-id", None, file_path, file_name)


def test_upload_endpoint_rejects_drive_id_path_delimiters() -> None:
    with pytest.raises(ValueError, match="Invalid drive ID"):
        _upload_endpoint("site-id", "bad/drive-id", "Reports", "report.pdf")


def test_file_chunks_read_in_bounded_blocks() -> None:
    content = b"0123456789"
    chunks = list(_file_chunks(BytesIO(content), chunk_size=3))

    assert b"".join(chunks) == content
    assert [len(chunk) for chunk in chunks] == [3, 3, 3, 1]
