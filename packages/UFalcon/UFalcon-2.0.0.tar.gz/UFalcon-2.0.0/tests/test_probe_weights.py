# Copyright (C) 2020 ETH Zurich, Institute for Particle Physics and Astrophysics
# Author: Alexander Reeves, Raphael Sgier and Jörg Herbel

from unittest import mock
import pytest
import numpy as np
from scipy import stats
from astropy.cosmology import FlatLambdaCDM
from UFalcon import probe_weights


@pytest.fixture()
def cosmo():
    omega_m = 0.3
    H0 = 70
    return FlatLambdaCDM(H0=H0, Om0=omega_m)


def test_dirac(cosmo):
    """
    Test the single-source lensing weights.
    """

    # source redshift above shell
    for z_source, z_low, z_up in [
        (0.3, 0.1, 0.11),
        (0.5, 0.4, 0.41),
        (0.7, 0.3, 0.31),
        (0.9, 0.8, 0.81),
        (1.1, 1.05, 1.06),
        (1.3, 1.2, 1.21),
        (1.5, 1.4, 1.41),
    ]:
        assert probe_weights.Dirac_lensing(z_source)(z_low, z_up, cosmo) > 0

    # source redshift below shell
    assert probe_weights.Dirac_lensing(0.3)(0.5, 0.6, cosmo) == 0

    # source redshift inside shell
    with pytest.raises(NotImplementedError):
        probe_weights.Dirac_lensing(0.3)(0.2, 0.6, cosmo)


def test_continuous_to_dirac(cosmo):
    """
    Test if lensing weights for continuous n(z) converge towards single-source weights for n(z) ~ Dirac-delta.
    """

    for z_source, z_low, z_up in [
        (0.3, 0.1, 0.11),
        (0.8, 0.4, 0.41),
        (1.5, 0.3, 0.31),
        (1.5, 0.8, 0.81),
        (1.5, 1.4, 1.41),
    ]:
        # compute Dirac weight
        w_dirac = probe_weights.Dirac_lensing(z_source)(z_low, z_up, cosmo)

        # compute continuous weight with a tabulated function
        with mock.patch("numpy.genfromtxt") as genfromtxt:
            # tabulated delta function
            genfromtxt.return_value = np.array(
                [[z_source - 0.001, 0.0], [z_source, 1.0], [z_source + 0.001, 0.0]]
            )
            # get the weights
            cont_weights = probe_weights.Continuous_lensing(
                "None", z_lim_low=0, z_lim_up=2
            )

        w_cont = cont_weights(z_low, z_up, cosmo)
        print(w_cont)

        assert (w_dirac - w_cont) / w_cont < 0.01

        # compute continuous weight with a tabulated function
        # tabulated delta function
        z_dist = np.array(
            [[z_source - 0.001, 0.0], [z_source, 1.0], [z_source + 0.001, 0.0]]
        )
        # get the weights
        cont_weights = probe_weights.Continuous_lensing(z_dist, z_lim_low=0, z_lim_up=2)

        w_cont = cont_weights(z_low, z_up, cosmo)
        print(w_cont)

        assert (w_dirac - w_cont) / w_cont < 0.01

        # compute continous weights with gaussian delta dist
        n_of_z = stats.norm(
            loc=z_source, scale=0.005
        ).pdf  # set n(z) interpolator to approximate Dirac
        # get the weights
        cont_weights = probe_weights.Continuous_lensing(n_of_z, z_lim_low=0, z_lim_up=2)
        w_cont = cont_weights(z_low, z_up, cosmo)
        assert (w_dirac - w_cont) / w_cont < 0.01

        n_of_z = stats.norm(
            loc=z_source, scale=0.5
        ).pdf  # set n(z) interpolator to approximate Dirac
        # get the weights
        cont_weights = probe_weights.Continuous_lensing(n_of_z, z_lim_low=0, z_lim_up=2)
        cont_weights_fast = probe_weights.Continuous_lensing(
            n_of_z, z_lim_low=0, z_lim_up=2, fast_mode=True
        )
        w_cont = cont_weights(z_low, z_up, cosmo)
        w_cont_fast = cont_weights_fast(z_low, z_up, cosmo)

        assert (w_cont_fast - w_cont) / w_cont < 0.001


