from dataclasses import dataclass
from typing import Callable

import h5py
import numpy as np


@dataclass
class MappedDataset:
    _lazy_pyuff_dataset: h5py.Dataset
    _lazy_pyuff_map_fn: Callable[[np.ndarray], np.ndarray]

    def __getitem__(self, args, new_dtype=None):
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


def fix_data_slice(data_slice, ndim: int):
    """Return the data-slice to be used when reading from disk and the data-slice after
    accounting for a (potentially) missing frames dimension.

    The API assumes the shape (frames, transmits, receivers, signal_time), but if there
    is only 1 frame then it may be missing the first dimension. This function fixes
    the data slice to account for this, making it transparent to the user.
    """
    assert ndim in (3, 4)
    if ndim == 4:
        return data_slice, ()
    elif ndim == 3:
        if isinstance(data_slice, tuple):
            return data_slice[1:], data_slice[0] if len(data_slice) > 0 else ()
        else:
            return (), data_slice


@dataclass
class LazyDataset:
    _lazy_pyuff_dataset: h5py.Dataset

    def __getitem__(self, args, new_dtype=None):
        ndim = self._lazy_pyuff_dataset.ndim
        slice_on_read, slice_after_expand = fix_data_slice(args, ndim)
        value = self._lazy_pyuff_dataset.__getitem__(slice_on_read, new_dtype=new_dtype)

        if ndim == 3:
            # Add a frames dimension
            value = np.expand_dims(value, 0)
        return value[slice_after_expand]

    def __array__(self, dtype=None):
        value = self._lazy_pyuff_dataset.__array__(dtype=dtype)
        if value.ndim == 3:
            # Add a frames dimension
            value = np.expand_dims(value, 0)
        return value

    def __getattr__(self, name):
        return getattr(self._lazy_pyuff_dataset, name)


@dataclass
class LazyDatasetComplexArray:
    _lazy_pyuff_dataset: h5py.HLObject

    def __getitem__(self, args, new_dtype=None):
        real = self._lazy_pyuff_dataset["real"]
        imag = self._lazy_pyuff_dataset["imag"]
        ndim = real.ndim

        slice_on_read, slice_after_expand = fix_data_slice(args, ndim)
        real = real.__getitem__(slice_on_read, new_dtype=new_dtype)
        imag = imag.__getitem__(slice_on_read, new_dtype=new_dtype)
        value = real + 1j * imag

        if ndim == 3:
            # Add a frames dimension
            value = np.expand_dims(value, 0)
        return value[slice_after_expand]

    def __array__(self, dtype=None):
        real = self._lazy_pyuff_dataset["real"].__array__(dtype=dtype)
        imag = self._lazy_pyuff_dataset["imag"].__array__(dtype=dtype)
        value = real + 1j * imag
        if real.ndim == 3:
            # Add a frames dimension
            value = np.expand_dims(value, 0)
        return value

    def __getattr__(self, name):
        return getattr(self._lazy_pyuff_dataset, name)
