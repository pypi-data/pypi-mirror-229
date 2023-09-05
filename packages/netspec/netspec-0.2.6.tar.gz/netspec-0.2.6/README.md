# netspec
![CI](https://github.com/grburgess/netspec/workflows/CI/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/grburgess/netspec/branch/master/graph/badge.svg)](https://codecov.io/gh/grburgess/netspec)
[![Documentation Status](https://readthedocs.org/projects/netspec/badge/?version=latest)](https://netspec.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3372456.svg)](https://doi.org/10.5281/zenodo.3372456)
![PyPI](https://img.shields.io/pypi/v/netspec)
![PyPI - Downloads](https://img.shields.io/pypi/dm/netspec)

![alt text](https://raw.githubusercontent.com/grburgess/netspec/master/docs/media/logo.png)

`netspec` allows for the use of neural net emulators of astrophysical photon /
particle emission spectra to be trained and then fitted within `3ML` to
astrophysical spectral data. It is built off `pytorch` and uses `pytorch-lightning`
as the training interface.

The network structure is adaptable and should be tuned to the need of the
simulation. Training data are derived from the outputs of
[`ronswanson`](http://jmichaelburgess.com/ronswanson/index.html) and utilities are
provided which pre-process the simulation output into suitable spaces for
efficient training. Once trained, models can be loaded in as `astromodels`
spectral function as used as any other model for spectral analysis.


* Free software: GNU General Public License v3
* Documentation: https://netspec.readthedocs.io.
