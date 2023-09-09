import numpy as np
import matplotlib.pyplot as plt
import tidy3d as td
import tidy3d.web as web
import fdtd_results as results

data_rhp = results.load_td_results("CH_basic_RHP/job.json","CH_basic_RHP/sim.hdf5")
norm_rhp = results.load_td_results("CH_basic_RHP/norm.json","CH_basic_RHP/norm.hdf5")

data_rhp_mr = results.load_td_results("CH_basic_med_res_RHP/job.json","CH_basic_med_res_RHP/sim.hdf5")
norm_rhp_mr = results.load_td_results("CH_basic_med_res_RHP/norm.json","CH_basic_med_res_RHP/norm.hdf5")

data_rhp_mhr = results.load_td_results("CH_basic_med_high_res_RHP/job.json","CH_basic_med_high_res_RHP/sim.hdf5")
norm_rhp_mhr = results.load_td_results("CH_basic_med_high_res_RHP/norm.json","CH_basic_med_high_res_RHP/norm.hdf5")

data_rhp_hr = results.load_td_results("CH_basic_high_res_RHP/job.json","CH_basic_high_res_RHP/sim.hdf5")
norm_rhp_hr = results.load_td_results("CH_basic_high_res_RHP/norm.json","CH_basic_high_res_RHP/norm.hdf5")

data_rhp_hr_v2 = results.load_td_results("CH_basic_high_v2_res_RHP/job.json","CH_basic_high_res_v2_RHP/sim.hdf5")
data_rhp_hr_v3 = results.load_td_results("CH_basic_high_v3_res_RHP/job.json","CH_basic_high_res_v2_RHP/sim.hdf5")
data_rhp_hr_v4 = results.load_td_results("CH_basic_high_v4_res_RHP/job.json","CH_basic_high_res_v2_RHP/sim.hdf5")


rhp_flux = results.get_concatenated_flux_data(data_rhp)
norm_rhp_flux= results.get_concatenated_flux_data(norm_rhp)

rhp_mr_flux = results.get_concatenated_flux_data(data_rhp_mr)
norm_rhp_mr_flux = results.get_concatenated_flux_data(norm_rhp_mr)

rhp_mhr_flux = results.get_concatenated_flux_data(data_rhp_mhr)
norm_rhp_mhr_flux = results.get_concatenated_flux_data(norm_rhp_mhr)

rhp_hr_flux = results.get_concatenated_flux_data(data_rhp_hr)
norm_rhp_hr_flux = results.get_concatenated_flux_data(norm_rhp_hr)

rhp_hr_v2_flux = results.get_concatenated_flux_data(data_rhp_hr_v2)
rhp_hr_v3_flux = results.get_concatenated_flux_data(data_rhp_hr_v3)
rhp_hr_v4_flux = results.get_concatenated_flux_data(data_rhp_hr_v4)

rhp_flux_normed = rhp_flux[0]/norm_rhp_flux[0]
rhp_mr_flux_normed = rhp_mr_flux[0]/norm_rhp_mr_flux[0]
rhp_mhr_flux_normed = rhp_mhr_flux[0]/norm_rhp_mhr_flux[0]
rhp_hr_flux_normed = rhp_hr_flux[0]/norm_rhp_hr_flux[0]
rhp_hr_v2_flux_normed = rhp_hr_v2_flux[0]/norm_rhp_hr_flux[0] #reusing previous normalization
rhp_hr_v3_flux_normed = rhp_hr_v3_flux[0]/norm_rhp_hr_flux[0] #reusing previous normalization
rhp_hr_v4_flux_normed = rhp_hr_v4_flux[0]/norm_rhp_hr_flux[0] #reusing previous normalization


rhp_flux_normed=results.convert_freq_data_array_to_nm(rhp_flux_normed)
rhp_mr_flux_normed= results.convert_freq_data_array_to_nm(rhp_mr_flux_normed)
rhp_mhr_flux_normed= results.convert_freq_data_array_to_nm(rhp_mhr_flux_normed)
rhp_hr_flux_normed= results.convert_freq_data_array_to_nm(rhp_hr_flux_normed)
rhp_hr_v2_flux_normed= results.convert_freq_data_array_to_nm(rhp_hr_v2_flux_normed)
rhp_hr_v3_flux_normed= results.convert_freq_data_array_to_nm(rhp_hr_v3_flux_normed)
rhp_hr_v4_flux_normed= results.convert_freq_data_array_to_nm(rhp_hr_v4_flux_normed)


fig,ax  = plt.subplots()
rhp_flux_normed[0,:].plot(ax=ax,color= "red",label = "Low Res")
rhp_mr_flux_normed[0,:].plot(ax=ax,color = "blue",label = "Med Res")
rhp_mhr_flux_normed[0,:].plot(ax=ax,color = "black",label = "Med High Res")
rhp_hr_flux_normed[0,:].plot(ax=ax,color = "green",label = "High Res")
rhp_hr_v2_flux_normed[0,:].plot(ax=ax,color = "green",label = "High Res v2",linestyle = "dotted")
rhp_hr_v3_flux_normed[0,:].plot(ax=ax,color = "green",label = "High Res v3",linestyle = "dashed")
rhp_hr_v4_flux_normed[0,:].plot(ax=ax,color = "green",label = "High Res v4",linestyle = "-.")
fig.legend()
fig.show()