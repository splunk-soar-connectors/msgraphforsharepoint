"""List SharePoint lists and retrieve a list with its columns and items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure

from ..client import GraphClient, encode_path_segment, validate_limit

if TYPE_CHECKING:
    from ..app import Asset, GetListOutput, GetListParams, ListListsOutput, ListListsParams


class ListListsSummary(ActionOutput):
    lists_count: int = OutputField(example_values=[1])


class GetListSummary(ActionOutput):
    item_count: int = OutputField(example_values=[1])


def list_lists(
    params: ListListsParams, soar: SOARClient, asset: Asset
) -> list[ListListsOutput]:
    """List SharePoint lists and set the legacy `lists_count` summary."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving lists information from specific site"
        )

    limit = validate_limit(params.limit)
    with GraphClient(asset) as graph:
        lists = graph.paginate(f"/sites/{asset.site_id}/lists", limit=limit)

    from ..app import ListListsOutput

    outputs = [ListListsOutput.model_validate(list_info) for list_info in lists]
    soar.set_summary(ListListsSummary(lists_count=len(outputs)))
    return outputs


def get_list(
    params: GetListParams, soar: SOARClient, asset: Asset
) -> GetListOutput:
    """Retrieve one list, its columns, and its fields-expanded items."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving a list from specific site"
        )

    limit = validate_limit(params.limit)
    try:
        encoded_list_id = encode_path_segment(params.list)
    except ValueError as exc:
        raise ActionFailure(f"Invalid list ID: {exc}") from exc

    endpoint = f"/sites/{asset.site_id}/lists/{encoded_list_id}"
    with GraphClient(asset) as graph:
        list_info = graph.request("GET", endpoint, params={"expand": "columns"})
        items = graph.paginate(
            f"{endpoint}/items",
            params={"expand": "fields"},
            limit=limit,
        )

    list_info["items"] = items
    from ..app import GetListOutput

    output = GetListOutput.model_validate(list_info)
    soar.set_summary(GetListSummary(item_count=len(items)))
    return output
