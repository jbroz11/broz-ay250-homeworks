from collections import namedtuple


class BaseSimulation:

    def __init__(self):

        # The simulation name that will be displayed in the GUI
        self.name = "Base Simulation"
        # Specifies tab to put this simulation in
        self.type = ""
        self.model_information = ""
        self.states = []

    def get_parameters(self):
        '''Returns the list of parameters for this simulation.'''
        p = self.parameter_dict
        for key, val in p.items():
            if type(val) == tuple:
                # named tuple doesn't allow spaces in identifier
                # btw, for some reason unicode ϕ doesn't work either.
                name = key.replace(" ", "_")
                nt = namedtuple(name, ["value", "range", "units"])
                nt.value = val[0]
                nt.range = (val[1], val[2])
                nt.units = val[3]
                p[key] = nt
            elif type(val) == dict:
                for key1, val1 in val.items():
                    if type(val1) == tuple:
                        # named tuple doesn't allow spaces in identifier
                        # btw, for some reason unicode ϕ doesn't work either.
                        name = key1.replace(" ", "_")
                        nt = namedtuple(name, ["value", "range", "units"])
                        nt.value = val1[0]
                        nt.range = (val1[1], val1[2])
                        nt.units = val1[3]
                        val[key1] = nt
        self.parameter_dict = p
        return self.parameter_dict

    def get_type(self):
        '''
        Returns the 'type' of simulation, which corresponds to the
        GUI tab that the simulation will be displayed under.
        '''
        return self.type

    def __str__(self):
        '''
        Returns the 'name' of the simulation, which corresponds to the
        name that will be associated with the simulation in the GUI
        displays.
        '''
        return self.name

    def model_info(self):
        return self.model_information

    def run_monte_carlo(self, **kwargs):
        '''This is where we'll implement quantum jump solver.'''
        return [0, ["", 0]]

    def run_master_equation(self, **kwargs):
        '''This is where we'll implement master equation solver.'''
        return [0, ["", 0]]

    def run(self, **kwargs):
        '''This is where we'll implement computation for analytical
        models.'''
        return [0, ["", 0]]