def test_dirac_to_continuous(cosmo):
    """
    Test if lensing weights for a continuous n(z) can be approximated by many single-source weights with source
    redshifts sampled from n(z).
    """

    # define n(z)
    mu = 0.6
    std = 0.1
    nz = stats.norm(loc=mu, scale=std)

    # define redshift interval to test
    z_low = 0.3
    z_up = 0.31

    # compute continuous lensing weight
    cont_weights = probe_weights.Continuous_lensing(nz.pdf, z_lim_low=0, z_lim_up=2)

    w_cont = cont_weights(z_low, z_up, cosmo)

    # sample source redshifts
    zs_source = nz.rvs(size=1000)
    zs_source[(zs_source > z_low) & (zs_source < z_up)] = 0

    # compute single-source weights
    w_dirac = 0

    for i, z_source in enumerate(zs_source):
        w_dirac += probe_weights.Dirac_lensing(z_source)(z_low, z_up, cosmo)

    w_dirac /= zs_source.size

    # compare
    assert (w_dirac - w_cont) / w_cont < 0.01


def test_kappa_prefactor(cosmo):
    """
    Test the computation of the prefactor to convert to convergence.
    """
    n_pix = 17395392
    n_particles = 1024**3
    boxsize = 6
    f = probe_weights.kappa_prefactor(n_pix, n_particles, boxsize, cosmo)
    assert "{:.18f}".format(f) == "0.001595227993431627"


def test_delta_prefactor(cosmo):
    """
    Test the computation of the prefactor to convert to clustering.
    """
    n_pix = 17395392
    n_particles = 1024**3
    boxsize = 1000
    delta_prefactor_value = probe_weights.delta_prefactor(
        n_pix, n_particles, boxsize, cosmo
    )
    assert "{:.14f}".format(delta_prefactor_value) == "234.45443760018043"


def test_NLA_alone(cosmo):
    # define n(z)
    mu = 0.6
    std = 0.1
    nz = stats.norm(loc=mu, scale=std)

    # define redshift interval to test
    z_low = 0.3
    z_up = 0.31

    # check that simple IA without redshift dependence works
    cont_weights = probe_weights.Continuous_intrinsic_alignment(
        nz.pdf, z_lim_low=0, z_lim_up=2, IA=1, eta=0.0, z_0=0.0
    )
    w_cont_IA = cont_weights(z_low, z_up, cosmo)

    assert w_cont_IA is not None

    # check that IA with redshift dependence works
    cont_weights = probe_weights.Continuous_intrinsic_alignment(
        nz.pdf, z_lim_low=0, z_lim_up=2, IA=1, eta=1.0, z_0=0.5
    )
    w_cont_IA = cont_weights(z_low, z_up, cosmo)

    assert w_cont_IA is not None


def test_clustering(cosmo):
    nz_arr = np.array([[0, 1], [1, 2], [2, 1], [3, 0]])
    lin_bias = 1.5
    cc = probe_weights.Continuous_clustering(nz_arr)

    assert cc is not None
    assert cc.z_lim_low == 0

    z_low, z_up = 0.5, 1.5
    weight = cc(z_low, z_up, lin_bias, cosmo)

    assert weight is not None
    assert isinstance(weight, float)

    cc_shift = probe_weights.Continuous_clustering(nz_arr, shift_nz=0.5)
    weight_shift = cc_shift(z_low, z_up, lin_bias, cosmo)

    assert weight_shift is not None
    assert isinstance(weight_shift, float)
    assert weight_shift != weight


def test_F_NLA_model(cosmo):
    z = np.linspace(0, 2, 10)
    IA = 0
    eta = -0.5
    z_0 = 0.62

    # Check if F_NLA_model returns zero when IA is zero
    F_NLA_values_zero_IA = np.array(
        [probe_weights.F_NLA_model(zi, IA, eta, z_0, cosmo) for zi in z]
    )
    assert np.all(F_NLA_values_zero_IA == 0)

    IA = 0.5

    # Check if F_NLA_model returns correct values in ther case IA amplitude is non-zero
    F_NLA_values_nonzero_IA = np.array(
        [probe_weights.F_NLA_model(zi, IA, eta, z_0, cosmo) for zi in z]
    )
    NLA_vals_test = [
        -0.00264935,
        -0.00268902,
        -0.0027726,
        -0.00287999,
        -0.00299973,
        -0.00312521,
        -0.00325266,
        -0.00337990,
        -0.00350571,
        -0.00362942,
    ]

    print(F_NLA_values_nonzero_IA)
    assert (
        all(np.isclose(F_NLA_values_nonzero_IA, NLA_vals_test, atol=0.0, rtol=1e-4))
        is True
    )
