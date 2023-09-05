from dataclasses import dataclass
from typing import Optional, Tuple

from scipy.signal import firwin
from vbeam_extras.signal_processing import filtfilt

from vbeam.fastmath import numpy as np


@dataclass
class DepthDependentFilterer:
    modulation_depths: np.ndarray
    # A tuple of different depth-dependent frequency bands
    modulation_values: Tuple[np.ndarray, ...]
    lowpass_coefficients: np.ndarray

    def __call__(self, data: np.ndarray, depths: np.ndarray, axis: int):
        all_filtered_bands = []
        # Filter the data for each modulation setup in modulation_values
        for modulation in self.modulation_values:
            # Get the modulation values for each depth
            modulation = np.interp(depths, self.modulation_depths, modulation)
            modulation = np.exp(-1j * np.pi * np.cumsum(modulation))
            # Ensure modulation is broadcastable
            modulation = np.expand_dims(
                modulation, (*range(axis), *range(axis + 1, data.ndim))
            )

            modulated_data = data * modulation  # Down-mix
            filtered_data = filtfilt(modulated_data, self.lowpass_coefficients, axis)
            demodulated_data = filtered_data / modulation  # Up-mix
            all_filtered_bands.append(demodulated_data)
        # Return the filtered data as a stacked array
        return np.stack(all_filtered_bands, axis)

    def plot_frequencies(self, depths: np.ndarray):
        import matplotlib.pyplot as plt

        Fs = 1540 / (depths[1] - depths[0])
        fig, ax = plt.subplots(figsize=(5, 3))
        for modulation in self.modulation_values:
            modulation = np.interp(depths, self.modulation_depths, modulation) * Fs / 2
            ax.plot(depths * 1000, modulation)
        ax.set_title("Filtering bands")
        ax.legend([f"Band {i+1}" for i in range(len(self.modulation_values))])
        ax.set_xlabel("Depth [mm]")
        ax.set_ylabel("Frequency [Hz]")
        fig.tight_layout()

    def plot_spectrograms(
        self,
        depths: np.ndarray,
        data: Optional[np.ndarray] = None,
        axis: Optional[int] = None,
    ):
        import matplotlib.pyplot as plt

        if data is None:
            from numpy import random

            data = random.uniform(-1, 1, depths.shape) + 1j * random.uniform(
                -1, 1, depths.shape
            )
            axis = 0

        filtered_data = self(data, depths, axis)

        s = int(depths.size / 10)
        Fs = 1540 / (depths[1] - depths[0])

        def specgram(ax, *args, **kwargs):
            xextent = (depths[0] * 1000, depths[-1] * 1000)
            ax.specgram(*args, NFFT=s, noverlap=s - 1, xextent=xextent, Fs=Fs, **kwargs)

        ncols = 1 + len(self.modulation_values)
        fig, ax = plt.subplots(ncols=ncols, figsize=(4 * ncols, 3))
        specgram(ax[0], data)
        ax[0].set_title("Spectogram of data")

        frequencies = [
            np.interp(depths, self.modulation_depths, modulation)
            for modulation in self.modulation_values
        ]
        for i in range(len(self.modulation_values)):
            specgram(ax[i + 1], filtered_data[i])
            ax[i + 1].plot(depths * 1000, frequencies[i] * Fs / 2, c="red")
            ax[i + 1].set_title(f"Filtered data: band {i+1}")
        for a in ax:
            a.set_xlabel("Depth [mm]")
            a.set_ylabel("Frequency [Hz]")
        fig.tight_layout()


def lowpass_coefficients(
    sampling_frequency: float,
    cutoff_frequency: float,
    filter_length: int,
) -> np.ndarray:
    nyquist_frequency = sampling_frequency / 2
    normalized_cutoff = cutoff_frequency / nyquist_frequency
    return np.array(firwin(filter_length, normalized_cutoff))
