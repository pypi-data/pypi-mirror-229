from typing import Union, Tuple, List, Sequence, MutableSequence


def is_attrs_class(cls):
    return getattr(cls, "__attrs_attrs__", None) is not None


def has_args(cls):
    return getattr(cls, "__args__", None) is not None


def is_tuple(t):
    return (
            t in (Tuple, tuple) or
            (getattr(t, "__origin__", None) is tuple)
    )


def is_sequence(t):
    return (
            t in (List, list, Sequence, MutableSequence)
            or (getattr(t, "__origin__", None) is list)
    )


def is_union_type(obj):
    return (
        obj is Union or getattr(obj, "__origin__", None) is Union
    )


class StructDict:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        for key, value in self.__dict__.items():
            if isinstance(value, dict):
                self.__dict__[key] = StructDict(**value)

    def to_dict(self, str_values: bool = False):
        if str_values:
            for key, value in self.__dict__.items():
                if not isinstance(value, str):
                    self.__dict__[key] = str(value)
        return self.__dict__
