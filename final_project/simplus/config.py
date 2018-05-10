# A dictionary with all of the simulation models that will be included
# in the program. The dictionary keys correspond to tab names (all
# lower case) in the GUI. The dictionary values are tuples, where the
# first element is the simulation file name (without the '.py') and
# the second element is the name of the class containing the simulation
# object.

model_dict = dict()
model_dict["Analytical"] = [("rabi_flop_analytic", "RabiFlopAnalytic"),
                            ("ms_analytic", "MSAnalytic")]
model_dict["Numerical"] = [("rabi_flop_numerical", "RabiFlopNumerical"),
                           ("ms_numerical", "MSNumerical")]
