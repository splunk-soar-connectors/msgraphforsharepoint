"""SDK action boundary for the SharePoint list_lists action."""

import httpx
from soar_sdk.params import Params, Param
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
from ._limits import validate_limit
from ..asset import Asset


class ListListsSummary(ActionOutput):
    lists_count: int = OutputField(example_values=[1])


class ListListsParams(Params):
    limit: float | None = Param(description="Maximum number of sites to return")


class UserOutput(ActionOutput):
    displayName: str = OutputField(example_values=["Test User"])
    email: str = OutputField(
        cef_types=["email"], example_values=["test_user@tenant-name.ontest.com"]
    )
    id: str = OutputField(example_values=["eeb3645f-df19-47a1-8e8c-fcd234cb5f6f"])


class CreatedbyOutput(ActionOutput):
    user: UserOutput


class LastmodifiedbyOutput(ActionOutput):
    user: UserOutput


class ListOutput(ActionOutput):
    contentTypesEnabled: bool
    hidden: bool
    template: str = OutputField(example_values=["genericList"])


class ParentreferenceOutput(ActionOutput):
    siteId: str = OutputField(
        example_values=[
            "tenant-name.sharepoint.com,dc6f43e9-54fa-4a39-8783-314e3bbbed41,c42b48c4-59b9-48f1-b96e-e8145b5539fa"
        ]
    )


class ListListsOutput(ActionOutput):
    etag: str = OutputField(alias="@odata.etag")
    createdBy: CreatedbyOutput
    createdDateTime: str = OutputField(example_values=["2022-02-24T05:38:53Z"])
    description: str = OutputField(example_values=["Test List Description"])
    displayName: str = OutputField(
        cef_types=["sharepoint list name"], example_values=["ListName"]
    )
    eTag: str = OutputField(example_values=['"4896b66a-659c-4fce-a148-0b26bd718f68,5"'])
    id: str = OutputField(
        cef_types=["sharepoint list id"],
        example_values=["4896b66a-659c-4fce-a148-0b26bd718f68"],
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
