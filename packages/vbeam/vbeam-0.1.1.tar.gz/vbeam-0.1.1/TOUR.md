# A tour of vbeam
Hello and welcome to a tour of vbeam — a starting point for how to read the repository. This document refers to the library as it is at the time of writing. Future plans for vbeam are described in another document.

There are code under:

- `vbeam/` — the main library
- `tests/` — tests for the library
- `docs/` — documentation/examples of how to use the library
- `friends/` — some experimental related projects

## `vbeam/`
This section gives an overview over all the modules found under vbeam.


### vbeam core and implementations
vbeam is built around a functional core found under `vbeam/core`. The most important function is `vbeam.core.kernels.signal_for_point` which has the logic to beamform a single pixel for a receiver. A beamformer is built by repeating this kernel function for all points _(pixels)_, receivers _(receiving elements)_, and transmits _(transmitted waves)_.

Some of the arguments to `signal_for_point` are sub-classed from abstract classes/interfaces. This includes `SpeedOfSound`,`InterpolationSpace1D`, `Wavefront`, and `Apodization`. These abstract classes can be found under `vbeam.core.speed_of_sound`, `vbeam.core.interpolation`, `vbeam.core.wavefront`, and `vbeam.core.apodization`, respectively. Additionally, there are a few data containers: `vbeam.core.element_geometry.ElementGeometry`, `vbeam.core.wave_data.WaveData`, and `vbeam.core.kernel_data.KernelData`.

Together these make up the beamforming core of vbeam. You'll find implementations of these abstract classes under the corresponding modules/folders: `vbeam/apodization`, `vbeam/interpolation`, `vbeam/speed_of_sound`, and `vbeam/wavefront`.


### Scans
Second to vbeam core, the `Scan` object is most important. vbeam core is completely agnostic to what points to image, so we have scans that define the grid, found under `vbeam/scan`. Two types of scans currently exists: `LinearScan` for cartesian coordinate grids and `SectorScan` for polar coordinate/beam-space grids.

Additionally, there are `vbeam/scan/advanced` which are more advanced scans (put in its own module so that the main scan classes is simpler to read). These typically include scans that does additional adaptive processing of the grid of points. For example, the `ApodizationFilteredScan` filters out any points not included in the final image, given the apodization values. These are used to speed up the beamforming process by not wasting computation on points that are zeroed out.

By default, all points are flattened to a P-by-3 array, where P is the number of points and 3 represent the xyz-components (always in cartesian coordinates). Use `scan.unflatten` after beamforming to convert the points back to the original scan shape.


### Spec
When working with beamforming algorithms we always have to keep track of the dimensions of the data, which can be a pain. [Another open-source library called spekk](https://bitbucket.org/ntnuultrasoundgroup/spekk/src/main/) was created to make it easier.

In short, spekk provides a class called `Spec` which is used to keep track of named dimensions shared across multiple arrays. For example, we may know that the second axis of the raw channel data array correspond to the receiving elements, and that each receiving element has a position stored in another array. These axes should be processed together, even though they are separate arrays, because they are the same dimension.


### Beamformers
A beamformer _(which is just a function in vbeam)_ is constructed by transforming the `signal_for_point` kernel function from `vbeam.core`. This is done by writing a domain specific language (DSL) found under `vbeam.beamformers.transformations`. The most important parts of the DSL are:

- `compose`: used for simply composing/chaining functions together in a readable way.
- `ForAll`: transforms the function such that it runs in parallel over the specified dimension.
- `Reduce`: transforms the function such that it is used to iteratively (i.e.: not in parallel) reduce over a given axis. Useful when for example summing over a dimension while using as little memory as possible.
- `Apply`: transforms the function such that a given function is applied to the result.
- `Wrap`: simply wraps the function with another higher-order function.
- `Axis`: a way of referencing axes by the name of the dimension. It may also tell vbeam what happens to the dimension — is it removed from the result, does it remain, or does it become something else?
- `Specced`: wraps a kernel function and lets vbeam know what it expects as an input-spec and what it returns as an output-spec. `specced_signal_for_point` is an example of this.

A basic beamformer may look like this:

```python
beamformer = compose(
    specced_signal_for_point,
    ForAll("points"),
    ForAll("receivers"),
    ForAll("transmits"),
    Apply(np.sum, [Axis("receivers"), Axis("transmits")]),
    Apply(scan.unflatten, Axis("points", becomes=["width", "height"])),
    Wrap(jax.jit),
).build(spec)  # <- Let vbeam know the dimensions of the input arguments
```

By using this DSL, vbeam will keep track of the dimensions for you, in addition to getting cleaner/more readable code. 

`vbeam.beamformers.base.get_beamformer` returns a very basic beamformer given some imported data. At the current version of vbeam, users are expected to write their own beamformers like the one above, but this will be improved in the near future.


### Data importers
The idea is that vbeam does not have its own data-format but is able to import and beamform data from multiple external formats. Currently only USTB UFF files may be imported. More data importers may be included in the future. Anything related to the cSound data-format will not be included in vbeam.

The code for importing UFF data is found in `vbeam.data_importers.pyuff_importer.import_pyuff`. It returns a `SignalForPointSetup` object which is a container of the arguments needed for the `vbeam.core.signal_for_point` kernel function. `SignalForPointSetup` also has some utility functions for slicing into a specific dimension (as specified by an imported `Spec` object), calculating the apodization values (for visualization purposes), and more.


### Fastmath
`vbeam/fastmath` contains an interface and a proxy-object that act as a wrapper for array-processing backends. This lets us support multiple different backends in vbeam. Currently only Numpy and JAX are supported, but implementations for PyTorch and Tensorflow are planned. Fastmath protects vbeam from library lock-in — perhaps there is a library that is faster/better than JAX in the future?

`vbeam/fastmath/included_backends` contains the implemented backends. The `vbeam.fastmath` module _(`vbeam/fastmath/__init__.py`)_ contains an proxy object called `numpy` that can be imported. Anytime a function is looked up it will forward the call to the currently active backend. The active backend can be set by setting `backend_manager.active_backend = "jax"`, where `backend_manager` can also be found in the `vbeam.fastmath` module.

Users of vbeam are not expected to use `vbeam.fastmath.numpy` in their own custom classes — it is only for internal use. Users should ideally use vbeam _as if_ it was written specifically for the selected backend.

Lastly, there is the `vbeam.fastmath.traceable` module which contains functions that enable the different backends to understand how to process the custom classes in vbeam. For example, by decorating a class with `@traceable_dataclass(data_fields=("foo", "bar"))` we let the backends know that the class has two fields called `foo` and `bar`.


### Postprocess
Postprocess contains some functions that didn't fit anywhere else, and that is typically applied to beamformed data. It contains the following functions:

- `coherence_factor`: coherence factor :)
- `normalized_decibels`: converts values to decibels and subtracts the maximum
- `upsample_by_interpolation`: IQ-interpolation/upsampling


