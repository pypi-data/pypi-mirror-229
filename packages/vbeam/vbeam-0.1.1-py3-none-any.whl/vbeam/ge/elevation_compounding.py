from dataclasses import dataclass
from typing import Sequence, Tuple

from spekk import Spec

from vbeam.beamformers.transformations.base import Transformation
from vbeam.core import WaveData
from vbeam.fastmath import numpy as np


def pairs(iterable, mode="all"):
    first = iterable[0]
    for second in iterable[1:]:
        yield (first, second)
        first = second
    if mode == "all":
        yield (first, None)


def integrate_segments(
    x: np.ndarray,
    segments_start: Sequence,
    segments_slope: Sequence,
):
    """Integrate some piecewise linear function defined by segments_start and
    segments_slope up to x.

    Example:
    >>> segments_start = [0, 1, 2]
    >>> segments_slope = [1, 0, 2]

    It starts at 0
    >>> integrate_segments(0, segments_start, segments_slope)
    0

    In the beginning it increases by 1 per x
    >>> integrate_segments(0.5, segments_start, segments_slope)
    0.5
    >>> integrate_segments(1, segments_start, segments_slope)
    1

    There's a plateau between 1 and 2 where the slope is 0
    >>> integrate_segments(2, segments_start, segments_slope)
    1

    Afterwards it increases by 2 per x
    >>> integrate_segments(3, segments_start, segments_slope)
    3
    >>> integrate_segments(4, segments_start, segments_slope)
    5
    """
    assert len(segments_start) == len(segments_slope)

    def _integrate1(x: float):
        "Integrate just for a single x (scalar value)"
        s = 0
        for i_from, i_to in pairs(range(len(segments_start))):
            if i_to is not None:
                to_x = np.min(np.array([segments_start[i_to], x]))
            else:
                to_x = x
            # Assumes segments_start is in ascending order
            length = np.max(np.array([0, to_x - segments_start[i_from]]))
            s += length * segments_slope[i_from]
        return s

    # Make it run for arbitrary arrays by vectorization
    if hasattr(x, "ndim"):
        for _ in range(x.ndim):
            _integrate1 = np.vmap(_integrate1, [0])
    return _integrate1(x)


@dataclass
class ElevationPlanesSetup:
    depth_segments: np.ndarray
    # How much the elevation (in meters) increase/decreases per depth
    elevation_increase_segments: np.ndarray

    def with_elevation_planes(self, point: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        "Take a point and return a tuple of two points with modified elevation."
        displacement = integrate_segments(
            point[..., 2],  # Integrate over depths
            self.depth_segments,
            self.elevation_increase_segments,
        )
        x, y, z = point[0], point[1], point[2]
        return (
            # Symmetrical elevation planes
            np.array([x, y - displacement, z]),
            np.array([x, y + displacement, z]),
        )

    def plot(self):
        import matplotlib.pyplot as plt

        depths = np.linspace(0, max(self.depth_segments) * 1.1, 100)
        elevation_displacement = integrate_segments(
            depths, self.depth_segments, self.elevation_increase_segments
        )
        plt.plot(depths * 1000, elevation_displacement * 1000)
        plt.plot(depths * 1000, -elevation_displacement * 1000)
        plt.plot(depths * 1000, np.zeros(depths.shape), "--", alpha=0.5)
        plt.xlabel("Depth [mm]")
        plt.ylabel("Elevation [mm]")
        plt.title("Elevation planes")
        plt.legend(["Elevation plane 1", "Elevation plane 2", "No elevation"])


@dataclass
class WithElevationPlanes(Transformation):
    elevation_planes_setup: ElevationPlanesSetup

    elevations_dimension: str = "elevations"
    point_pos_dimension: str = "point_pos"
    wave_data_dimension: str = "wave_data"

    def transform(
        self, to_be_transformed: callable, input_spec: Spec, output_spec: Spec
    ) -> callable:
        def wrapped(**kwargs):
            point_pos = kwargs[self.point_pos_dimension]
            wave_data: WaveData = kwargs[self.wave_data_dimension]
            assert point_pos.shape == (
                3,
            ), f"Can not have additional dimensions. Expected point_pos.shape to be (3,) but it is {point_pos.shape}."
            assert (
                wave_data.shape == ()
            ), f"Can not have additional dimensions. Expected wave_data.shape to be () but it is {wave_data.shape}"

            results = []
            for new_point_pos in self.elevation_planes_setup.with_elevation_planes(
                point_pos
            ):
                kwargs[self.point_pos_dimension] = new_point_pos
                results.append(to_be_transformed(**kwargs))
            return np.array(results)

        return wrapped

    def transform_input_spec(self, spec: Spec) -> Spec:
        return spec

    def transform_output_spec(self, spec: Spec) -> Spec:
        # return spec
        return spec.add_dimension(self.elevations_dimension)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
