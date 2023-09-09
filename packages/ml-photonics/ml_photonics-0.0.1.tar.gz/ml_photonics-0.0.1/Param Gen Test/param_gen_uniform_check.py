import numpy as np
import parameter_generation as param_gen

uni_param_gen = param_gen.UniformParameterGenerator([0,1],
                                                    [1,2],
                                                    [0,2])

param_set = uni_param_gen.get_random_parameter_set(10)
print(param_set)