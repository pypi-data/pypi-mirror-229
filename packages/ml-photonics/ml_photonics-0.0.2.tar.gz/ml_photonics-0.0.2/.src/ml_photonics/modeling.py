import lpproj
import numpy as np
import sklearn.decomposition
import matplotlib.pyplot as plt
import pickle
import scipy as sp

class PCA_Model():
    def __init__(self,pca_model,fit_coefs,truncation_size=None):
        if (truncation_size == None):
            truncation_size = np.size(fit_coefs,axis = -1)
        self.pca_model = pca_model
        self.fit_coefs = fit_coefs
        self.fit_coefs_trunc= np.copy(fit_coefs)
        self.fit_coefs_trunc[:,truncation_size:] = 0
        self.sep_fit_coefs = fit_coefs[:,:truncation_size]

    def check_truncation_inverse_visual(self,idx= 0):
        data_inv_full = self.pca_model.inverse_transform(self.fit_coefs[idx,:])
        data_inv_trunc = self.pca_model.inverse_transform(self.fit_coefs_trunc[idx,:])
        plt.plot(data_inv_trunc,color = "black",linestyle = "dotted")
        plt.plot(data_inv_full,color ="black")
        plt.show()

class Peak_Model():
    def __init__(self,wvl_array,spectra_set,n_peaks =1):
        self.wvl_array = wvl_array
        self.spectra_set = spectra_set
        self.peaks = self.get_peaks(wvl_array,spectra_set,n_peaks)
    def get_peaks(self,wvl_array,spectra_set,n_peaks,height_ratio = .1,promience_ratio = 0.05):
        if (np.size(spectra_set,axis=-1) != np.size(wvl_array)):
            ValueError("Spectra set final axis must be same size as wavelength array")
        peaks_array = np.zeros(shape= (np.size(spectra_set,axis=0),2,n_peaks))
        for i in range(np.size(spectra_set,axis=0)):
            cur_spectra = spectra_set[i,:]
            spec_max_abs=  np.max(np.abs(cur_spectra))
            req_height =spec_max_abs*height_ratio #peak must be at least 1/10 of the max recorded signal by default
            req_prominence = spec_max_abs*promience_ratio
            peaks_pos,peaks_pos_dict= sp.signal.find_peaks(cur_spectra,height=req_height,prominence=req_prominence)
            peaks_neg,peaks_neg_dict= sp.signal.find_peaks(-1*cur_spectra,height=req_height,prominence=req_prominence)
            peaks_total_idx = np.concatenate((peaks_neg,peaks_pos))
            peak_params = np.vstack((wvl_array[peaks_total_idx],cur_spectra[peaks_total_idx]))
            peak_argsort = np.argsort(-np.abs(cur_spectra[peaks_total_idx]))
            peak_params_sorted = peak_params[:,peak_argsort]
            peaks_array[i,:,:] = peak_params_sorted[:,:n_peaks]
        return peaks_array

class LPP_Model():
    def __init__(self, lpp_model, fit_coefs, truncation_size=None):
        if (truncation_size == None):
            truncation_size = np.size(fit_coefs, axis=-1)
        self.lpp_model = lpp_model
        self.fit_coefs = fit_coefs

def pca_spectra(spectral_set,**pca_params):
    pca = sklearn.decomposition.PCA(**pca_params)
    fit_coefs = pca.fit_transform(spectral_set)
    return fit_coefs, pca

def lpp_spectra(spectral_set,**lpp_params):
    lpp = lpproj.LocalityPreservingProjection(**lpp_params)
    fit_coefs = lpp.fit_transform(spectral_set)
    return fit_coefs, lpp

def random_projection_spectra(spectral_set,**rp_params):
    rp_transformer = sklearn.random_projection.GaussianRandomProjection(**rp_params)
    fit_coefs = rp_transformer.fit_transform(spectral_set)
    return fit_coefs, rp_transformer
def lpp_pseudo_inverse(lpp,fit_coefs_array):
    '''
    Note that LPP cannot really be inverted, so this doesn't work
    :param lpp:
    :param fit_coefs_array:
    :return:
    '''
    projection_matrix = lpp.projection_.T
    # fit_coefs.T = lpp.projection_.T*spectra_set.T--we want to find spectra set
    pseudo_inverse_projection= np.linalg.pinv(projection_matrix)
    spectra_set = np.dot(pseudo_inverse_projection,fit_coefs_array.T).T
    return spectra_set

from sklearn.random_projection import GaussianRandomProjection
class Random_Projection_Model():
    def __init__(self,spectral_set,n_components):
        self.rp_model = GaussianRandomProjection(n_components=n_components,compute_inverse_components=True)
        self.fit_coefs = self.rp_model.fit_transform(spectral_set)
        self.spectra_inverted = self.rp_model.inverse_transform(self.fit_coefs)

