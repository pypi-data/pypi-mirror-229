from typing import Any, Mapping, TypeVar

T = TypeVar("T")

def make_mapping(obj: Any, by_alias: bool = True) -> Mapping[str, Any]:
    """Receives a gyver.attrs defined class and
    returns a mapping depth-1 of the class"""
    ...

def deserialize_mapping(
    mapping: Mapping[str, Any], by_alias: bool = True
) -> Mapping[str, Any]:
    """Recursively unwraps the mapping resolving gyver classes,
    other mappings and sequences(list, set, tuple) internally"""
    ...

def deserialize(value: Any, by_alias: bool = True) -> Mapping[str, Any]:
    """Recursively unwraps the values resolving gyver classes,
    other mappings and sequences(list, set, tuple) internally"""
    ...
