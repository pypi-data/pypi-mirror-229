import numpy as np
import fdtd_results
import matplotlib.pyplot as plt

'''
Parses second batch of FDTD simulations for testing. The "etch width" paramter 
has been dropped, leaving 4 free parameters. 100 simulations were run, which
should lead to an improvement over the first batch of 100. Also, wavelength shifted to
visible-near IR (400 to 1200 nm) as this is more the region of interest. 
'''

num_runs = 100
runs_list = list(range(num_runs))
runs_str_list = list(map(str,runs_list))


data_rhp = fdtd_results.parse_data_set("CH_BATCH_2","RUN_",
                                     runs_str_list,"sim_lhp.hdf5","sim_lhp.json")

data_lhp = fdtd_results.parse_data_set("CH_BATCH_2","RUN_",
                                     runs_str_list,"sim_rhp.hdf5","sim_rhp.json")

norm_data_rhp = fdtd_results.load_td_results(r"CH_BATCH_2\RUN_0\norm.json",r"CH_BATCH_2\RUN_0\norm.hdf5")
norm_data_rhp_array,monitors_rhp = fdtd_results.get_concatenated_flux_data(norm_data_rhp)

norm_data_lhp = norm_data_rhp #normalization magnitudes should be same (they are both nearly 2 in any case due to the two sources)
norm_data_lhp_array,monitors_lhp = fdtd_results.get_concatenated_flux_data(norm_data_lhp)

data_rhp_normed=  np.einsum("ija,ij->ija",data_rhp,1/norm_data_rhp_array)
data_lhp_normed =  np.einsum("ija,ij->ija",data_lhp,1/norm_data_lhp_array)


np.save("second_batch_lhp_normed.npy",data_lhp_normed)
np.save("second_batch_rhp_normed.npy",data_rhp_normed)

abs_l = -np.log10(data_lhp_normed)
abs_r = -np.log10(data_rhp_normed)

cd = abs_l-abs_r
freq_array = np.array(norm_data_lhp_array.f)
spec_array = 2.9979e17/freq_array

'''
Plotting CD to get a sense of what the data looks like 
'''
for i in range(num_runs):
    plt.plot(spec_array,cd[0,:,i],color = "black")
plt.show()

np.save("second_batch_freq.npy",freq_array)
np.save("second_batch_spec.npy",spec_array)