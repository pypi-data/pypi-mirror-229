__all__ = ["LogMarginalLikelihood"]

from dataclasses import dataclass
from typing import overload

import jax.numpy as jnp
import jax.tree_util as jtu

from calcgp.gpjax_base import Module, static_field
from calcgp.gps import AbstractPosterior, Posterior, SparsePosterior
from calcgp.typing import ScalarFloat


@dataclass
class LogMarginalLikelihood(Module):
    negative: bool = static_field(False)
    constant: ScalarFloat = static_field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.constant = jnp.array(-1.0) if self.negative else jnp.array(1.0)
    
    def __call__(self, posterior: AbstractPosterior) -> ScalarFloat:
        return self.forward(posterior)

    def __hash__(self):
        return hash(tuple(jtu.tree_leaves(self)))

    @overload
    def forward(self, posterior: Posterior) -> ScalarFloat:
        ...

    @overload
    def forward(self, posterior: SparsePosterior) -> ScalarFloat:
        ...

    def forward(self, posterior):
        X = posterior.observation.X
        Y = posterior.observation.Y
        noise = posterior.observation.noise

        prior_dist = posterior.prior(X)

        log_prob = prior_dist.log_prob(Y, noise)

        return self.constant * log_prob.squeeze()