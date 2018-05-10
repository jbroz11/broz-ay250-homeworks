import useful_functions as uf
from base_simulation import BaseSimulation
from rabi_flop_numerical_model_info import model_info
from qutip import *
from numpy import pi, sqrt, linspace, array, real, imag
from functools import partial

class RabiFlopNumerical(BaseSimulation):

    def __init__(self):

        self.name = "Rabi Flop"
        self.type = "numerical"

        sim_params = {"number of steps": 1000, "resolution": 10,
                      "duration": (1, 1, 10000, "μsec")}

        driving_field = {"Δ": (0, -10, 10, "MHz"),
                         "Ω": (1, -10, 10, "MHz"),
                         "phi": (0, -360, 360, "deg")}

        elec = {"lifetime": (0, 0, 1000, "sec"),
                "dephasing time": (0, 0, 1000, "μsec"),
                "initial state": ["ground", ["ground", "excited"]]}

        mot = {"nbar": 0,
               "motional dimension": 10,
               "η": .1,
               "ν": (1, -100, 100, "MHz")}

        plot_opts = {"ρ11": True,
                     "ρ22": False,
                     "ρ12": False}

        self.parameter_dict = {"simulation parameters": sim_params,
                               "driving field": driving_field,
                               "elec state info": elec,
                               "motional state info": mot,
                               "plot options": plot_opts,
                               "order in η": ["1", ["0", "1", "2", "3"]]
                               }

        self.model_information = model_info

    def Hamiltonian(self, **kwargs):

        Ω = 2 * pi * kwargs["Ω"]
        phi = kwargs["phi"]
        Δ = 2 * pi * kwargs["Δ"]
        η = kwargs["η"]
        ν = 2 * pi * kwargs["ν"]
        M = kwargs["motional dimension"]
        order = int(kwargs["order in η"])

        C = Ω / 2
        a = destroy(M)
        adag = create(M)
        IM = qeye(M)

        H1 = C * tensor(sigmap(), IM)
        H2 = C * 1j * η * tensor(sigmap(), a)
        H3 = C * 1j * η * tensor(sigmap(), adag)
        H4 = C * -η**2 * tensor(sigmap(), a * a)
        H5 = C * -η**2 * tensor(sigmap(), adag * adag)
        H6 = C * -η**2 * tensor(sigmap(), IM)
        H7 = C * -η**2 * tensor(sigmap(), 2 * adag * a)
        H8 = C * -1j * η**3 * tensor(sigmap(), a * a * a)
        H9 = C * -1j * η**3 * tensor(sigmap(), a * adag * adag)
        H10 = C * -1j * η**3 * tensor(sigmap(), -a)
        H11 = C * -1j * η**3 * tensor(sigmap(), 2 * a * a * adag)
        H12 = C * -1j * η**3 * tensor(sigmap(), adag * a * a)
        H13 = C * -1j * η**3 * tensor(sigmap(), adag * adag * adag)
        H14 = C * -1j * η**3 * tensor(sigmap(), adag)
        H15 = C * -1j * η**3 * tensor(sigmap(), 2 * adag * adag * a)

        H = [[H1, "exp(1j*(phi-delta*t))"],
             [H1.dag(), "exp(-1j*(phi-delta*t))"]]

        if order == 0:
            args = {"phi": phi, "delta": Δ}
            return H, args

        H.append([H2, "exp(1j*(phi-(delta+nu)*t))"])
        H.append([H3, "exp(1j*(phi-(delta-nu)*t))"])
        H.append([H2.dag(), "exp(-1j*(phi-(delta+nu)*t))"])
        H.append([H3.dag(), "exp(-1j*(phi-(delta-nu)*t))"])

        args = {"phi": phi, "delta": Δ, "nu": ν}

        if order == 1:
            return H, args

        H.append([H4, "exp(1j*(phi-(delta+2*nu)*t))"])
        H.append([H5, "exp(1j*(phi-(delta-2*nu)*t))"])
        H.append([H6, "exp(1j*(phi-delta*t))"])
        H.append([H7, "exp(1j*(phi-delta*t))"])
        H.append([H4.dag(), "exp(-1j*(phi-(delta+2*nu)*t))"])
        H.append([H5.dag(), "exp(-1j*(phi-(delta-2*nu)*t))"])
        H.append([H6.dag(), "exp(-1j*(phi-delta*t))"])
        H.append([H7.dag(), "exp(-1j*(phi-delta*t))"])

        if order == 2:
            return H, args

        H.append([H8, "exp(1j*(phi-(delta+3*nu)*t))"])
        H.append([H9, "exp(1j*(phi-(delta-nu)*t))"])
        H.append([H10, "exp(1j*(phi-(delta+nu)*t))"])
        H.append([H11, "exp(1j*(phi-(delta+nu)*t))"])
        H.append([H12, "exp(1j*(phi-(delta+nu)*t))"])
        H.append([H13, "exp(1j*(phi-(delta-3*nu)*t))"])
        H.append([H14, "exp(1j*(phi-(delta-nu)*t))"])
        H.append([H15, "exp(1j*(phi-(delta-nu)*t))"])
        H.append([H8.dag(), "exp(-1j*(phi-(delta+3*nu)*t))"])
        H.append([H9.dag(), "exp(-1j*(phi-(delta-nu)*t))"])
        H.append([H10.dag(), "exp(-1j*(phi-(delta+nu)*t))"])
        H.append([H11.dag(), "exp(-1j*(phi-(delta+nu)*t))"])
        H.append([H12.dag(), "exp(-1j*(phi-(delta+nu)*t))"])
        H.append([H13.dag(), "exp(-1j*(phi-(delta-3*nu)*t))"])
        H.append([H14.dag(), "exp(-1j*(phi-(delta-nu)*t))"])
        H.append([H15.dag(), "exp(-1j*(phi-(delta-nu)*t))"])

        return H, args

    def run_master_equation(self, **kwargs):

        try:
            γ2 = sqrt(1 / (kwargs["lifetime"] * 1e6))
        except ZeroDivisionError:
            γ2 = 0
        try:
            γ12 = sqrt(1 / kwargs["dephasing time"])
        except ZeroDivisionError:
            γ12 = 0
        nbar = kwargs["nbar"]
        nsteps = kwargs["number of steps"]
        res = kwargs["resolution"]
        duration = kwargs["duration"]
        init_state = kwargs["initial state"]
        M = kwargs["motional dimension"]
        ρ11 = kwargs["ρ11"]
        ρ22 = kwargs["ρ22"]
        ρ12 = kwargs["ρ12"]

        c_ops = []
        if γ2 != 0:
            T1 = tensor(sqrt(γ2) * sigmap(), qeye(M))  # Spontaneous emission
            c_ops.append(T1)
        if γ12 != 0:
            dephasing = tensor(sqrt(γ12) * sigmaz(), qeye(M))  # pure dephasing
            c_ops.append(dephasing)

        t_list = linspace(0, duration, res)

        if nbar >= M:
                nbar = M - 1

        if init_state == "ground":
            init_state = tensor(basis(2, 0) * basis(2, 0).dag(),
                                thermal_dm(M, nbar))
        else:
            init_state = tensor(basis(2, 1) * basis(2, 1).dag(),
                                thermal_dm(M, nbar))

        H, args = self.Hamiltonian(**kwargs)

        output = mesolve(H, init_state, t_list, c_ops, [], args=args,
                         options=Options(nsteps=nsteps),
                         progress_bar=ui.TextProgressBar())

        self.states = output.states

        data = [t_list]
        if ρ11:
            ρ11 = abs(array(parfor(partial(uf.ρ, 1, 1), self.states)))
            data.append([r"$\rho_{11}$", ρ11])
        if ρ22:
            ρ22 = abs(array(parfor(partial(uf.ρ, 2, 2), self.states)))
            data.append([r"$\rho_{22}$", ρ22])
        if ρ12:
            ρ12 = array(parfor(partial(uf.ρ, 1, 2), self.states))
            data.append([r"$Re(\rho_{12})$", real(ρ12)])
            data.append([r"$Im(\rho_{12})$", imag(ρ12)])

        return data

    def run_monte_carlo(self, **kwargs):

        try:
            γ2 = sqrt(1 / (kwargs["lifetime"] * 1e6))
        except ZeroDivisionError:
            γ2 = 0
        try:
            γ12 = sqrt(1 / kwargs["dephasing time"])
        except ZeroDivisionError:
            γ12 = 0
        if γ2 == 0 and γ12 == 0:
            return [[], ["", []]]
        nbar = kwargs["nbar"]
        nsteps = kwargs["number of steps"]
        res = kwargs["resolution"]
        duration = kwargs["duration"]
        init_state = kwargs["initial state"]
        M = kwargs["motional dimension"]
        ρ11 = kwargs["ρ11"]
        ρ22 = kwargs["ρ22"]
        ρ12 = kwargs["ρ12"]

        c_ops = []
        if γ2 != 0:
            T1 = tensor(sqrt(γ2) * sigmap(), qeye(M))  # Spontaneous emission
            c_ops.append(T1)
        if γ12 != 0:
            dephasing = tensor(sqrt(γ12) * sigmaz(), qeye(M))  # pure dephasing
            c_ops.append(dephasing)

        t_list = linspace(0, duration, res)

        if nbar >= M:
                nbar = M - 1

        if init_state == "ground":
            init_state = tensor(basis(2, 0), basis(M, nbar))
        else:
            init_state = tensor(basis(2, 1), basis(M, nbar))

        H, args = self.Hamiltonian(**kwargs)

        expect = [tensor(basis(2, 0) * basis(2, 0).dag(), qeye(M)),
                  tensor(basis(2, 1) * basis(2, 1).dag(), qeye(M)),
                  tensor(basis(2, 0) * basis(2, 1).dag(), qeye(M))]

        output = mcsolve(H, init_state, t_list, c_ops, expect, args=args,
                         options=Options(nsteps=nsteps),
                         progress_bar=ui.TextProgressBar())

        states = output.expect
        self.states = [t_list, states]

        data = [t_list]
        if ρ11:
            data.append([r"$\rho_{11}$", states[0]])
        if ρ22:
            data.append([r"$\rho_{22}$", states[1]])
        if ρ12:
            data.append([r"$Re(\rho_{12})$", real(states[2])])
            data.append([r"$Im(\rho_{12})$", imag(states[2])])

        return data


