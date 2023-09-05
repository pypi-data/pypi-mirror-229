__all__ = ["AbstractMultivariateNormal", "MultivariateNormal", "SparseMultivariateNormal"]

from dataclasses import dataclass

import jax.numpy as jnp
import jax.scipy as jsp
from jaxtyping import Array, Float

from calcgp.gpjax_base import Module
from calcgp.typing import ScalarFloat
from calcgp.utils import matmul_diag


@dataclass
class AbstractMultivariateNormal(Module):
    loc: Float[Array, "N 1"]

    def mean(self) -> Float[Array, "N 1"]:
        return self.loc


@dataclass
class MultivariateNormal(AbstractMultivariateNormal):
    covariance_matrix: Float[Array, "N N"]

    def covariance(self) -> Float[Array, "N N"]:
        return self.covariance_matrix

    def log_prob(self, Y: Float[Array, "N 1"], noise: Float[Array, "N 1"]) -> ScalarFloat:
        K_xx = self.covariance_matrix
        diag = jnp.diag_indices(len(K_xx))
        K_xx = K_xx.at[diag].add(noise**2)

        # lower cholesky factor of K_xx
        L_xx = jsp.linalg.cholesky(K_xx, lower=True)

        L_xx_diag = jnp.diag(L_xx)
        log_det = 2*jnp.sum(jnp.log(L_xx_diag))

        fit = Y.T @ jsp.linalg.cho_solve((L_xx, True), Y)

        log_prob = -0.5*(log_det + fit + len(Y)*jnp.log(2*jnp.pi))

        return log_prob / len(Y)

@dataclass
class SparseMultivariateNormal(AbstractMultivariateNormal):
    scale: Float[Array, "M N"]
    fic_diag: Float[Array, "N"]
    L_uu: Float[Array, "M M"]

    def log_prob(self, Y: Float[Array, "N 1"], noise: Float[Array, "N 1"]) -> ScalarFloat:
        # Lambda = noise**2 - fic_diag
        Lambda = noise**2 - self.fic_diag

        # solve the inner matrix to be inverted
        # V.T @ Lambda**(-1) @ V + id
        V_scaled = matmul_diag(1 / jnp.sqrt(Lambda), self.scale.T)
        K_inner = V_scaled.T@V_scaled
        diag = jnp.diag_indices(len(K_inner))
        K_inner = K_inner.at[diag].add(1.0)

        # cholesky factor of the inner matrix
        L_inner = jsp.linalg.cholesky(K_inner, lower=True)

        L_inner_diag = jnp.diag(L_inner)
        log_det_inner = 2*jnp.sum(jnp.log(L_inner_diag))

        logdet_Lambda = jnp.sum(jnp.log(Lambda))

        Y_scaled = (Y - self.loc) / jnp.sqrt(Lambda.reshape(-1,1))
        sqrt_fit = jsp.linalg.solve_triangular(L_inner, self.scale@((Y - self.loc) / Lambda.reshape(-1,1)), lower=True)
        fit = Y_scaled.T@Y_scaled - sqrt_fit.T@sqrt_fit

        log_prob = -0.5*(log_det_inner + logdet_Lambda + fit + len(Y)*jnp.log(2*jnp.pi))

        return log_prob / len(Y)