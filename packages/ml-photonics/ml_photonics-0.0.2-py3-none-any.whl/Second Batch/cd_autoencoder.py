import keras
from keras import layers
import numpy as np

encoded_dim = 20

spectra_data = np.load("second_batch_cd.npy")

spec_size = np.size(spectra_data,axis =-1)
input_layer= keras.Input(shape = (spec_size,))
encoded_layer = layers.Dense(2000,activation='relu')(input_layer)
encoded_layer = layers.Dense(2000,activation = 'relu')(encoded_layer)
encoded_layer = layers.Dense(encoded_dim,activation = 'relu')(encoded_layer)

decoded_layer = layers.Dense(2000,activation = 'relu')(encoded_layer)
decoded_layer = layers.Dense(2000,activation = 'relu')(decoded_layer)
decoded_layer = layers.Dense(spec_size,activation = "sigmoid")(decoded_layer)

autoencoder_model = keras.Model(input_layer,decoded_layer)

encoder_model = keras.Model(input_layer,encoded_layer)

encoded_input_layer = keras.Input(shape = (encoded_dim,))

decoder_layer = autoencoder_model.layers[-3](encoded_input_layer)
decoder_layer = layers.Dense(200,activation = 'relu')(decoder_layer)
decoder_layer = layers.Dense(spec_size,activation = "sigmoid")(decoder_layer)

decoder_model = keras.Model(inputs =encoded_input_layer,outputs= decoder_layer)

autoencoder_model.compile(optimizer='adam',loss = 'mse')

x_data_to_use = spectra_data/np.max(np.abs(spectra_data))

sep_idx =10
x_test, x_train = x_data_to_use[:sep_idx,:],x_data_to_use[sep_idx:,:]

autoencoder_model.fit(x_train,x_train,
                      epochs = 50,
                      batch_size = 30,
                      shuffle = True,
                      validation_data = (x_test,x_test))

encoded_spectra = encoder_model.predict(x_test)
decoded_spectra = decoder_model.predict(encoded_spectra)


import matplotlib.pyplot as plt

for i in range(np.size(x_test,axis=0)):
    spec_to_reprod = x_test[i,:]
    decoded_spectrum = decoded_spectra[i,:]

    plt.plot(spec_to_reprod,color = "black")
    plt.plot(decoded_spectrum,color = 'black',linestyle = 'dotted')
    plt.show()
