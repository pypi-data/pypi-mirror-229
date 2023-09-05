__all__ = ["AbstractKernel", "ConstantKernel", "CombinationKernel", "SumKernel", "ProductKernel"]

from abc import abstractmethod
from dataclasses import dataclass
from functools import partial

import jax.numpy as jnp
from beartype.typing import Callable, List, Union
from jax import jacfwd, jacrev
from jaxtyping import Array, Float

from calcgp.containers import Input
from calcgp.gpjax_base import Module, param_field, static_field
from calcgp.kernels.compute import (
    covariance_diagonal_computation,
    covariance_matrix_computation
)
from calcgp.typing import ScalarFloat


@dataclass
class AbstractKernel(Module):
    '''Kernel base-class. Defines the needed derivatives of a kernel based 
    on the eval method. In each derived class the eval method must be overwritten.
    '''

    @abstractmethod
    def __call__(self, x1: Float[Array, "D"], x2: Float[Array, "D"]) -> ScalarFloat:
        '''General kernel.

        Parameters
        ----------
        x1 : Float[Array, "D"]
            Left hand input corresponding to a function evaluation.
        x2 : Float[Array, "D"]
            Right hand input corresponding to a function evaluation.

        Returns
        -------
        ScalarFloat
            Kernel evaluated at the inputs.
        '''
    
    def grad(self, x1: Float[Array, "D"], x2: Float[Array, "D"]) -> Float[Array, "D"]:
        '''"Gradient" of the kernel w.r.t. x2.

        Parameters
        ----------
        x1 : Float[Array, "D"]
            Left hand input corresponding to a function evaluation.
        x2 : Float[Array, "D"]
            Right hand input corresponding to a gradient evaluation.

        Returns
        -------
        Float[Array, "D"]
            "Gradient" of the kernel w.r.t the right hand argument evaluated at the inputs.
        '''
        return jacrev(self, argnums=1)(x1, x2)
    
    def hess(self, x1: Float[Array, "D"], x2: Float[Array, "D"]) -> Float[Array, "DD"]:
        '''"Hessian" of the kernel.

        Parameters
        ----------
        x1 : Float[Array, "D"]
            Left hand input corresponding to a gradient evaluation.
        x2 : Float[Array, "D"]
            Right hand input corresponding to a gradient evaluation.

        Returns
        -------
        Float[Array, "DD"]
            "Hessian" of the kernel evaluated at the inputs (only the true hessian if x1 == x2).
        '''
        return jacfwd(jacrev(self, argnums=1), argnums=0)(x1, x2)

    def __add__(self, other: Union["AbstractKernel", ScalarFloat]) -> "AbstractKernel":
        '''Sum of two kernels.

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be added to this kernel.

        Returns
        -------
        Kernel
            A new Kernel representing the sum of two kernels.
        '''
        if isinstance(other, AbstractKernel):
            return SumKernel(kernels=[self, other])
        else:
            return SumKernel(kernels=[self, ConstantKernel(other)])

    def __radd__(self, other: Union["AbstractKernel", ScalarFloat]) -> "AbstractKernel":
        '''Sum of two kernels.

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be added to this kernel.

        Returns
        -------
        Kernel
            A new Kernel representing the sum of two kernels.
        '''
        return self.__add__(other)
    
    def __mul__(self, other: Union["AbstractKernel", ScalarFloat]) -> "AbstractKernel":
        '''Product of two kernels.

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be multiplied to this kernel.

        Returns
        -------
        Kernel
            A new Kernel representing the product of two kernels.
        '''
        if isinstance(other, AbstractKernel):
            return ProductKernel(kernels=[self, other])
        else:
            return ProductKernel(kernels=[self, ConstantKernel(other)])

    def __rmul__(self, other: Union["AbstractKernel", ScalarFloat]) -> "AbstractKernel":
        '''Product of two kernels.

        Parameters
        ----------
        other : Union[AbstractKernel, ScalarFloat]
            The kernel or scalar to be multiplied to this kernel.

        Returns
        -------
        Kernel
            A new Kernel representing the product of two kernels.
        '''
        return self.__mul__(other)

    def gram_matrix(self, X: Input) -> Float[Array, "N M"]:
        '''Gram matrix between the elements of an array.

        Parameters
        ----------
        X : Input
            The inputs from which to construct the gram matrix.

        Returns
        -------
        Kernel
            The gram matrix constructed from the inputs.
        '''
        return self.covariance_matrix(X, X)

    def gram_diagonal(self, X: Input) -> Float[Array, "N"]:
        '''Diagonal of the gram matrix between the elements of an array.

        Parameters
        ----------
        X : Input
            The inputs from which to construct the gram matrix diagonal.

        Returns
        -------
        Kernel
            The diagonal of the gram matrix constructed from the inputs.
        '''
        return covariance_diagonal_computation(self, X)

    def covariance_matrix(self, X1: Input, X2: Input) -> Float[Array, "N M"]:
        '''Covariance matrix between the elements of two arrays.

        Parameters
        ----------
        X1 : Input
            First array from which to construct the covariance matrix.
        X2 : Input
            Second array from which to construct the covariance matrix.

        Returns
        -------
        Kernel
            The covariance matrix constructed from the inputs.
        '''
        return covariance_matrix_computation(self, X1, X2)


@dataclass  
class ConstantKernel(AbstractKernel):
    '''A constant kernel.
    '''
    constant: ScalarFloat = param_field()

    def __call__(self, x1: Float[Array, "D"], x2: Float[Array, "D"]) -> ScalarFloat:
        '''Covariance between two function evaluations at x1 and x2 according to the combination of kernels.

        Parameters
        ----------
        x1 : Float[Array, "D"]
            Left hand input corresponding to a function evaluation.
        x2 : Float[Array, "D"]
            Right hand input corresponding to a gradient evaluation.

        Returns
        -------
        ScalarFloat
            Kernel evaluated at the inputs.
        '''
        return self.constant

@dataclass  
class CombinationKernel(AbstractKernel):
    '''A wrapper that supports the combination of multiple kernels.
    '''
    kernels: List[AbstractKernel]
    operator: Callable = static_field()

    def __call__(self, x1: Float[Array, "D"], x2: Float[Array, "D"]) -> ScalarFloat:
        '''Covariance between two function evaluations at x1 and x2 according to the combination of kernels.

        Parameters
        ----------
        x1 : Float[Array, "D"]
            Left hand input corresponding to a function evaluation.
        x2 : Float[Array, "D"]
            Right hand input corresponding to a gradient evaluation.

        Returns
        -------
        ScalarFloat
            Kernel evaluated at the inputs.
        '''
        return self.operator(jnp.array([k(x1, x2) for k in self.kernels]))


SumKernel = partial(CombinationKernel, operator=jnp.sum)
ProductKernel = partial(CombinationKernel, operator=jnp.prod)