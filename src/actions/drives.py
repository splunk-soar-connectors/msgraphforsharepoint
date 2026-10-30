"""SDK action boundary for the SharePoint list_drives action."""

from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _paginate
from ._paths import encode_path_segment
from ._limits import validate_limit
from ..asset import Asset


class DrivesSummary(ActionOutput):
    drives_count: int = OutputField(example_values=[1])


class UserOutput(PermissiveActionOutput):
    displayName: str | None = OutputField(example_values=["Test User"])
    email: str | None = OutputField(cef_types=["email"])
    id: str | None = OutputField()


class GroupOutput(PermissiveActionOutput):
    id: str | None = OutputField()
    email: str | None = OutputField(cef_types=["email"])
    displayName: str | None = OutputField()


class OwnerOutput(PermissiveActionOutput):
    user: UserOutput | None = OutputField()
    group: GroupOutput | None = OutputField()


class QuotaOutput(PermissiveActionOutput):
    used: float | None = OutputField(example_values=[8546734])
    state: str | None = OutputField(example_values=["normal"])
    total: float | None = OutputField(example_values=[274877685])
    deleted: float | None = OutputField(example_values=[0])
    remaining: float | None = OutputField(example_values=[266330951])


class CreatedByOutput(PermissiveActionOutput):
    user: UserOutput | None = OutputField()


class LastModifiedByOutput(PermissiveActionOutput):
    user: UserOutput | None = OutputField()


class ListDrivesOutput(PermissiveActionOutput):
    name: str | None = OutputField(
        example_values=["Custom Library"], column_name="Drive Name"
    )
    id: str | None = OutputField(column_name="Drive ID")
    owner: OwnerOutput | None = OutputField()
    quota: QuotaOutput | None = OutputField()
    createdBy: CreatedByOutput | None = OutputField()
    createdDateTime: str | None = OutputField()
    description: str | None = OutputField(example_values=["Test List Description"])
    driveType: str | None = OutputField(example_values=["documentLibrary"])
    lastModifiedBy: LastModifiedByOutput | None = OutputField()
    lastModifiedDateTime: str | None = OutputField()
    webUrl: str | None = OutputField(cef_types=["url"])


class ListDrivesParams(Params):
    limit: float | None = Param(description="Maximum number of drives to return")


def list_drives(
    params: ListDrivesParams, soar: SOARClient, asset: Asset
) -> list[ListDrivesOutput]:
    """List drives for the configured SharePoint site."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving drives information from specific site"
        )

    try:
        limit = validate_limit(params.limit)
    except ValueError as exc:
        raise ActionFailure(str(exc)) from exc
    with get_graph_client(asset) as graph:
        drives = _paginate(graph, f"/sites/{asset.site_id}/drives", limit=limit)

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
