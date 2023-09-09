import numpy as np
import tidy3d as td
import tidy3d.web as web
import xarray
import os
'''
Scripts for the handling of FDTD results
'''

def load_td_results(json_path,data_path):
    '''
    Loads tidy3d results from given path and results the results object
    :param path:
    :return:
    '''
    data_load = web.Job.from_file(json_path)
    return data_load.load(data_path)

def get_concatenated_flux_data(flux_data):
    '''
    Takes flux_data tuple from tidy3D loading and converts to xarray that
    collate the monitors. Monitor name list also passed for assignment of each
    collumn of concatenated data
    :param flux_data:
    :return: xarray, list
    '''
    flux_data_list = list(flux_data.data)
    monitor_list = list(map(lambda x:x.monitor,flux_data_list))
    monitor_name_list = list(map(lambda x:x.name,monitor_list))
    flux_list = list(map(lambda x:x.flux,flux_data_list))
    flux_data_concat = xarray.concat(flux_list,"monitor")
    return flux_data_concat,monitor_name_list

def convert_freq_data_array_to_nm(data_array):
    '''
    Assumes that data is labeled as 'f'--may generalize in future
    :param data_array: 
    :return: 
    '''
    if (data_array.f.units.lower() != 'hz'):
        Warning("Freq data array must be in Hz")
    new_data_array = data_array.assign_coords(f=(3e17/data_array.f))
    new_data_array.f.attrs.update(long_name = "wavelength",units = "nm")
    return new_data_array

def get_flux_data_array_nm_from_load(data_loaded,norm_data_loaded):
    '''
    Converts tidy3d loaded flux data into
    concatenated data arrays over all monitors in wavelength (nm) convention
    :param data_loaded:
    :param norm_data_loaded:
    :return:
    '''
    flux,labels =get_concatenated_flux_data(data_loaded)
    norm_flux,norm_labels = get_concatenated_flux_data(norm_data_loaded)
    flux_normed = flux/norm_flux
    flux_normed_nm = convert_freq_data_array_to_nm(flux_normed)
    return flux_normed_nm

def parse_data_set(folder,subfolder_base,subfolder_suffix_list,data_filename,json_filename):
    '''
    :param folder:
    :param subfolder_base:
    :param subfolder_suffix_list:
    :param data_filename:
    :param json_filename:
    :return:
    '''
    #initializing--will be set after first dataset is parsed
    num_monitors =  1
    flux_data_total = np.zeros(1)
    for i in range(len(subfolder_suffix_list)):
        current_subfolder = subfolder_base+subfolder_suffix_list[i]
        subfolder_path = os.sep.join((folder,current_subfolder))
        json_path = os.sep.join((subfolder_path,json_filename))
        data_path = os.sep.join((subfolder_path,data_filename))
        td_results = load_td_results(json_path=json_path,data_path=data_path)
        flux_data,monitor_list = get_concatenated_flux_data(td_results)
        if (i==0):
            num_monitors = len(monitor_list)
            flux_data_total_shape= np.shape(flux_data)+(len(subfolder_suffix_list),)
            flux_data_total = np.zeros(shape=flux_data_total_shape)
        flux_data_total[:,:,i] = flux_data
    return flux_data_total

