"""Site discovery actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField

from ..client import GraphClient, validate_limit

if TYPE_CHECKING:
    from ..app import Asset, ListSitesParams, ListSitesOutput


class SitesSummary(ActionOutput):
    sites_count: int = OutputField(example_values=[1])


def list_sites(
    params: ListSitesParams, soar: SOARClient, asset: Asset
) -> list[ListSitesOutput]:
    """Return SharePoint sites and the legacy `sites_count` summary."""
    from ..app import ListSitesOutput

    limit = validate_limit(params.limit)
    with GraphClient(asset) as graph:
        sites = graph.paginate("/sites", limit=limit)
    outputs = [ListSitesOutput.model_validate(site) for site in sites]
    soar.set_summary(SitesSummary(sites_count=len(outputs)))
    return outputs
