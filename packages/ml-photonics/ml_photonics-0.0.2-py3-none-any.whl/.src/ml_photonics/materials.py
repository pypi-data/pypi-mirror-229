import numpy as np
import tidy3d as td

'''Material library for simulations
At present, using tidy3d's material library but may add additional materials/spectral ranges'''

gold_jc = td.material_library['Au']['JohnsonChristy1972'] #190 nm to 1940 nm

glass = td.material_library['SiO2']['Horiba'] #250 nm to 1770 nm