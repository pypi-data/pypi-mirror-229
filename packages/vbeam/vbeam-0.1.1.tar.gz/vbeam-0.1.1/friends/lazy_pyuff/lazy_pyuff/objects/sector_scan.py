from functools import cached_property
from typing import Sequence

import lazy_pyuff.readers.channel_data_reader as reader
import numpy as np
from lazy_pyuff.pyuff_object import PyuffObject
from lazy_pyuff.objects.wave import Wave


class SectorScan(PyuffObject):
    ...
