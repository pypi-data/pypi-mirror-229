__all__ = ["AbstractPrior", "Prior", "SparsePrior", "AbstractPosterior", "Posterior", "SparsePosterior", "InducingSet", "sparsify"]

from abc import abstractmethod
from dataclasses import dataclass
from typing import overload

import jax.numpy as jnp
import jax.scipy as jsp
import tensorflow_probability.substrates.jax.bijectors as tfb
from beartype.typing import Tuple
from jax import vmap
from jaxtyping import Array, Float

from calcgp.containers import Input, Observation
from calcgp.distributions import (
    AbstractMultivariateNormal,
    MultivariateNormal, 
    SparseMultivariateNormal
)
from calcgp.gpjax_base import Module, param_field, static_field
from calcgp.kernels.base import AbstractKernel
from calcgp.mean_functions import AbstractMean
from calcgp.typing import ScalarFloat
from calcgp.utils import inner_map, matmul_diag

# -------------------------------------------------------------------
# Priors

@dataclass
class AbstractPrior(Module):
    mean: AbstractMean
    covariance: AbstractKernel
    jitter: ScalarFloat = static_field(default=1e-6)

    def __call__(self, test_inputs: Input) -> AbstractMultivariateNormal:
        return self.forward(test_inputs)

    @abstractmethod
    def forward(self, test_inputs: Input) -> AbstractMultivariateNormal:
        '''Returns a Multivariate normal distribution over the given inputs.

        Parameters
        ----------
        test_inputs : Input
            Inputs at which to evalute the mean and covariance functions.

        Returns
        -------
        MultivariateNormalFullCovariance
            Multivariate normal distribution over the given inputs.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def __mul__(self, other: "Observation") -> "AbstractPosterior":
        raise NotImplementedError
    
    @overload
    def __rmul__(self, other: "Observation") -> "Posterior":
        ...

    @overload
    def __rmul__(self, other: "Observation") -> "SparsePosterior":
        ...

    def __rmul__(self, other):
        # TODO: docs
        return self.__mul__(other)


@dataclass
class Prior(AbstractPrior):

    def forward(self, test_inputs: Input) -> MultivariateNormal:
        '''Returns a Multivariate normal distribution over the given inputs.

        Parameters
        ----------
        test_inputs : Input
            Inputs at which to evalute the mean and covariance functions.

        Returns
        -------
        MultivariateNormalTriL
            Multivariate normal distribution over the given inputs.
        '''
        m_x = self.mean.mean_vector(test_inputs)
        K_xx = self.covariance.gram_matrix(test_inputs)

        diag = jnp.diag_indices(len(K_xx))
        K_xx = K_xx.at[diag].add(self.jitter)

        return MultivariateNormal(m_x, K_xx)
    
    def __mul__(self, other: "Observation") -> "Posterior":
        # TODO: docs
        return Posterior(other, self)


@dataclass
class SparsePrior(AbstractPrior):
    inducing_set: "InducingSet" = None

    def forward(self, test_inputs: Input) -> SparseMultivariateNormal:
        '''Returns a Multivariate normal distribution over the given inputs.

        Parameters
        ----------
        test_inputs : Input
            Inputs at which to evalute the mean and covariance functions.

        Returns
        -------
        MultivariateNormalTriL
            Multivariate normal distribution over the given inputs.
        '''
        # mean is not sparsified
        m_x = self.mean.mean_vector(test_inputs)

        # gram matrix for the inducing set
        K_uu = self.covariance.gram_matrix(self.inducing_set.to_Input())
        diag = jnp.diag_indices(len(K_uu))
        K_uu = K_uu.at[diag].add(self.jitter)

        # Lower cholesky factor of K_uu
        L_uu = jsp.linalg.cholesky(K_uu, lower=True)

        # covariance between inducing set and test inputs
        K_ux = self.covariance.covariance_matrix(self.inducing_set.to_Input(), test_inputs)

        # FIC approximation: K_xx approx. Q_xx - diag(Q_xx - K_xx), Q_xx = K_ux.T @ (K_uu)**(-1) @ K_ux
        # Q_xx = V.T @ V
        V = jsp.linalg.solve_triangular(L_uu, K_ux, lower=True)
        Q_xx_diag = vmap(lambda x: x.T@x, in_axes=(1,))(V)
        K_xx_diag = self.covariance.gram_diagonal(test_inputs)
        fic_diag = Q_xx_diag - K_xx_diag

        return SparseMultivariateNormal(m_x, V, fic_diag, L_uu)
    
    def __mul__(self, other: "Observation") -> "SparsePosterior":
        # TODO: docs
        return SparsePosterior(other, self)


# -------------------------------------------------------------------
# Posteriors

@dataclass
class AbstractPosterior(Module):
    observation: Observation

    def __call__(self, test_inputs: Input) -> Tuple[Float[Array, "N"], Float[Array, "N"]]:
        return self.forward(test_inputs)

    @abstractmethod
    def forward(self, test_inputs: Input) -> Tuple[Float[Array, "N"], Float[Array, "N"]]:
        raise NotImplementedError

@dataclass
class Posterior(AbstractPosterior):
    # TODO: docs
    prior: Prior

    def forward(self, test_inputs: Input) -> Tuple[Float[Array, "N"], Float[Array, "N"]]:
        # calculate mean and covariance of prior distribution
        prior_distr = self.prior(self.observation.X)

        m_x = prior_distr.mean()

        # add the observational noise to the prior covariance
        K_xx = prior_distr.covariance()
        diag = jnp.diag_indices(len(K_xx))
        K_xx = K_xx.at[diag].add(self.observation.noise**2)

        # lower cholesky factor of K_xx
        L_xx = jsp.linalg.cholesky(K_xx, lower=True)

        # covariance between test inputs and observations
        K_tx = self.prior.covariance.covariance_matrix(test_inputs, self.observation.X)

        # covariance between the different test inputs
        K_tt_diag = self.prior.covariance.gram_diagonal(test_inputs)

        # posterior mean via K_tx @ (K_xx)**(-1) @ (Y - m_x)
        m_t = self.prior.mean.mean_vector(test_inputs)
        mean = m_t + K_tx@jsp.linalg.cho_solve((L_xx, True), self.observation.Y - m_x)

        # diag(K_tx @ (K_xx)**(-1) @ K_tx.T)
        K_txt_diag = inner_map(L_xx, K_tx.T)
        
        # posterior std
        stddef = jnp.sqrt(K_tt_diag - K_txt_diag)

        return (mean.squeeze(), stddef.squeeze())


@dataclass
class SparsePosterior(AbstractPosterior):
    prior: SparsePrior

    def forward(self, test_inputs: Input) -> Tuple[Float[Array, "N"], Float[Array, "N"]]:
        # calculate the sparse prior for the given observations
        prior_dist = self.prior(self.observation.X)

        # Lambda = fic_diag + noise**2
        Lambda = self.observation.noise**2 - prior_dist.fic_diag

        # solve the inner matrix to be inverted
        # V.T @ Lambda**(-1) @ V + id
        V_scaled = matmul_diag(1 / jnp.sqrt(Lambda), prior_dist.scale.T)
        K_inner = V_scaled.T@V_scaled
        diag = jnp.diag_indices(len(K_inner))
        K_inner = K_inner.at[diag].add(1.0)

        # cholesky factor of the inner matrix
        L_inner = jsp.linalg.cholesky(K_inner, lower=True)

        # projected Y onto u-space via K_ut @ Lambda**(-1) @ (Y - m_x)
        m_x = prior_dist.mean()
        Y_u = (self.observation.Y - prior_dist.mean()) / Lambda.reshape(-1,1)
        Y_u = prior_dist.scale @ Y_u

        # covariance between u and test inputs
        K_ut = self.prior.covariance.covariance_matrix(self.prior.inducing_set.to_Input(), test_inputs)
        # V factor for the new inputs
        V_ut = jsp.linalg.solve_triangular(prior_dist.L_uu, K_ut, lower=True)

        # posterior mean
        m_t = self.prior.mean.mean_vector(test_inputs)
        mean = m_t + V_ut.T@jsp.linalg.cho_solve((L_inner, True), Y_u)

        # posterior std
        K_tt_diag = self.prior.covariance.gram_diagonal(test_inputs)
        Q_tt_diag = vmap(lambda x: x.T@x, in_axes=(1,))(V_ut)
        K_tut_diag = inner_map(L_inner, V_ut)

        stddef = jnp.sqrt(K_tt_diag - Q_tt_diag + K_tut_diag)

        return (mean.squeeze(), stddef.squeeze())


# -------------------------------------------------------------------
# Sparsify
    
@dataclass
class InducingSet(Module):
    # TODO: docs
    X: Float[Array, "N D"] = param_field(bijector=tfb.Identity())
    
    def to_Input(self) -> Input:
        return Input(self.X, "func")

@overload
def sparsify(inducing_set: InducingSet, model: Prior) -> "SparsePrior":
    ...

@overload
def sparsify(inducing_set: InducingSet, model: Posterior) -> "SparsePosterior":
    ...

def sparsify(inducing_set, model):
    if isinstance(model, Prior):
        return SparsePrior(model.mean, model.covariance, model.jitter, inducing_set)
    
    if isinstance(model, Posterior):
        sp_prior = SparsePrior(model.prior.mean, model.prior.covariance, model.prior.jitter, inducing_set)
        return SparsePosterior(model.observation, sp_prior)
    
    return model