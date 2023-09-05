from functools import cached_property
from typing import Optional, Sequence

from h5py import Group


class PyuffObject:
    def __init__(self, h5py_obj: Optional[Group] = None, **kwargs):
        if h5py_obj is not None and not isinstance(h5py_obj, Group):
            raise TypeError(
                "PyuffObject may only take one positional argument: h5py_obj. All other arguments must be keyword arguments (i.e.: Wave(sound_speed=1540.0), not Wave(1540.0))."
            )
        self._h5py_obj = h5py_obj
        for key, val in kwargs.items():
            setattr(self, key, val)

    def _get_fields(self) -> Sequence[str]:
        t = type(self)
        return [
            attr
            for attr in dir(t)
            if isinstance(getattr(t, attr), (property, cached_property))
        ]

    def __repr__(self) -> str:
        field_strs = [f"{field}={getattr(self, field)}" for field in self._get_fields()]
        return self.__class__.__name__ + "(" + ", ".join(field_strs) + ")"
