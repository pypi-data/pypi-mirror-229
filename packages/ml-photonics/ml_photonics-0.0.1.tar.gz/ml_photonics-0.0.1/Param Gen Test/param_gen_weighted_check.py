import numpy as np
import parameter_generation as param_gen

parameter_array = np.vstack((np.linspace(0,1,5),
                            np.linspace(1,2,5)))

weight_array = np.ones(5)/5

bound_array = np.array([[0,1],[1,2]])

weighted_param_gen = param_gen.WeightedParameterGenerator(parameter_array,weight_array,bound_array)

param_set = weighted_param_gen.get_random_parameter_set(10,kick=.5)
print(param_set)