import numpy as np
import matplotlib.pyplot as plt
import simulation
import tidy3d.web as web
import os
import time
parameter_set = np.load("parameter_set_batch_1.npy")
max_credit_cost = .05
create_job = True
run_job = False
base_folder = "CH_BATCH_1_LHP"
for i in range(2):
    current_parameters = parameter_set[:,i]
    sx,sy = current_parameters[0],current_parameters[1]
    etch_width = current_parameters[2]
    etch_1_y_ratio = current_parameters[3]
    etch_1_etch_2_ratio = current_parameters[4]
    to_norm = False
    simulation_object = simulation.crosshatch_Simulation(simulation_size=(sx,sy,5),etch_width = etch_width,etch_1_y_ratio=etch_1_y_ratio,etch_1_etch_2_ratio=etch_1_etch_2_ratio,
                                                         etch_2_angle=np.pi/4,pol_str="l",z_film= 0,source_buffer =1,monitor_buffer =1,resolution =[25,25,25])
    simulation_object.plot_self()

    if (create_job):
        sim = simulation_object.simulation
        job_sim = web.Job(simulation=sim, task_name="test_crosshatch", verbose=True)
        if (i == 0):
            norm_sim = sim.copy(update={'structures':[]})
            job_norm = web.Job(simulation=norm_sim, task_name="norm_crosshatch", verbose=True)
            est_cost_norm_sim = web.estimate_cost(job_norm.task_id)
            to_norm = True
        est_cost_job_sim = web.estimate_cost(job_sim.task_id)
        if (est_cost_job_sim >max_credit_cost):
            print("Excess Cost: Skip")
            continue
        print("Estimated cost are"+str(est_cost_job_sim)+" flex credits")
        sub_folder = "RUN_"+str(i)
        folder = os.sep.join((base_folder,sub_folder))
        if (run_job):
            data_sim = job_sim.run(path = folder+"/sim.hdf5")
            job_sim.to_file(folder+"/sim.json")
            if (to_norm):
                data_norm = job_norm.run(path=folder+"/norm.hdf5")
                job_norm.to_file(folder+"/norm.json")
    time.sleep(5)
