from vbeam.fastmath import numpy as np
from vbeam.interpolation import FastInterpLinspace
from vbeam.scan import SectorScan
from vbeam.util.arrays import grid


def resample_grid(
    image: np.ndarray,
    orignal_scan: SectorScan,
    new_scan: SectorScan,
    x_axis: int,
    z_axis: int,
):
    # The x- and z-axis of the original scan
    min_x, max_x, min_z, max_z = orignal_scan.bounds
    num_x, num_z = image.shape[x_axis], image.shape[z_axis]
    xp = FastInterpLinspace(min_x, (max_x - min_x) / num_x, num_x)
    zp = FastInterpLinspace(min_z, (max_z - min_z) / num_z, num_z)

    # The x- and z-axis must come first when using interp2d
    image = np.moveaxis(image, x_axis, 0)
    image = np.moveaxis(image, z_axis, 1)

    # The points to interpolate the image on
    points = grid(new_scan.azimuths, new_scan.depths)
    resampled_image = FastInterpLinspace.interp2d(
        points[..., 0],  # The x-coordinates of the points
        points[..., 1],  # The z-coordinates of the points
        xp,
        zp,
        image,
    )

    # Move the x- and z-axis back
    resampled_image = np.moveaxis(resampled_image, 1, z_axis)
    resampled_image = np.moveaxis(resampled_image, 0, x_axis)
    return resampled_image
