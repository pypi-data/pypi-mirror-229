from dataclasses import dataclass
from typing import Callable

import h5py
import numpy as np


@dataclass
class MappedDataset:
    _lazy_pyuff_dataset: h5py.Dataset
    _lazy_pyuff_map_fn: Callable[[np.ndarray], np.ndarray]

    def __getitem__(self, args, new_dtype=None):
        real = self._lazy_pyuff_dataset["real"][slice_on_read]
        imag = self._lazy_pyuff_dataset["imag"][slice_on_read]
        value = real + 1j * imag






        arr = self._lazy_pyuff_dataset.__getitem__(args, new_dtype=new_dtype)
        return self._lazy_pyuff_map_fn(arr)

    def __array__(self, dtype=None):
        arr = self._lazy_pyuff_dataset.__array__(dtype=dtype)
        return self._lazy_pyuff_map_fn(arr)

    def __getattr__(self, name):
        return getattr(self._lazy_pyuff_dataset, name)


def map_dataset(
    dataset: h5py.Dataset,
    map_fn: Callable[[np.ndarray], np.ndarray],
) -> h5py.Dataset:  # type: ignore
    return MappedDataset(dataset, map_fn)