### Preprocess
Preprocess contains some functions that is applied to the **_arguments_** before beamforming. It contains the following functions:

- `with_new_speed_of_sound`: used when beamforming with a different value of speed of sound on receive than on transmit (i.e.: assumed 1540 m/s on transmit, but use 1580 m/s on receive). It updates the virtual source position and the grid such that points doesn't move around when changing the speed of sound.
- `revert_time_gain_compensation`: reverts time gain compensation (TGC).

### Utilities
Utility function and classes:
#### `vbeam.util.download`
Function for downloading and caching files from the internet.

#### `vbeam.util.geometry`
Some helper classes for working with geometry, including `Line`, `Circle`, and `Ellipse`.

#### `vbeam.util.rfiq`
Code for converting RF- to IQ-data and vice-versa. This module is kind of buggy/unfinished but planned for the future.

#### `vbeam.util.apply_windowed`
Helper function for constructing windowed functions; functions that apply a kernel to a small window of an image. If the kernel is a linear transformation then it is very similar to a convolution. However, it supports arbitrary kernels. For example, to create an erosion function, one would simply write:

```python
erode_3x3 = windowed(np.min, (1, 1))

# Apply it to some image
eroded_image = erode_3x3(image)
```

`erode_3x3 = windowed(np.min, (1, 1))` and `dilate_3x3 = windowed(np.max, (1, 1))` are included in the module by default.

#### `vbeam.util.arrays`
Helper functions for constructing bigger arrays, like when constructing grids.

#### `vbeam.util.coordinate_systems`
Helper functions for converting between cartesian and polar coordinates.



### Experimental modules
Experimental stuff — things that I'm not sure will be included in vbeam and may be deleted at any point — is included under `vbeam/experimental`. At the time of writing it contains some previous iterations on the beamformer DSL, and an experimental REFoCUS `Wavefront` implementation.



## `friends/`
A collection of (experimental) projects that depend on vbeam and that may some day be moved to their own repositories. Contains:

- `lazy_pyuff`: an attempt to rewrite [the pyUFF library](https://bitbucket.org/ntnuultrasoundgroup/pyuff). This was eventually moved to [this public GitHub repository](https://github.com/magnusdk/pyuff). it is the UFF data structure from USTB, implemented in Python. There is nothing here that does not already exist publically in USTB.
- `raxterize`: an experimental module for rasterization in JAX. Its usecase was supposed to be for scan-conversion for arbitrary scan setups in vbeam.
- `vbeam_augment`: a project for performing data augmentations for machine learning on beamformed images.


## `tests/`
Self explanatory. Nothing special here.



## `docs/`
Contains documentation, examples, and a blog(post). The examples are from before I started wokring with GE. It could be useful to look through all the notebooks.
