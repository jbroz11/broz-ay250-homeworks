'''A place to put commonly used functions.'''
from qutip import *
from numpy import sqrt


def ρ(i, j, state, half_rotation=False):
    i -= 1
    j -= 1
    n = state.dims[0].count(2)
    m = state.dims[0][n]
    if state.isket:
        if half_rotation:
            π_2 = (1 / sqrt(2)) * qeye(2) - (1j / sqrt(2)) * sigmay()
            state = tensor([π_2] * n + [qeye(m)]) * state
        ψ = state.ptrace(range(n))
        rho = ψ * ψ.dag()
        return rho[i, j]
    return state.ptrace(range(n))[i, j]
