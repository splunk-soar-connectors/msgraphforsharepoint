"""SDK view for the SharePoint list inventory action."""

from soar_sdk.models.view import ViewContext

from ..actions.list_lists import ListListsOutput


def display_list_lists(
    context: ViewContext, action: str, outputs: list[ListListsOutput]
) -> dict:
    """Return list data in the shape consumed by the legacy list view."""
    return {
        "results": [
            {
                "data": [
                    output.model_dump(mode="json", by_alias=True) for output in outputs
                ]
            }
        ]
    }
