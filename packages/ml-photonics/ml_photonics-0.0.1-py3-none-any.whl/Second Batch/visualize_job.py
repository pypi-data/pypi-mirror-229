import numpy as np
import matplotlib.pyplot as plt
import simulation
import tidy3d.web as web
import os
import time

parameter_set = np.load("parameter_set_batch_2.npy")
base_folder = "CH_BATCH_2"

i = 86 #job number to visualize

current_parameters = parameter_set[:,i]
sx,sy = current_parameters[0],current_parameters[1]
etch_width = current_parameters[2]
etch_1_y_ratio = current_parameters[3]
etch_1_etch_2_ratio = current_parameters[4]
to_norm = False
simulation_object_lhp = simulation.crosshatch_Simulation(simulation_size=(sx,sy,5),etch_width = etch_width,etch_1_y_ratio=etch_1_y_ratio,etch_1_etch_2_ratio=etch_1_etch_2_ratio,
                                                     etch_2_angle=np.pi/4,pol_str="l",z_film= 0,source_buffer =1,monitor_buffer =1,resolution =[25,25,25],wvl_range = [.4,1.2])
simulation_object_rhp =simulation.crosshatch_Simulation(simulation_size=(sx,sy,5),etch_width = etch_width,etch_1_y_ratio=etch_1_y_ratio,etch_1_etch_2_ratio=etch_1_etch_2_ratio,
                                                     etch_2_angle=np.pi/4,pol_str="r",z_film= 0,source_buffer =1,monitor_buffer =1,resolution =[25,25,25],wvl_range = [.4,1.2])
simulation_object_lhp.plot_self()