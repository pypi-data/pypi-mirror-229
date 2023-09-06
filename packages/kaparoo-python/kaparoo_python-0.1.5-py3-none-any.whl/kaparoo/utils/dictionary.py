# -*- coding: utf-8 -*-

from __future__ import annotations

__all__ = ("add_affixes", "extract")

from typing import TYPE_CHECKING, overload

from kaparoo.utils.optional import replace_if_none, unwrap_or_default

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any, Literal


StrDict = dict[str, Any]


def add_affixes(
    dictionary: StrDict,
    prefix: str | None = None,
    suffix: str | None = None,
    delimiter: str | None = None,
    excludes: Iterable[str] | None = None,
) -> StrDict:
    """Add prefixes and suffixes to keys in a dictionary.

    Args:
        dictionary: The dictionary whose keys will be affixed.
        prefix: The prefix to add to the keys. Defaults to None.
        suffix: The suffix to add to the keys. Defaults to None.
        delimiter: The delimiter to separate keys from affixes. Defaults to None.
        excludes: Keys to be excluded from affixing. Defaults to None.

    Returns:
        A new dictionary with affixed keys.
    """

    def unwrap_str(s: str | None) -> str:
        return unwrap_or_default(s, "").strip()

    delimiter = unwrap_str(delimiter)

    if prefix := unwrap_str(prefix):
        prefix = prefix + delimiter

    if suffix := unwrap_str(suffix):
        suffix = delimiter + suffix

    excludes = set(replace_if_none(excludes, []))

    new_dict: StrDict = {}

    for key, value in dictionary.items():
        if key not in excludes:
            if prefix:
                key = prefix + key
            if suffix:
                key = key + suffix

        new_dict[key] = value

    return new_dict


@overload
def extract(
    dictionary: StrDict,
    keys: Iterable[str],
    returns_rest: Literal[False] = False,
) -> StrDict:
    ...


@overload
def extract(
    dictionary: StrDict,
    keys: Iterable[str],
    returns_rest: Literal[True],
) -> tuple[StrDict, StrDict]:
    ...


@overload
def extract(
    dictionary: StrDict,
    keys: Iterable[str],
    returns_rest: bool,
) -> StrDict | tuple[StrDict, StrDict]:
    ...


def extract(
    dictionary: StrDict,
    keys: Iterable[str],
    returns_rest: bool = False,
) -> StrDict | tuple[StrDict, StrDict]:
    """Extracts specific key-value pairs from a dictionary.

    Args:
        dictionary: The dictionary to extract.
        keys: Keys to be extracted from the dictionary.
        returns_rest: Whether to return the unextracted pairs also. Defaults to False.

    Returns:
        A dictionary of extracted pairs. If `returns_rest` is True, a dictionary of
            unextracted pairs is returned together as a tuple.
    """

    keys = set(keys)
    items = dictionary.items()
    new_dict = {k: v for k, v in items if k in keys}

    if returns_rest:
        rest_dict = {k: v for k, v in items if k not in keys}
        return new_dict, rest_dict

    return new_dict
