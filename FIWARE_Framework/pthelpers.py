from typing import Union


def _all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _all_subclasses(c)])


def all_subclasses(cls):
    return tuple(_all_subclasses(cls))


def Subclasses(cls):
    return Union[all_subclasses(cls)]
