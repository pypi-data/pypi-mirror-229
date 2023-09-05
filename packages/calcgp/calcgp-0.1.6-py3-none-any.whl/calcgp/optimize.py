__all__ = ["optimize"]

import jax
import jax.numpy as jnp
from beartype.typing import Callable, Union
from jaxopt._src.base import IterativeSolver

from calcgp.gpjax_base import Module


def optimize(
        fun: Union[Module, Callable], 
        solver: IterativeSolver, 
        model: Module,
        num_iter: int = 500,
        ) -> Module:
    '''TODO: docs
    '''
    def loss(model):
        # stop gradient calculation for leaves flagged as not trainable
        model = model.stop_gradient()
        # return objective evaluated at the contrained model
        return fun(model.constrain())
    
    # jaxopt needs all parameters to be of the same type and thus floats have to be turned into 0-d arrays
    def prepare(pytree):
        def vectorize(x):
            return jnp.array(x)
        
        return jax.tree_map(vectorize, pytree)

    model = prepare(model)
    model = model.unconstrain()

    solver = solver(loss)

    state = solver.init_state(model)

    iters = jnp.arange(num_iter)

    def step(carry, iter):
        model, state = carry

        loss_val = loss(model)

        model, state = solver.update(model, state)

        carry = (model, state)
        return carry, loss_val
    
    (optim_model, _), loss_history = jax.lax.scan(step, (model, state), iters) 

    return optim_model.constrain(), loss_history