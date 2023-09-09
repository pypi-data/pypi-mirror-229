__all__ = ["Input", "Observation"]

from dataclasses import dataclass

import tensorflow_probability.substrates.jax.bijectors as tfb
from beartype import beartype
from beartype.typing import List, Optional, Tuple, Union
from jaxtyping import Array, Float

from calcgp.gpjax_base import Module, param_field, static_field
from calcgp.typing import ScalarFloat, ScalarOrVector, TwoArrays

from typing import overload


@dataclass
class Input(Module):
    data: Union[TwoArrays, Float[Array, "N D"]] = static_field()
    type: Optional[str] = static_field(None)
    dims: ScalarFloat = static_field(init=False)

    @overload
    def __init__(self, 
                 data: TwoArrays, 
                 type: Optional[str]
                ) -> None:
        ...

    @overload
    def __init__(self, 
                 data: Float[Array, "N D"], 
                 type: Optional[str]
                ) -> None:
        ...

    def __init__(self, data, type) -> None:
        # TODO: doc

        if isinstance(data, Float[Array, "N D"]) and type not in ["func", "grad"]:
            raise ValueError(f"If data is a single array, type must be either 'func' or 'grad'! Given was {self.type}")

        if isinstance(data, Union[List, Tuple]) and type not in ["mix", None]:
            raise ValueError(f"If data is a two arrays, type must be either 'mix'! Given was {self.type}")

        if type in ["mix", None]:
            if data[0].shape[1] != data[1].shape[1]:
                raise ValueError(f"Both array must have the same second dimension! Got dimensions {data[0].shape[1]} and {data[1].shape[1]}.")
            
            self.dims = data[0].shape[1]
        else:
            self.dims = data.shape[1]
        
        if type is None:
            self.type = "mix"
        else:
            self.type = type

        self.data = data


@dataclass
class Observation(Module):
    # TODO: docs
    X: Input = static_field()
    Y: Float[Array, "N 1"] = static_field()
    noise: ScalarOrVector = param_field(bijector=tfb.Softplus())