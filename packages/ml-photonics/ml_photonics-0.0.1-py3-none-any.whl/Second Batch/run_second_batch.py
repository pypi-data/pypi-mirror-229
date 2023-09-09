import numpy as np
import matplotlib.pyplot as plt
import simulation
import tidy3d.web as web
import os
import time
parameter_set = np.load("parameter_set_batch_2.npy")
max_credit_cost = .04
create_job = True
run_job = True
base_folder = "CH_BATCH_2"
for i in range(100):
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

    if (create_job):
        sim_lhp = simulation_object_lhp.simulation
        sim_rhp = simulation_object_rhp.simulation
        job_sim_lhp = web.Job(simulation=sim_lhp, task_name="lhp_crosshatch", verbose=True)
        job_sim_rhp = web.Job(simulation=sim_rhp, task_name="rhp_crosshatch", verbose=True)
        if (i == 0):
            norm_sim = sim_lhp.copy(update={'structures':[]})
            job_norm = web.Job(simulation=norm_sim, task_name="norm_crosshatch", verbose=True)
            est_cost_norm_sim = web.estimate_cost(job_norm.task_id)
            to_norm = True
        est_cost_job_sim = web.estimate_cost(job_sim_lhp.task_id)
        if (est_cost_job_sim >max_credit_cost):
            print("Excess Cost: Skip")
            continue
        print("Estimated cost are"+str(est_cost_job_sim)+" flex credits")
        sub_folder = "RUN_"+str(i)
        folder = os.sep.join((base_folder,sub_folder))
        if (run_job):
            data_sim_lhp = job_sim_lhp.run(path = folder+"/sim_lhp.hdf5")
            job_sim_lhp .to_file(folder+"/sim_lhp.json")

            data_sim_rhp = job_sim_rhp.run(path=folder + "/sim_rhp.hdf5")
            job_sim_rhp.to_file(folder + "/sim_rhp.json")
            if (to_norm):
                data_norm = job_norm.run(path=folder+"/norm.hdf5")
                job_norm.to_file(folder+"/norm.json")

    time.sleep(1)
