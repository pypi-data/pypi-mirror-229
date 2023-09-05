from dataclasses import dataclass
from typing import Literal

from vbeam.fastmath import numpy as np


def decibels(x: float) -> float:
    return 20 * np.log10(x)


def inverse_decibels(x: float) -> float:
    return 10 ** (x / 20)


@dataclass
class DepthGainCompensation:
    tgc_depths: np.ndarray  # Meters
    tgc_gain_values: np.ndarray

    # gain_scale tells us whether the gain values are in decibels or not
    gain_scale: Literal["linear", "decibels"] = "decibels"

    def __call__(
        self,
        data: np.ndarray,
        depths: np.ndarray,
        axis: int,
        *,
        apply_in_db: bool = False,
    ):
        gain = np.interp(depths, self.tgc_depths, self.tgc_gain_values)
        if apply_in_db and self.gain_scale == "linear":
            gain = decibels(gain)
        if not apply_in_db and self.gain_scale == "decibels":
            gain = inverse_decibels(gain)
        # Ensure gain array is broadcastable with data
        gain = np.expand_dims(
            gain, tuple(range(axis)) + tuple(range(axis + 1, data.ndim))
        )
        return data * gain

    def plot(self):
        import matplotlib.pyplot as plt

        plt.title("Depth (time) gain compensation")
        plt.plot(self.tgc_depths * 1000, self.tgc_gain_values)
        plt.xlabel("Depth [mm]")
        plt.ylabel("Gain [dB]")
