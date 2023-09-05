__all__ = ["AbstractMean", "ConstantMean", "CombinationMean", "SumMean", "ProductMean", "mean_f", "mean_g"]

from abc import abstractmethod
from dataclasses import dataclass
from functools import partial

import jax.numpy as jnp
from beartype.typing import Callable, List, Union
from jax import jacrev, vmap
from jaxtyping import Array, Float

from calcgp.containers import Input
from calcgp.gpjax_base import Module, param_field, static_field
from calcgp.typing import ScalarFloat


@dataclass
class AbstractMean(Module):

    @abstractmethod
    def __call__(self, x: Float[Array, "D"]) -> ScalarFloat:
        '''General mean.

        Parameters
        ----------
        x : Float[Array, "D"]
            Input corresponding to a function evaluation.

        Returns
        -------
        Float[Array, "D"]
            Mean evaluated at the input.
        '''
        raise NotImplementedError
    
    def grad(self, x: Float[Array, "D"]) -> Float[Array, "D"]:
        '''Gradient of the mean.

        Parameters
        ----------
        x : Float[Array, "D"]
            Input corresponding to a gradient evaluation.

        Returns
        -------
        Float[Array, "D"]
            Gradient of the mean evaluated at the input.
        '''
        return jacrev(self, argnums=0)(x)
    
    def __add__(self, other: Union["AbstractMean", ScalarFloat]) -> "AbstractMean":
        '''add two kernels together

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be added to this kernel

        Returns
        -------
        Kernel
            A new Kernel representing the sum of two kernels
        '''
        if isinstance(other, AbstractMean):
            return SumMean(kernels=[self, other])
        else:
            return SumMean(kernels=[self, ConstantMean(other)])

    def __radd__(self, other: Union["AbstractMean", ScalarFloat]) -> "AbstractMean":
        '''add two kernels together

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be added to this kernel

        Returns
        -------
        Kernel
            A new Kernel representing the sum of two kernels
        '''
        return self.__add__(other)
    
    def __mul__(self, other: Union["AbstractMean", ScalarFloat]) -> "AbstractMean":
        '''multiply two kernels together

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be multiplied to this kernel

        Returns
        -------
        Kernel
            A new Kernel representing the product of two kernels
        '''
        if isinstance(other, AbstractMean):
            return ProductMean(kernels=[self, other])
        else:
            return ProductMean(kernels=[self, ConstantMean(other)])

    def __rmul__(self, other: Union["AbstractMean", ScalarFloat]) -> "AbstractMean":
        '''multiply two kernels together

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be multiplied to this kernel

        Returns
        -------
        Kernel
            A new Kernel representing the product of two kernels
        '''
        return self.__mul__(other)
    
    def mean_vector(self, X: Input) -> Float[Array, "N 1"]:
        if X.type == "func":
            return mean_f(self, X.data)
        if X.type == "grad":
            return mean_g(self, X.data)
        if X.type == "mix":
            m_f = mean_f(self, X.data[0])
            m_g = mean_g(self, X.data[1])
            return jnp.vstack((m_f, m_g))


@dataclass
class ConstantMean(AbstractMean):
    '''A constant mean that returns the same value for each input. The parameter cannot be trained.
    '''
    constant: ScalarFloat = param_field(jnp.array(0.0))

    def __call__(self, x: Float[Array, "D"]) -> ScalarFloat:
        '''Constant mean.

        Parameters
        ----------
        x : Float[Array, "D"]
            Input corresponding to a function evaluation.

        Returns
        -------
        Float[Array, "D"]
            Mean evaluated at the input.
        '''
        return self.constant
    

@dataclass  
class CombinationMean(AbstractMean):
    '''A wrapper that supplies the combination of multiple kernels
    '''
    means: List[AbstractMean]
    operator: Callable = static_field()

    def __call__(self, X: Float[Array, "N D"]) -> Float[Array, "N 1"]:
        '''Mean of function evaluations at X according to the combination of means.

        Parameters
        ----------
        X : Float[Array, "N D"]
            Input corresponding to a function evaluation

        Returns
        -------
        Float[Array, "N 1"]
            Function Mean evaluated at the inputs
        '''
        return self.operator(jnp.stack([m(X) for m in self.means]))


SumMean = partial(CombinationMean, operator=partial(jnp.sum, axis=0))
ProductMean = partial(CombinationMean, operator=partial(jnp.prod, axis=0))


    
def mean_f(kernel, X: Float[Array, "N D"]) -> Float[Array, "N 1"]:
    '''Mean vector for function evaluations.

    Parameters
    ----------
    x : Float[Array, "N D"]
        Input corresponding to function evaluations.

    Returns
    -------
    Float[Array, "N 1"]
        Function mean vector evaluated at the inputs.
    '''
    return vmap(kernel)(X).reshape(-1,1)

def mean_g(kernel, X: Float[Array, "N D"]) -> Float[Array, "N D"]:
    '''Mean vector for gradient evaluations.

    Parameters
    ----------
    x : Float[Array, "N D"]
        Input corresponding to gradient evaluations.

    Returns
    -------
    Float[Array, "N D"]
        Gradient mean vector evaluated at the inputs.
    '''
    return vmap(kernel.grad)(X).reshape(-1,1)