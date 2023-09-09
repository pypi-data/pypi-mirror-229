# ML_Photonics
Andrew Salij

This is a suite for creating photonic systems, running machine learning algorithms on results from said systems, and using those results for further design and optimization.

Core Dependencies: keras, numpy, tidy3D, scikit-learn, pandas

At present, this repository is designed around a workflow of creating simulations in Tidy3D, using TensorFlow to create neural networks that reproduce spectral results, and then using
the neural networks to propose additional systems to run. 

For a good overview of the scientific considerations at play here, Ma, W., Liu, Z., Kudyshev, Z. A., Boltasseva, A., Cai, W., & Liu, Y. (2021). Deep learning for the design of photonic structures. Nature Photonics, 15(2), 77-90. is a solid introduction. 
