from base_simulation import BaseSimulation


class MSNumerical(BaseSimulation):

    def __init__(self):

        self.name = "Molmer Sorensen"
        self.type = "numerical"
        nested_dictionary = {"some other float": 2,
                             "some other  tuple": (0, 1, 100, "dBm"),
                             "some other combo box": ["majig1", ["majig1", "majig2"]]}
        self.parameter_dict = {"some float": 2,
                               "some tuple": (0, 1, 100, "dBm"),
                               "some combo box": ["thing1", ["thing1", "thing2"]],
                               "dictionary": nested_dictionary
                              }
        self.model_information = ("This isn't implemented but I want to make sure "
                                  "everything is working.")
