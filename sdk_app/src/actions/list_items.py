"""Create and update SharePoint list items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure

from ..client import GraphClient, encode_path_segment

if TYPE_CHECKING:
    from ..app import AddItemOutput, AddItemParams, Asset, UpdateItemOutput, UpdateItemParams


class ListItemSummary(ActionOutput):
    sites_count: int = OutputField(example_values=[1])


def add_item(params: AddItemParams, soar: SOARClient, asset: Asset) -> AddItemOutput:
    """Add one list item with the legacy Graph request and summary contract."""
    try:
        list_id = encode_path_segment(params.list)
    except ValueError as exc:
        raise ActionFailure(f"Invalid list ID: {exc}") from exc

    endpoint = f"/sites/{asset.site_id}/lists/{list_id}/items"
    with GraphClient(asset) as graph:
        response = graph.request(
            "POST", endpoint, data=params.item.encode("utf-8")
        )

    from ..app import AddItemOutput

    output = AddItemOutput.model_validate(response)
    soar.set_summary(ListItemSummary(sites_count=1))
    return output


def update_item(
    params: UpdateItemParams, soar: SOARClient, asset: Asset
) -> UpdateItemOutput:
    """Update one list item with the existing legacy request contract."""
    try:
        list_id = encode_path_segment(params.list)
        item_id = encode_path_segment(params.item_id)
    except ValueError as exc:
        raise ActionFailure(f"Invalid list or item ID: {exc}") from exc

    endpoint = f"/sites/{asset.site_id}/lists/{list_id}/items/{item_id}"
    with GraphClient(asset) as graph:
        response = graph.request(
            "PATCH", endpoint, data=params.item.encode("utf-8")
        )

    from ..app import UpdateItemOutput

    output = UpdateItemOutput.model_validate(response)
    soar.set_summary(ListItemSummary(sites_count=1))
    return output
