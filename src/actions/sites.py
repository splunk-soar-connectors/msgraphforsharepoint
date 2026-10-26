"""SDK action boundary for the SharePoint list_sites action."""

import httpx
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
from ._limits import validate_limit
from ..asset import Asset


class SitesSummary(ActionOutput):
    sites_count: int = OutputField(example_values=[1])


class ListSitesParams(Params):
    limit: float | None = Param(description="Maximum number of sites to return")


class SitecollectionOutput(PermissiveActionOutput):
    hostname: str = OutputField(
        cef_types=["host name"], example_values=["tenant-name.sharepoint.com"]
    )


class ListSitesOutput(PermissiveActionOutput):
    createdDateTime: str = OutputField(example_values=["2016-10-31T20:25:06Z"])
    displayName: str = OutputField(example_values=["Test Site Name"])
    id: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,595384ee-13aa-49d1-814b-00ed3e024cde,70abfe37-8aa1-4168-b83e-41b6e9721509"
        ]
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


def _request_graph(client: httpx.Client, method: str, endpoint: str, **kwargs):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request_headers = kwargs.pop("headers", {})
    headers.update(request_headers)
    try:
        response = client.request(
            method, endpoint, headers=headers, follow_redirects=False, **kwargs
        )
    except httpx.RequestError as exc:
        raise ActionFailure("Error connecting to Microsoft Graph") from exc
    try:
        return get_graph_response(response)
    except GraphResponseError as exc:
        raise ActionFailure(str(exc)) from exc


def _paginate(
    client: httpx.Client,
    endpoint: str,
    *,
    limit: int | None = None,
    params: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    """Follow Graph pages for this action, guarding against loops and runaway pages."""
    page_params = dict(params or {})
    page_params["$top"] = min(limit, 1000) if limit else 1000
    results: list[dict[str, object]] = []
    next_link: str | None = None
    seen_links: set[str] = set()
    for _ in range(1000):
        page = _request_graph(
            client,
            "GET",
            next_link or endpoint,
            **({} if next_link else {"params": page_params}),
        )
        if not isinstance(page, dict):
            raise ActionFailure("Microsoft Graph returned an invalid page")
        value = page.get("value", [])
        if not isinstance(value, list) or not all(
            isinstance(item, dict) for item in value
        ):
            raise ActionFailure("Microsoft Graph returned an invalid page value")
        results.extend(value)
        if limit is not None and len(results) >= limit:
            return results[:limit]
        next_link = page.get("@odata.nextLink")
        if not next_link:
            return results
        if not isinstance(next_link, str) or next_link in seen_links:
            raise ActionFailure(
                "Rejected repeated or invalid Microsoft Graph pagination URL"
            )
        seen_links.add(next_link)
    raise ActionFailure("Microsoft Graph pagination exceeded its safety limit")


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
