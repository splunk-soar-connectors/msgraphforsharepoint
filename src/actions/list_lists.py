"""SDK action boundary for the SharePoint list_lists action."""

from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ._graph import _paginate
from ._limits import validate_limit
from ..asset import Asset


class ListListsSummary(ActionOutput):
    lists_count: int = OutputField(example_values=[1])


class ListListsParams(Params):
    limit: float | None = Param(description="Maximum number of sites to return")


class UserOutput(PermissiveActionOutput):
    displayName: str = OutputField(example_values=["Test User"])
    email: str = OutputField(
        cef_types=["email"], example_values=["test_user@tenant-name.ontest.com"]
    )
    id: str = OutputField(example_values=["eeb3645f-df19-47a1-8e8c-fcd234cb5f6f"])


class CreatedbyOutput(PermissiveActionOutput):
    user: UserOutput


class LastmodifiedbyOutput(PermissiveActionOutput):
    user: UserOutput


class ListOutput(PermissiveActionOutput):
    contentTypesEnabled: bool
    hidden: bool
    template: str = OutputField(example_values=["genericList"])


class ParentreferenceOutput(PermissiveActionOutput):
    siteId: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa"
        ]
    )


class ListListsOutput(PermissiveActionOutput):
    etag: str = OutputField(alias="@odata.etag")
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2022-02-24T05:38:53Z"])
    description: str = OutputField(example_values=["Test List Description"])
    displayName: str = OutputField(
        cef_types=["sharepoint list name"],
        example_values=["ListName"],
        column_name="List Name",
    )
    eTag: str = OutputField(example_values=['"4896b66a-659c-4fce-a148-0b26bd718f68,5"'])
    id: str = OutputField(
        cef_types=["sharepoint list id"],
        example_values=["4896b66a-659c-4fce-a148-0b26bd718f68"],
        column_name="List ID",
    )
    lastModifiedBy: LastmodifiedbyOutput
    lastModifiedDateTime: str = OutputField(example_values=["2022-03-03T13:43:06Z"])
    list: ListOutput
    name: str = OutputField(example_values=["ListName"])
    parentReference: ParentreferenceOutput
    webUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/SiteName/Lists/ListName"
        ],
    )


def list_lists(
    params: ListListsParams, soar: SOARClient, asset: Asset
) -> list[ListListsOutput]:
    """List SharePoint lists and set the legacy `lists_count` summary."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving lists information from specific site"
        )

    try:
        limit = validate_limit(params.limit)
    except ValueError as exc:
        raise ActionFailure(str(exc)) from exc
    with get_graph_client(asset) as graph:
        lists = _paginate(graph, f"/sites/{asset.site_id}/lists", limit=limit)

    outputs = [ListListsOutput.model_validate(list_info) for list_info in lists]
    soar.set_summary(ListListsSummary(lists_count=len(outputs)))
    return outputs
