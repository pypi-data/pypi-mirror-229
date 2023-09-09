from typing import Any, Collection, Dict, Optional


def filter_dict(
    value: Dict[Any, Any],
    included: Optional[Collection] = None,
    excluded: Optional[Collection] = None,
):
    """
    .. usage:
        >>> filter_dict({"foo": "bar"}, included={}, excluded={"foo"})
        {}

        >>> filter_dict(
        ...     {"foo": 1, "bar": 2, "baz": 3},
        ...     included=("foo", )
        ... )
        {'foo': 1}
    """
    _exc = excluded or ()
    return dict(
        filter(
            lambda i: i[0]
            in (v for v in (included or value.keys()) if v not in _exc),
            value.items(),
        )
    )
