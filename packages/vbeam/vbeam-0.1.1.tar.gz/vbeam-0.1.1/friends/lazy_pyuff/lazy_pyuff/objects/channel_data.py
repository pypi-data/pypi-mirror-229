from functools import cached_property
from typing import Sequence

import lazy_pyuff.readers.channel_data_reader as reader
import numpy as np
from lazy_pyuff.objects.wave import Wave
from lazy_pyuff.pyuff_object import PyuffObject
from lazy_pyuff.readers.common import read_value


class ChannelData(PyuffObject):
    @cached_property
    def data(self) -> np.ndarray:
        return reader.read_data(self._h5py_obj)

    @cached_property
    def sequence(self) -> Sequence[Wave]:
        return reader.read_sequence(self._h5py_obj)

    @cached_property
    def sound_speed(self) -> float:
        return read_value(self._h5py_obj, "sound_speed")

    @cached_property
    def initial_time(self) -> float:
        return read_value(self._h5py_obj, "initial_time")

    @cached_property
    def sampling_frequency(self) -> float:
        return read_value(self._h5py_obj, "sampling_frequency")

    #### Dependent properties

    @cached_property
    def n_samples(self) -> int:
        print(self.data)
        return self.data.shape[0]
