from typing import List, Literal, Optional, Tuple, Union

import numpy
import pyuff
from pyuff import Wavefront
from scipy.signal import hilbert
from spekk import Spec

from vbeam.apodization import (
    RTBApodization,
    Hamming,
    NoApodization,
    PlaneWaveReceiveApodization,
    PlaneWaveTransmitApodization,
    TxRxApodization,
)
from vbeam.core import ElementGeometry, WaveData
from vbeam.data_importers.setup import SignalForPointSetup
from vbeam.fastmath import numpy as np
from vbeam.interpolation import FastInterpLinspace
from vbeam.scan import Scan, linear_scan, sector_scan
from vbeam.wavefront import FocusedSphericalWavefront, PlaneWavefront, UnifiedWavefront

speed_of_sound = np.array(float(channel_data.sound_speed), dtype="float32")
t_axis_interp = FastInterpLinspace(
    min=float(channel_data.initial_time),
    d=1 / channel_data.sampling_frequency,
    n=channel_data.n_samples,
)
modulation_frequency = channel_data.modulation_frequency
receiver = ElementGeometry(
    np.array(channel_data.probe.xyz.T),
    np.array(channel_data.probe.theta),
    np.array(channel_data.probe.phi),
)
sender = ElementGeometry(np.array([0.0, 0.0, 0.0], dtype="float32"), 0.0, 0.0)
sequence: List[pyuff.Wave] = channel_data.sequence
wave_data = WaveData(
    azimuth=np.array([wave.source.azimuth for wave in sequence]),
    elevation=np.array([wave.source.elevation for wave in sequence]),
    source=np.array([wave.source.xyz for wave in sequence]),
    delay_distance=np.array([wave.delay * wave.sound_speed for wave in sequence]),
)
wave_data = wave_data[0]
apodization = NoApodization()
wavefront = FocusedSphericalWavefront()
signal = channel_data.data.T

spec = Spec(
    {
        "speed_of_sound": [],
        "t_axis_interp": [],
        "signal": ["transmits", "signal_time"],
        "modulation_frequency": [],
        "receiver": ["transmits"],
        "sender": [],
        "point_pos": ["points"],
        "wavefront": [],
        "wave_data":[],
        "apodization": [],
    }
)

setup = SignalForPointSetup(
    speed_of_sound,
    t_axis_interp,
    signal,
    modulation_frequency,
    receiver,
    sender,
    None,
    wavefront,
    wave_data,
    apodization,
    spec,
    scan,
)
