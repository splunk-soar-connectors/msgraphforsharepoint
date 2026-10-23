"""SDK view for list columns and items."""

from soar_sdk.models.view import ViewContext

from ..app import GetListOutput


def display_get_list(
    context: ViewContext, action: str, outputs: list[GetListOutput]
) -> dict:
    """Return list detail data in the shape consumed by the legacy view."""
    return {
        "results": [
            {"data": [output.model_dump(mode="json", by_alias=True) for output in outputs]}
        ]
    }
