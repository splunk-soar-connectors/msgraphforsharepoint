"""SDK action boundary for the SharePoint copy_drive_item action."""

import json
import time
from typing import Any

import httpx
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _parse_graph_response, _send_graph_request
from ._paths import encode_path_segment
from .drives import drive_root_endpoint
from ..asset import Asset


COPY_OPERATION_TIMEOUT_SECONDS = 300.0
COPY_OPERATION_INITIAL_POLL_INTERVAL_SECONDS = 1.0
COPY_OPERATION_MAX_POLL_INTERVAL_SECONDS = 5.0
COPY_MONITOR_HOSTS = {"api.onedrive.com"}
COPY_MONITOR_HOST_SUFFIXES = (".sharepoint.com",)


class CopyDriveItemOutput(PermissiveActionOutput):
    """Preserve the legacy action's unstructured Graph response payload."""


class CopyDriveItemParams(Params):
    source_item_id: str = Param(
        description="ID for drive item that needs to be copied",
        primary=True,
        cef_types=["sharepoint drive item id"],
    )
    source_drive_id: str | None = Param(
        description="Drive ID that contains the source item to copy. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    dest_drive_id: str | None = Param(
        description="Drive ID that contains target folder to copy item to. If no id is specified the default drive will be used",
        primary=True,
        cef_types=["sharepoint drive id"],
    )
    dest_folder_id: str = Param(
        description="ID of target folder to copy drive item to",
        primary=True,
        cef_types=["sharepoint drive item id"],
    )
    file_name: str | None = Param(
        description="Optional new folder/file name for the copy. If not provided will use the original name"
    )


def _validate_copy_monitor_url(
    location: str, *, allowed_hosts: set[str] | None = None
) -> str:
    """Validate Graph's unauthenticated, short-lived copy monitor URL."""
    try:
        url = httpx.URL(location)
    except (TypeError, ValueError) as exc:
        raise ActionFailure(
            "Microsoft Graph returned an invalid copy monitor URL"
        ) from exc

    host = url.host.lower()
    test_host = allowed_hosts is not None and host in allowed_hosts
    allowlisted_host = (
        host in COPY_MONITOR_HOSTS
        or any(host.endswith(suffix) for suffix in COPY_MONITOR_HOST_SUFFIXES)
        or test_host
    )
    valid_transport = (
        test_host and url.scheme in {"http", "https"}
    ) or (url.scheme == "https" and url.port in (None, 443))

    valid_monitor_path = "/monitor/" in url.path and url.path.rsplit("/", 1)[-1] != ""
    if (
        not url.is_absolute_url
        or not allowlisted_host
        or not valid_transport
        or not valid_monitor_path
        or url.username
        or url.password
        or url.fragment
    ):
        raise ActionFailure("Rejected Microsoft Graph copy monitor URL")

    return str(url)


def _copy_monitor_status(response: httpx.Response) -> dict[str, Any]:
    if response.status_code not in {200, 202, 303}:
        raise ActionFailure("Microsoft Graph copy monitor request failed")

    try:
        payload = response.json()
    except (ValueError, UnicodeDecodeError) as exc:
        raise ActionFailure("Microsoft Graph returned an invalid copy status") from exc
    if not isinstance(payload, dict):
        raise ActionFailure("Microsoft Graph returned an invalid copy status")
    return payload


def _wait_for_copy_completion(
    monitor_location: str,
    client: httpx.Client,
    *,
    timeout_seconds: float = COPY_OPERATION_TIMEOUT_SECONDS,
    initial_poll_interval_seconds: float = COPY_OPERATION_INITIAL_POLL_INTERVAL_SECONDS,
    max_poll_interval_seconds: float = COPY_OPERATION_MAX_POLL_INTERVAL_SECONDS,
    allowed_hosts: set[str] | None = None,
) -> dict[str, Any]:
    """Poll the unauthenticated monitor URL until the copy succeeds or fails."""
    monitor_url = _validate_copy_monitor_url(
        monitor_location, allowed_hosts=allowed_hosts
    )
    deadline = time.monotonic() + timeout_seconds
    poll_interval = initial_poll_interval_seconds

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ActionFailure("Timed out waiting for Microsoft Graph copy to complete")

        try:
            response = client.get(
                monitor_url,
                follow_redirects=False,
                timeout=min(10.0, remaining),
            )
        except httpx.RequestError as exc:
            raise ActionFailure("Error checking Microsoft Graph copy status") from exc

        status = _copy_monitor_status(response)
        operation_status = status.get("status")
        if operation_status == "completed":
            return status
        if operation_status == "failed":
            raise ActionFailure("Microsoft Graph copy operation failed")
        if not isinstance(operation_status, str) or operation_status not in {
            "notStarted",
            "inProgress",
        }:
            raise ActionFailure("Microsoft Graph returned an unknown copy status")

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ActionFailure("Timed out waiting for Microsoft Graph copy to complete")
        time.sleep(min(poll_interval, remaining))
        poll_interval = min(poll_interval * 1.5, max_poll_interval_seconds)


def copy_drive_item(
    params: CopyDriveItemParams, soar: SOARClient, asset: Asset
) -> CopyDriveItemOutput:
    """Copy a drive item using the legacy request body and success message."""
    try:
        source_item_id = encode_path_segment(params.source_item_id)
    except ValueError as exc:
        raise ActionFailure(f"Invalid source item ID: {exc}") from exc

    endpoint = (
        f"{drive_root_endpoint(str(asset.site_id), params.source_drive_id)}"
        f"/items/{source_item_id}/copy"
    )
    parent_reference: dict[str, Any] = {"id": params.dest_folder_id}
    if params.dest_drive_id:
        parent_reference["driveId"] = params.dest_drive_id
    request_body: dict[str, Any] = {"parentReference": parent_reference}
    if params.file_name:
        request_body["name"] = params.file_name

    with get_graph_client(asset) as graph:
        graph_response = _send_graph_request(
            graph, "POST", endpoint, content=json.dumps(request_body)
        )
        response = _parse_graph_response(graph_response)

    if graph_response.status_code == 202:
        monitor_location = graph_response.headers.get("Location")
        if not monitor_location:
            raise ActionFailure(
                "Microsoft Graph accepted the copy but returned no monitor URL"
            )
        with httpx.Client(timeout=10.0, follow_redirects=False) as monitor_client:
            _wait_for_copy_completion(monitor_location, monitor_client)

    soar.set_message("Successfully copied an item")
    return CopyDriveItemOutput(**response)
