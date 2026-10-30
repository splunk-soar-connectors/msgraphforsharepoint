"""SDK action boundary for the SharePoint list_sites action."""

from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from ..auth import get_graph_client
from ._graph import _paginate
from ._limits import validate_limit
from ..asset import Asset


class SitesSummary(ActionOutput):
    sites_count: int = OutputField(example_values=[1])


class ListSitesParams(Params):
    limit: float | None = Param(description="Maximum number of sites to return")


class SitecollectionOutput(PermissiveActionOutput):
    hostname: str = OutputField(
        cef_types=["host name"],
        example_values=["tenant-name.sharepoint.com"],
        column_name="Hostname",
    )


class ListSitesOutput(PermissiveActionOutput):
    createdDateTime: str = OutputField(example_values=["2016-10-31T20:25:06Z"])
    displayName: str = OutputField(
        example_values=["Test Site Name"], column_name="Sharepoint Site Name"
    )
    id: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,595384ee-13aa-49d1-814b-00ed3e024cde,70abfe37-8aa1-4168-b83e-41b6e9721509"
        ],
        column_name="Sharepoint Site ID",
    )
    isPersonalSite: bool
    lastModifiedDateTime: str = OutputField(
        example_values=["2022-02-16T12:12:25.9162131Z"]
    )
    name: str = OutputField(example_values=["Test Site Name"])
    siteCollection: SitecollectionOutput
    webUrl: str = OutputField(
        cef_types=["url"],
        example_values=["https://test-tenant-name.sharepoint.com/search"],
    )


def list_sites(
    params: ListSitesParams, soar: SOARClient, asset: Asset
) -> list[ListSitesOutput]:
    """Return SharePoint sites and the legacy `sites_count` summary."""

    try:
        limit = validate_limit(params.limit)
    except ValueError as exc:
        raise ActionFailure(str(exc)) from exc
    with get_graph_client(asset) as graph:
        sites = _paginate(graph, "/sites", limit=limit)
    outputs = [ListSitesOutput.model_validate(site) for site in sites]
    soar.set_summary(SitesSummary(sites_count=len(outputs)))
    return outputs
