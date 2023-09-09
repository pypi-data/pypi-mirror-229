import numpy as np
import matplotlib.pyplot as plt
import simulation


test_simulation = simulation.crosshatch_Simulation(simulation_size=(0.5,0.5,3),etch_width = .05,etch_1_y_ratio=.8,etch_1_etch_2_ratio=.8,etch_2_angle=np.pi/4,pol_str="r",z_film= 0.5)

test_simulation.plot_self()
