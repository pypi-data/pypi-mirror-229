# Copyright (C) 2020 ETH Zurich, Institute for Particle Physics and Astrophysics
# Author: Raphael Sgier, Jörg Herbel and Alexander Reeves

import pytest
import numpy as np
from astropy.cosmology import FlatLambdaCDM
from UFalcon import utils

Om0 = 0.3
H0 = 70
Ob0 = 0.05


@pytest.fixture()
def cosmo():
    return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)


def test_comoving_distance(cosmo):
    """
    Test the computation of the comoving distance.
    """

    z_low = np.arange(0, 1, 0.1)
    z_up = z_low + np.random.uniform(low=0, high=0.2, size=z_low.size)

    for zl, zu in zip(z_low, z_up):
        com_utils = utils.comoving_distance(zl, zu, cosmo)
        com_astropy = (
            cosmo.comoving_distance(zu).value - cosmo.comoving_distance(zl).value
        )

        print("com astropy", com_astropy)
        print("com ufalc", com_utils)

        assert np.isclose(com_utils, com_astropy, rtol=1e-06)


def test_growth_z(cosmo):
    """
    Test the computation of the normalised growth factor.
    Note this is only tested up to z=3.5 which should be sufficient for most LSS surveys.
    """
    z_array = np.linspace(0, 3.5, 20)

    # growth factor as computed in the same cosmology using pyccl
    growth_ccl = [
        1.0,
        0.9089825033143222,
        0.8264172344849806,
        0.7532576453974106,
        0.6892317634793498,
        0.6334774907300478,
        0.5849394350351591,
        0.5425759309368472,
        0.5054488850564394,
        0.4727508423902183,
        0.4438026263411351,
        0.41803923671663173,
        0.3949926060167336,
        0.37427497088911954,
        0.35556446569702876,
        0.33859285321230204,
        0.323135631613484,
        0.3090038847272628,
        0.296037915983548,
        0.28410199969471345,
    ]

    growth_ufalcon = utils.growth_z(z_array, cosmo)

    assert (
        all(np.isclose(growth_ufalcon, growth_ccl, atol=0.0, rtol=1e-3)) is True
    )  # test to within 0.1% accuracy


def test_a_of_r(cosmo):
    """
    Test the accuracy of the interpolation to find a(r). Note this iunterpolation goes
    only upt o z=12 so we also limit the test to a similar range
    """
    a_array = np.logspace(-1.1, 0, 50)
    z_array = 1 / a_array - 1
    r = [utils.comoving_distance(0, z, cosmo) for z in z_array]

    recovered_a_array = utils.a_of_r(r, cosmo)  # input the vector

    assert all(np.isclose(recovered_a_array, a_array, atol=0.0, rtol=1e-3)) is True
