import pytest


from nnapec import get_apec_model
import numpy as np


def test_model():
    nn_apec = get_apec_model()

    nn_apec.redshift = 1.0
    nn_apec.redshift.fix = True
    nn_apec.kT = 3.0
    nn_apec.abund = 0.3

    energies = np.geomspace(0.1, 10.0, 1000)

    photon_flux = nn_apec(energies)
