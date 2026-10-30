"""Pure input validation shared by actions with a result limit."""


def validate_limit(value: float | None) -> int | None:
    if value is None:
        return None
    if not float(value).is_integer():
        raise ValueError(
            "Please provide a valid integer value in the 'limit' action parameter"
        )
    limit = int(value)
    if limit < 0:
        raise ValueError(
            "Please provide a valid non-zero positive integer in the 'limit' action parameter"
        )
    if limit == 0:
        raise ValueError(
            "Please provide non-zero positive integer in 'limit' action parameter"
        )
    return limit
