from importlib import import_module
from config import model_dict


class GenerateTree:

    def __init__(self):
        parameters = dict()

        for key in model_dict.keys():
            parameters[key] = dict()
            for val in model_dict[key]:
                for module_name, class_name in model_dict[key]:
                    name = getattr(import_module(module_name),
                                   class_name)().__str__()
                    p = getattr(import_module(module_name),
                                class_name)().get_parameters()
                    parameters[key][name] = p
        self.values = parameters


if __name__ == "__main__":
    gt = GenerateTree()
    print(gt.values)
