import numpy as np
import fdtd_results
import matplotlib.pyplot as plt
num_runs = 20
runs_list = list(range(num_runs))
runs_str_list = list(map(str,runs_list))



data_rhp = fdtd_results.parse_data_set("CH_BATCH_1","RUN_",
                                     runs_str_list,"sim.hdf5","sim.json")

data_lhp = fdtd_results.parse_data_set("CH_BATCH_1_LHP","RUN_",
                                     runs_str_list,"sim.hdf5","sim.json")

norm_data_rhp = fdtd_results.load_td_results(r"CH_BATCH_1\RUN_0\norm.json",r"CH_BATCH_1\RUN_0\norm.hdf5")
norm_data_rhp_array,monitors_rhp = fdtd_results.get_concatenated_flux_data(norm_data_rhp)

norm_data_lhp = fdtd_results.load_td_results(r"CH_BATCH_1_LHP\RUN_0\norm.json",r"CH_BATCH_1_LHP\RUN_0\norm.hdf5")
norm_data_lhp_array,monitors_lhp = fdtd_results.get_concatenated_flux_data(norm_data_lhp)

data_rhp_normed=  np.einsum("ija,ij->ija",data_rhp,1/norm_data_rhp_array)
data_lhp_normed =  np.einsum("ija,ij->ija",data_lhp,1/norm_data_lhp_array)


np.save("first_batch_lhp_normed.npy",data_lhp_normed)
np.save("first_batch_rhp_normed.npy",data_rhp_normed)

abs_l = -np.log10(data_lhp_normed)
abs_r = -np.log10(data_rhp_normed)

cd = abs_l-abs_r
freq_array = np.array(norm_data_lhp_array.f)
spec_array = 2.9979e17/freq_array

for i in range(num_runs):
    plt.plot(spec_array,cd[0,:,i],color = "black")
plt.xlim(500,1000)
plt.show()

np.save("first_batch_freq.npy",freq_array)
np.save("first_batch_spec.npy",spec_array)