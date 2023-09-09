import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import modeling
'''
Trying to get a sense of peak heights, prominences, etc. from this
batch of data
'''

wvl_array = np.load("second_batch_spec.npy")

parameter_set = np.load("parameter_set_batch_2.npy")
parameter_set = parameter_set.T
parameter_set = np.delete(parameter_set,2,1) #deleting width column (all widths should be same-50 nm)

parameter_bounds = np.load("batch_2_bounds.npy")
parameter_bounds = np.delete(parameter_bounds,2,0)

data_lhp = np.load("second_batch_lhp_normed.npy")
data_rhp = np.load("second_batch_rhp_normed.npy")


trans_lhp = -np.log10(data_lhp)[0,:,:].T
trans_rhp = -np.log10(data_rhp)[0,:,:].T

mean_trans = (trans_lhp+trans_rhp)/2
cd=  -np.log(trans_lhp/trans_rhp)

spec_test = cd[0,:]
peaks_pos, peak_dict_pos = sp.signal.find_peaks(spec_test,height = .01,prominence=1e-2)
peaks_neg, peak_dict_neg = sp.signal.find_peaks(-spec_test,height = .01,prominence=1e-2)
prominence = sp.signal.peak_prominences(spec_test,peaks_pos)

plt.plot(spec_test)
plt.plot(peaks_pos,spec_test[peaks_pos],"x")
plt.plot(peaks_neg,spec_test[peaks_neg],"x")
plt.show()

peak_model = modeling.Peak_Model(wvl_array,cd,n_peaks=1)

