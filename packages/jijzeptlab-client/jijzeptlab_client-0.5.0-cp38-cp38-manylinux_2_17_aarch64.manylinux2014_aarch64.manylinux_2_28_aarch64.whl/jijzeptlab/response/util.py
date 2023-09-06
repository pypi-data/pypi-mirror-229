import typing as tp

from functools import singledispatch

import jijmodeling as jm

from google.protobuf.text_encoding import CUnescape

from orjson import JSONDecodeError


@singledispatch
def _recursive_deserialize(obj: tp.Any) -> tp.Any:
    """deserialize an object (jm.SampleSet and jm.Problem) recursively.
    This function traverses the object recursively and deserializes it if the instance type is serialized from jm.SampleSet or jm.Problem.
    """
    return obj


@_recursive_deserialize.register
def _(obj: str) -> tp.Any:
    deserialized = None

    # attempt to deserialize using `jm.SampleSet.from_json`
    try:
        deserialized = jm.SampleSet.from_json(obj)
        return deserialized
    except (AttributeError, TypeError, JSONDecodeError, NotImplementedError):
        pass

    # attempt to deserialize with `jm.from_protobuf (jm.Problem)` and `CUnescape`
    try:
        deserialized = jm.from_protobuf(CUnescape(obj))
        return deserialized
    except (ValueError, NotImplementedError, jm.ProtobufDeserializationError):
        pass

    return obj


@_recursive_deserialize.register
def _(obj: dict) -> tp.Any:
    return {k: _recursive_deserialize(v) for k, v in obj.items()}


# list
@_recursive_deserialize.register
def _(obj: list) -> tp.Any:
    return [_recursive_deserialize(elem) for elem in obj]


# tuple
@_recursive_deserialize.register
def _(obj: tuple) -> tp.Any:
    return tuple(_recursive_deserialize(elem) for elem in obj)
