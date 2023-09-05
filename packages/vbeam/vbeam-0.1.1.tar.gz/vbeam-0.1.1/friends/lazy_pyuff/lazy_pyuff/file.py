from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Union

import h5py


def nested_get(obj: Mapping, *path):
    for k in path:
        obj = obj[k]
    return obj


@dataclass
class File:
    filepath: str
    path: tuple = ()

    def __getitem__(self, name: str) -> Union["File", h5py.Group, h5py.Dataset]:
        new_path = self.path + (name,)
        with h5py.File(self.filepath, "r") as obj:
            obj = nested_get(obj, *new_path)
        return (
            File(self.filepath, new_path)
            if isinstance(obj, h5py.Group)
            else obj
        )

    def keys(self) -> Sequence[str]:
        return self.__getattr__("keys")()

    def __getattr__(self, name: str) -> Any:
        with h5py.File(self.filepath, "r") as obj:
            obj = nested_get(obj, *self.path)
            return getattr(obj, name)
