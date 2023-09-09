import numpy as np
import modeling
import tensorflow
from tensorflow import keras
from keras import layers


num_runs = 20

parameter_set = np.load("parameter_set_batch_1.npy")
parameter_set = parameter_set[:,:num_runs].T

parameter_bounds = np.load("batch_1_bounds.npy")

data_lhp = np.load("first_batch_lhp_normed.npy")
data_rhp = np.load("first_batch_rhp_normed.npy")


trans_lhp = -np.log10(data_lhp)[0,:500,:].T
trans_rhp = -np.log10(data_rhp)[0,:500,:].T

mean_trans = (trans_lhp+trans_rhp)/2
cd=  -np.log(trans_lhp/trans_rhp)

spectra = cd

fit_coefs, pca = modeling.pca_spectra(spectra)

trunc_size= 4
pca_object = modeling.PCA_Model(pca,fit_coefs,truncation_size=trunc_size)
pca_object.check_truncation_inverse_visual(idx=  3)


fit_coefs_sep = pca_object.sep_fit_coefs

norm_factor = np.max(np.abs(fit_coefs_sep))
fit_coefs_normed = fit_coefs_sep/norm_factor

def norm_inputs(input_data,bounds_max):
    input_data_normed = np.einsum("ij,j->ij",input_data,1/bounds_max)
    input_norms = 1/bounds_max
    return input_data_normed,input_norms

input_data_normed,input_norms = norm_inputs(parameter_set,parameter_bounds[:,1])

spec_norm_factor = np.max(np.abs(spectra))
if (np.isscalar(spec_norm_factor)):
    cd_data_normed =spectra/spec_norm_factor
else:
    spectra_normed = np.einsum('ij,i->ij',spectra,1/spec_norm_factor)

x_data_to_use = input_data_normed
y_data_to_use = fit_coefs_normed

sep_idx =4
x_test, x_train = x_data_to_use[:sep_idx,:],x_data_to_use[sep_idx:,:]
y_test, y_train = y_data_to_use[:sep_idx,:],y_data_to_use[sep_idx:,:]


val_idx =2
x_val = x_train[-val_idx:,:]
y_val = y_train[-val_idx:,:]
x_train = x_train[:-val_idx,:]
y_train = y_train[:-val_idx,:]

# test_data= tf.data.Dataset.from_tensor_slices((quaternion_data_test,fit_coefs_test))
# train_data = tf.data.Dataset.from_tensor_slices((quaternion_data_train,fit_coefs_train))



dropout_rate = .02
model = keras.Sequential(
    [
        keras.Input(shape = (np.size(x_train,axis =-1),)),
        layers.Dense(20, activation="relu", name="layer1"),
        layers.Dropout(dropout_rate,name = "dropout1"),
        layers.Dense(20, activation="relu", name="layer2"),
        layers.Dropout(dropout_rate,name = "dropout2"),
        layers.Dense(np.size(y_train,axis =-1), name="layer4"),
    ])


model.compile(
    optimizer=keras.optimizers.Adam(),  # Optimizer
    # Loss function to minimize
    loss='mean_squared_error',
    # List of metrics to monitor
    metrics=['accuracy'],
)

print("Fit model on training data")
history = model.fit(
    x_train,
    y_train,
    epochs = 3,
    validation_data=(x_val, y_val),
)

history.history
results = model.evaluate(x_test, y_test, batch_size=5)
print("test loss, test acc:", results)

idx_2 = np.random.randint(low = 0,high = val_idx)
spec_test = spectra[-val_idx+idx_2,:]
np.save("spec_forward_test",spec_test)

spec_input_test = spectra[-val_idx+idx_2,:]

fit_coefs_pred = model.predict(np.atleast_2d(x_val[idx_2,:]))
fit_coefs_pred_renormed = fit_coefs_pred*norm_factor
fit_coefs_pred_to_inverse = np.zeros((1,np.size(fit_coefs,axis =1)))
fit_coefs_pred_to_inverse[:,:trunc_size] = fit_coefs_pred_renormed
spec_pred = pca.inverse_transform(np.atleast_2d(fit_coefs_pred_to_inverse))
np.save('spec_forward_pred',spec_pred)

import matplotlib.pyplot as plt

plt.plot(spec_input_test)
plt.plot(spec_pred[0,:])
plt.show()