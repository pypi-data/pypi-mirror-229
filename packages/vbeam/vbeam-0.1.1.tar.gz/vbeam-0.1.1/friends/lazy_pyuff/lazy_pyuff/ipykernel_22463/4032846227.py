from dataclasses import dataclass
import numpy as np
import jax.numpy as jnp


def read(indices):
    print(indices)
    return np.arange(100)[indices]


@dataclass
class LazyArray:
    data = np.array([0, 1, 2])

    def __array__(self):
        return self.data

    def __jax_array__(self):
        return self.data

    #@property
    #def dtype(self):
    #    return self.data.dtype


larr = LazyArray()
jnp.sum(larr)