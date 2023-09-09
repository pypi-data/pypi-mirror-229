import numpy as np
import matplotlib.pyplot as plt
import simulation
import tidy3d.web as web
#the simulation object contains additional information about the simulation beyond  that which
#is covered by the tidy3D simulation class

simulation_object = simulation.crosshatch_Simulation(simulation_size=(0.5,0.5,5),etch_width = .05,etch_1_y_ratio=.8,etch_1_etch_2_ratio=.8,
                                                     etch_2_angle=np.pi/4,pol_str="r",z_film= 0,source_buffer =1,monitor_buffer =1,resolution =[30,30,30])
simulation_object.plot_self()

sim = simulation_object.simulation

norm_sim = sim.copy(update={'structures':[]})

job_sim = web.Job(simulation= sim,task_name="test_crosshatch",verbose =True)
job_norm= web.Job(simulation = norm_sim,task_name="norm_crosshatch",verbose =True)

est_cost_job_sim = web.estimate_cost(job_sim.task_id)
est_cost_norm_sim = web.estimate_cost(job_norm.task_id)

print("Estimated costs are"+str(est_cost_job_sim)+" and "+str(est_cost_norm_sim)+" flex credits")

run_job= False
to_norm = False
folder = "CH_basic_high_v4_res_RHP"
if (run_job):
    data_sim = job_sim.run(path = folder+"/sim.hdf5")
    job_sim.to_file(folder+"/job.json")
    if (to_norm):
        data_norm = job_norm.run(path=folder+"/norm.hdf5")
        job_norm.to_file(folder+"/norm.json")

