"""Utility definitions"""

import re
from typing import Any, NamedTuple, NewType

PluginName = NewType("PluginName", str)
PluginGroup = NewType("PluginGroup", str)


class PluginID(NamedTuple):
    """Normalized name"""

    name: PluginName
    group: PluginGroup


_canonicalize_regex = re.compile(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))")


def canonicalize_name(name: str) -> PluginID:
    """Extracts the plugin identifier from an input string

    Args:
        name: The string to parse

    Returns:
        The plugin identifier
    """

    sub = re.sub(_canonicalize_regex, r" \1", name)
    values = sub.split(" ")
    result = "".join(values[:-1])
    return PluginID(PluginName(result.lower()), PluginGroup(values[-1].lower()))


def canonicalize_type(input_type: type[Any]) -> PluginID:
    """Extracts the plugin identifier from a type

    Args:
        input_type: The input type to resolve

    Raises:
        ValueError: When the class name is incorrect

    Returns:
        The plugin identifier
    """
    return canonicalize_name(input_type.__name__)
