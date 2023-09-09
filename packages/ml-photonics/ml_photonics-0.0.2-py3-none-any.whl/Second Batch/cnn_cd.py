import numpy as np
import modeling
import tensorflow
from tensorflow import keras
from keras import layers
import matplotlib.pyplot as plt

num_runs = 100

wvl_array = np.load("second_batch_spec.npy")

parameter_set = np.load("parameter_set_batch_2.npy")
parameter_set = parameter_set[:,:num_runs].T
parameter_set = np.delete(parameter_set,2,1) #deleting width column (all widths should be same-50 nm)

parameter_bounds = np.load("batch_2_bounds.npy")
parameter_bounds = np.delete(parameter_bounds,2,0)

data_lhp = np.load("second_batch_lhp_normed.npy")
data_rhp = np.load("second_batch_rhp_normed.npy")


trans_lhp = -np.log10(data_lhp)[0,:,:].T
trans_rhp = -np.log10(data_rhp)[0,:,:].T

mean_trans = (trans_lhp+trans_rhp)/2
cd=  -np.log(trans_lhp/trans_rhp)
mean_abs = -np.log(trans_lhp*trans_rhp)/2
np.save("second_batch_cd.npy",cd)

spectra = cd
model_type = "lpp"
n_peaks = 1
if (model_type == "pca"):
    fit_coefs, pca = modeling.pca_spectra(spectra)
    trunc_size= 20
    pca_object = modeling.PCA_Model(pca,fit_coefs,truncation_size=trunc_size)
    pca_object.check_truncation_inverse_visual(idx=  3)
    fit_coefs_sep = pca_object.sep_fit_coefs
    norm_factor = np.max(np.abs(fit_coefs_sep))
    fit_coefs_normed = fit_coefs_sep/norm_factor
elif (model_type == "rp"):
    trunc_size= 10
    rp_object = modeling.Random_Projection_Model(spectra,trunc_size)
    fit_coefs = rp_object.fit_coefs

    norm_factor = np.max(np.abs(fit_coefs))
    fit_coefs_normed = fit_coefs/norm_factor
    spectra_reconstructed = rp_object.spectra_inverted
    plt.plot(spectra[4,:])
    plt.plot(spectra_reconstructed[4,:])
    plt.show()
elif (model_type == "lpp"):
    trunc_size= 5
    fit_coefs, lpp= modeling.lpp_spectra(spectra,n_components = trunc_size)
    lpp_object = modeling.LPP_Model(lpp,fit_coefs)
    norm_factor = np.max(np.abs(fit_coefs))
    fit_coefs_normed = fit_coefs/norm_factor
    spectra_reconstructed = modeling.lpp_pseudo_inverse(lpp,fit_coefs)
    plt.plot(spectra[0,:])
    plt.plot(spectra_reconstructed[0,:])
    plt.show()
elif(model_type=="peaks"):
    peak_model = modeling.Peak_Model(wvl_array,spectra,n_peaks=n_peaks)
    peaks = peak_model.peaks
    peaks_init_shape = np.array(np.shape(peaks))
    peak_wvl_init_max = np.max(peaks[:,0,:])
    peak_wvl_init_min = np.min(peaks[:,0,:])
    peak_norms = np.array([peak_wvl_init_max-peak_wvl_init_min,np.max(np.abs(spectra))])
    peak_shift = peaks[:,0,:]-peak_wvl_init_min
    peaks_shifted = np.copy(peaks)
    peaks_shifted[:,0,:] = peak_shift
    peaks_normed = np.einsum("ija,j->ija",peaks_shifted,1/peak_norms)
    peaks_2d_normed = peaks_normed.reshape((peaks_init_shape[0],np.product(peaks_init_shape[1:])))
    peaks_2d_normed = np.abs(peaks_2d_normed)
