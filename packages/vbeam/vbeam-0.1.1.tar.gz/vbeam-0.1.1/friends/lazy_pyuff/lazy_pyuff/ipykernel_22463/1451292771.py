import jax
import jax.numpy as jnp

from vbeam.beamformers import *
from vbeam.postprocess import *
from vbeam.scan import cartesian_map

beamformer = compose(
    specced_signal_for_point,
    ForAll("points"),
    ForAll("transmits"),
    Apply(jnp.sum, Axis("transmits")),
    Apply(setup.scan.unflatten),
    Apply(normalized_decibels),
    Apply(cartesian_map, setup.scan),
    Wrap(jax.jit),
).build(spec)
result = beamformer(**setup.data)
None