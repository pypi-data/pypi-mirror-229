__all__ = ["inner_map", "matmul_diag"]

from functools import partial

import jax.scipy as jsp
from jax import vmap
from jaxtyping import Array, Float


@partial(vmap, in_axes=(None, 1))
def inner_map(triangular: Float[Array, "N N"], rhs: Float[Array, "N M"], lower: bool=True) -> Float[Array, "M"]:
    # TODO: docs
    sol = jsp.linalg.solve_triangular(triangular, rhs, lower=lower)
    return sol.T@sol

@partial(vmap, in_axes=(0,0))
def matmul_diag(diagonal: Float[Array, "N"], rhs: Float[Array, "N M"]) -> Float[Array, "N M"]:
    '''Faster matrix multiplication for a diagonal matrix. 

    Parameters
    ----------
    diagonal : ndarray
        shape (N,). A diagonal matrix represented by a 1d vector
    rhs : ndarray
        shape (N, M). A generic matrix to be multiplied with a diagonal matrix from the left

    Returns
    -------
    ndarray
        shape (N, M). Product matrix
    '''
    return diagonal*rhs