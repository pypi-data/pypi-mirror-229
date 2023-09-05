import h5py


def read_value(h5py_obj: h5py.Group, name: str) -> float:
    return h5py_obj[name][0, 0]


def read_complex_data(data: h5py.Group, slice=()):
    real = data["real"][slice]
    imag = data["imag"][slice]
    return real + 1j * imag





from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class ComplexDataset:
    _lazy_pyuff_dataset: h5py.Group

    def __getitem__(self, args, new_dtype=None):
        real = self._lazy_pyuff_dataset["real"].__getitem__(args, new_dtype=new_dtype)
        imag = self._lazy_pyuff_dataset["imag"].__getitem__(args, new_dtype=new_dtype)
        return real + 1j * imag

    def __array__(self, dtype=None):
        real = self._lazy_pyuff_dataset["real"].__array__(dtype=dtype)
        imag = self._lazy_pyuff_dataset["imag"].__array__(dtype=dtype)
        return real + 1j * imag

    def __getattr__(self, name):
        return getattr(self._lazy_pyuff_dataset, name)