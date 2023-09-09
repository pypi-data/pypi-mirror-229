import numpy as np
import matplotlib.pyplot as plt
import tidy3d as td
import tidy3d.web as web

data_lhp_load = web.Job.from_file("CH_basic_LHP/job.json")
norm_data_lhp_load = web.Job.from_file("CH_basic_LHP/norm.json")

data_lhp = data_lhp_load.load(path="CH_basic_LHP/data.hdf5")
norm_data_lhp = norm_data_lhp_load.load(path="CH_basic_LHP/norm.hdf5")

data_rhp_load = web.Job.from_file("CH_basic_RHP/job.json")
norm_data_rhp_load = web.Job.from_file("CH_basic_RHP/norm.json")

data_rhp = data_rhp_load.load(path="CH_basic_RHP/data.hdf5")
norm_data_rhp = norm_data_rhp_load.load(path="CH_basic_RHP/norm.hdf5")


trans_lhp = data_lhp["transmission"].flux
trans_rhp = data_rhp["transmission"].flux
norm_lhp = norm_data_lhp["transmission"].flux
norm_rhp = norm_data_rhp["transmission"].flux

trans_lhp_norm = trans_lhp/norm_lhp
trans_rhp_norm = trans_rhp/norm_rhp

figure, (axis_1,axis_2) = plt.subplots(2,1,figsize = (5,8),tight_layout = True)
trans_lhp.plot(ax = axis_1,label = "Nanoarray")
norm_lhp.plot(ax= axis_1,label = "Vacuum")
axis_1.legend()
trans_lhp_norm.plot(ax=axis_2)
figure.show()

figure, (axis_1,axis_2) = plt.subplots(2,1,figsize = (5,8),tight_layout = True)
trans_rhp.plot(ax = axis_1,label = "Nanoarray")
norm_rhp.plot(ax= axis_1,label = "Vacuum")
axis_1.legend()
trans_rhp_norm.plot(ax=axis_2)
figure.show()

abs_l = -np.log10(trans_lhp_norm.to_numpy())
abs_r = -np.log10(trans_rhp_norm.to_numpy())
cd = -np.log10(trans_lhp_norm.to_numpy()/trans_rhp_norm.to_numpy())
freq_array = trans_lhp.coords['f'].values

def convert_freq_to_nm(freq_array):
    return 3e17/freq_array
def data_array_convert_freq_to_nm(data_array):
    return data_array.assign_coords([convert_freq_to_nm(data_array.coords)])
wl_array = convert_freq_to_nm(freq_array)
fig,ax = plt.subplots()
plt.plot(wl_array,abs_l,color = "blue")
plt.plot(wl_array,abs_r,color = "red")
plt.plot(wl_array,cd,color = "black")
fig.show()


