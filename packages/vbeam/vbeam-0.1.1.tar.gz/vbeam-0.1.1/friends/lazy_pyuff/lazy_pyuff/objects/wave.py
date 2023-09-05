from functools import cached_property

import lazy_pyuff.readers.wave_reader as reader
from lazy_pyuff.pyuff_object import PyuffObject


class Wave(PyuffObject):
    @cached_property
    def sound_speed(self) -> float:
        return reader.read_sound_speed(self._h5py_obj)
