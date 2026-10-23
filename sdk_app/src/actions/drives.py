"""Actions for SharePoint drive libraries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure

from ..client import GraphClient, encode_path_segment, validate_limit

if TYPE_CHECKING:
    from ..app import Asset, ListDrivesParams


class DrivesSummary(ActionOutput):
    drives_count: int = OutputField(example_values=[1])


class UserOutput(ActionOutput):
    displayName: str | None = OutputField(example_values=["Test User"])
    email: str | None = OutputField(cef_types=["email"])
    id: str | None = OutputField()


class GroupOutput(ActionOutput):
    id: str | None = OutputField()
    email: str | None = OutputField(cef_types=["email"])
    displayName: str | None = OutputField()


class OwnerOutput(ActionOutput):
    user: UserOutput | None = OutputField()
    group: GroupOutput | None = OutputField()


class QuotaOutput(ActionOutput):
    used: float | None = OutputField(example_values=[8546734])
    state: str | None = OutputField(example_values=["normal"])
    total: float | None = OutputField(example_values=[274877685])
    deleted: float | None = OutputField(example_values=[0])
    remaining: float | None = OutputField(example_values=[266330951])


class CreatedByOutput(ActionOutput):
    user: UserOutput | None = OutputField()


class LastModifiedByOutput(ActionOutput):
    user: UserOutput | None = OutputField()


class ListDrivesOutput(ActionOutput):
    id: str | None = OutputField()
    name: str | None = OutputField(example_values=["Custom Library"])
    owner: OwnerOutput | None = OutputField()
    quota: QuotaOutput | None = OutputField()
    createdBy: CreatedByOutput | None = OutputField()
    createdDateTime: str | None = OutputField()
    description: str | None = OutputField(example_values=["Test List Description"])
    driveType: str | None = OutputField(example_values=["documentLibrary"])
    lastModifiedBy: LastModifiedByOutput | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()
    webUrl: str | None = OutputField(cef_types=["url"])


def list_drives(
    params: ListDrivesParams, soar: SOARClient, asset: Asset
) -> list[ListDrivesOutput]:
    """List drives for the configured SharePoint site."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving drives information from specific site"
        )

    limit = validate_limit(params.limit)
    with GraphClient(asset) as graph:
        drives = graph.paginate(f"/sites/{asset.site_id}/drives", limit=limit)

    outputs = [ListDrivesOutput.model_validate(drive) for drive in drives]
    soar.set_summary(DrivesSummary(drives_count=len(outputs)))
    return outputs


def drive_children_endpoint(site_id: str, drive_id: str | None) -> str:
    """Build the legacy default-drive or named-drive children endpoint."""
    return f"{drive_root_endpoint(site_id, drive_id)}/items/root/children"


def drive_root_endpoint(site_id: str, drive_id: str | None) -> str:
    """Build the legacy default-drive or named-drive root endpoint."""
    if drive_id:
        encoded_drive_id = encode_path_segment(drive_id)
        return f"/sites/{site_id}/drives/{encoded_drive_id}"
    return f"/sites/{site_id}/drive"
