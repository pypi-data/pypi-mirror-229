import numpy as np
import parameter_generation as param_gen

'''Generation of second batch of parameters to test'''
x_size_bounds = np.array([.3,.6])
y_size_bounds = np.array([.4,.8])
etch_width_bounds = np.array([0.05,.05]) #no variation in order to minimize number of free params
etch_1_y_ratio = np.array([.5,.9])
etch_1_etch_2_ratio= np.array([.5,1.5])


parameter_set_generator = param_gen.UniformParameterGenerator(x_size_bounds,y_size_bounds,etch_width_bounds,etch_1_y_ratio,etch_1_etch_2_ratio)

parameter_set = parameter_set_generator.get_random_parameter_set(n=100)

all_bounds = np.vstack((x_size_bounds,y_size_bounds,etch_width_bounds,etch_1_y_ratio,etch_1_etch_2_ratio))
np.save("parameter_set_batch_2.npy",parameter_set)
np.save("batch_2_bounds.npy",all_bounds)