# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Science target templates
#
# The companion python package [ScopeSim-Templates](https://scopesim-templates.readthedocs.io/en/latest/) contains a library of helper functions for generating ScopeSim-friendly `Source` objects for various common astronomical sources.
#
# For more information, please see the [ScopeSim-Templates documentation](https://scopesim-templates.readthedocs.io/en/latest/)

# +
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import scopesim_templates as sim_tp
# -

# ## A basic star cluster

my_cluster = sim_tp.stellar.clusters.cluster(mass=1000.0,       # [Msun]
                                             distance=8000,     # [pc]
                                             core_radius=1)     # [pc]
my_cluster.plot()

# ## A basic elliptical galaxy

# +
# See the docstring of `elliptical` for more keywords
my_elliptical = sim_tp.extragalactic.galaxies.elliptical(half_light_radius=30,   # [arcsec]
                                                         pixel_scale=0.1,        # [arcsec]
                                                         filter_name="Ks",
                                                         amplitude=10,
                                                         normalization="total",  # [Ks=10 for integrated flux]
                                                         n=4,                    # Sersic index    
                                                         ellipticity=0.5,
                                                         angle=30)

plt.figure(figsize=(12, 5))
plt.subplot(121)
plt.imshow(my_elliptical.fields[0].data, norm=LogNorm(), extent=[-25.6, 25.6, -25.6, 25.6])
plt.xlabel("[arcsec]")
plt.subplot(122)
wave = np.arange(5000, 25000)   # [angstrom]
plt.plot(wave, my_elliptical.spectra[0](wave))
plt.xlabel("Wavelength [Angstrom]")
