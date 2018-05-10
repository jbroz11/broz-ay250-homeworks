from base_simulation import BaseSimulation
from numpy import linspace, sin, pi, sqrt

class RabiFlopAnalytic(BaseSimulation):

    def __init__(self):

        self.name = "Rabi Flop"
        self.type = "analytical"
        self.parameter_dict = {"Ω": (1, 0, 100, "MHz"),
                               "Δ": (0, 0, 100, "MHz"),
                               "duration": 5,
                               "resolution": 1000}
        self.model_information = (r"$P_{1\rightarrow 2} = $"
          r"$\frac{\Omega^2}{\Omega^2 + \Delta^2}\textrm{sin}^2(\sqrt{\Omega^2 + \Delta^2} t)$")

    def run(self, **kwargs):
        Ω = kwargs["Ω"]
        Δ = kwargs["Δ"]
        duration = kwargs["duration"]
        resolution = kwargs["resolution"]

        t_list = linspace(0, duration, resolution)

        C = Ω**2 / (Ω**2 + Δ**2)
        Ω0 = sqrt(Ω**2 + Δ**2)

        Pe = [C * sin(2 * pi * Ω0 * t)**2 for t in t_list]

        return [t_list, [r"$P_{1\rightarrow 2}$", Pe]]