def norm_inputs(input_data,parameter_bounds,shift = True):
    num_its = np.size(input_data,axis=0)
    if (shift):
        norms = np.tile(parameter_bounds[:, 1] - parameter_bounds[:, 0], (num_its, 1))
        shifts = np.tile((parameter_bounds[:, 0]),(num_its,1))
    else:
        norms = np.tile(parameter_bounds[:, 1], (num_its, 1))
        shifts = np.tile(parameter_bounds[:,0]*0,(num_its,1))
    input_data_normed = (input_data-shifts)/norms
    return input_data_normed,shifts,norms

input_data_normed,input_min,input_norms = norm_inputs(parameter_set,parameter_bounds,shift= True)

x_data_to_use =(input_data_normed-.5)*2

if (model_type=="pca" or model_type == "lpp" or model_type == "rp"):
    y_data_to_use = fit_coefs_normed
if (model_type=="peaks"):
    y_data_to_use = np.atleast_2d(peaks_2d_normed)

sep_idx =10
x_test, x_train = x_data_to_use[:sep_idx,:],x_data_to_use[sep_idx:,:]
y_test, y_train = y_data_to_use[:sep_idx,:],y_data_to_use[sep_idx:,:]


val_idx =10
x_val = x_train[-val_idx:,:]
y_val = y_train[-val_idx:,:]
x_train = x_train[:-val_idx,:]
y_train = y_train[:-val_idx,:]


dropout_rate = .01
model = keras.Sequential(
    [
        keras.Input(shape = (np.size(x_train,axis =-1),)),
        layers.Dense(100, activation="relu", name="layer1"),
        layers.Dropout(dropout_rate,name = "dropout1"),
        layers.Dense(100, activation="relu", name="layer2"),
        layers.Dense(100,activation= 'relu',name="layer3"),
        layers.Dense(np.size(y_train,axis =-1),name="layer4"),
    ])


model.compile(
    optimizer=keras.optimizers.Adam(),  # Optimizer
    loss=keras.losses.MeanSquaredError(),
    metrics=[keras.metrics.MeanSquaredError()],
)

print("Fit model on training data")
history = model.fit(
    x_train,
    y_train,
    batch_size=20,
    epochs = 3,
    validation_data=(x_val, y_val),
)

history.history
results = model.evaluate(x_test, y_test, batch_size=5)
print("test loss, test acc:", results)

idx_2 = np.random.randint(low = 0,high = val_idx)
test_idx = -val_idx+idx_2
spec_test = spectra[test_idx,:]
np.save("spec_forward_test",spec_test)

spec_input_test = spectra[test_idx,:]

if (model_type == "pca" or model_type == "rp"):
    fit_coefs_pred = model.predict(np.atleast_2d(x_val[idx_2,:]))
    fit_coefs_pred_renormed = fit_coefs_pred*norm_factor
    fit_coefs_pred_to_inverse = np.zeros((1,np.size(fit_coefs,axis =1)))
    fit_coefs_pred_to_inverse[:,:trunc_size] = fit_coefs_pred_renormed
    if (model_type == "pca"):
        spec_pred = pca.inverse_transform(np.atleast_2d(fit_coefs_pred_to_inverse))
    elif (model_type == "rp"):
        spec_pred = rp_object.rp_model.inverse_transform(fit_coefs_pred_renormed)
    np.save('spec_forward_pred',spec_pred)

    plt.plot(spec_input_test)
    plt.plot(spec_pred[0,:])
    plt.show()

if (model_type == "peaks"):
    peaks_pred = model.predict(np.atleast_2d(x_data_to_use[:,:]))
    new_shape = (np.size(peaks_pred,axis=0),2,n_peaks)
    peaks_pred_reshaped = peaks_pred.reshape(new_shape)
    y_val_new_shape = (np.size(y_data_to_use,axis=0),2,n_peaks)
    check = y_data_to_use.reshape(y_val_new_shape)

    plt.scatter(check[:,0,0],peaks_pred_reshaped[:,0,0],color ="blue")
    plt.scatter(check[:,1,0],peaks_pred_reshaped[:,1,0],color = "red")
    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.show()