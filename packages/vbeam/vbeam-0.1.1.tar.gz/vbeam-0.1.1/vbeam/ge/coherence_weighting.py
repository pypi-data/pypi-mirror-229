from vbeam.fastmath import numpy as np
from vbeam.postprocess import coherence_factor


def coherence_weighting(data: np.ndarray, gamma: float, axis: int):
    coherence = coherence_factor(data, axis)
    b_mode = np.sum(data, axis)
    return b_mode * (coherence**gamma)
