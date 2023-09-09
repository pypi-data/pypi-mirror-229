# Copyright (C) 2020 ETH Zurich, Institute for Particle Physics and Astrophysics
# Author: Raphael Sgier and Jörg Herbel

import numpy as np
from scipy import integrate, interpolate
import healpy as hp
from UFalcon import constants

splines = {}


def dimensionless_comoving_distance(z_low, z_up, cosmo):
    """
    Computes the dimensionless comoving distance between two redshifts. Scalar input only.
    Legacy code - see updated function

    :param z_low: lower redshift
    :type z_low: ndarray
    :param z_up: upper redshift, must have same shape as z_low
    :type z_up: ndarray
    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: dimensionless comoving distance
    :rtype: ndarray
    """
    dimless_com = (
        (cosmo.comoving_distance(z_up) - cosmo.comoving_distance(z_low))
        * cosmo.H0
        / constants.c
    )

    return dimless_com.value


def dimensionless_comoving_distance_old(
    z_low, z_up, cosmo, fast_mode=0, z_max_interp=10
):
    """
    Computes the dimensionless comoving distance between two redshifts. Scalar input only.
    Legacy code - see updated function

    :param z_low: lower redshift
    :type z_low: ndarray
    :param z_up: upper redshift, must have same shape as z_low
    :type z_up: ndarray
    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :param fast_mode: Instead of using quad from scipy, use a simple romberg integration rule (this works here because
                      we know that the dimless com behaves and is differentiable)
    :type fast_mode: bool
    :return: dimensionless comoving distance
    :rtype: ndarray
    """
    if fast_mode == 1:
        integration_range, dz = np.linspace(z_low, z_up, 32 + 1, retstep=True)
        dimless_com = integrate.romb(cosmo.inv_efunc(integration_range), dx=dz, axis=0)

    elif fast_mode == 2:
        prec_required = 1e-6
        from scipy.interpolate import CubicSpline

        if z_max_interp not in splines:
            z = np.arange(0, z_max_interp, 0.005)
            splines[z_max_interp] = CubicSpline(z, cosmo.inv_efunc(z))
            dimless_com_spline = splines[z_max_interp].integrate(a=z_low, b=z_up)
            dimless_com_quad = integrate.quad(cosmo.inv_efunc, z_low, z_up)[0]
            frac_diff = np.abs(dimless_com_spline - dimless_com_quad) / dimless_com_quad
            if frac_diff > prec_required:
                raise Exception(
                    f"spline acceleration of integrals has bad precision frac_diff={frac_diff}, required={prec_required}"
                )

        if np.any(z_up > z_max_interp):
            raise Exception("inv_efunc speed up z_max not sufficient")

        dimless_com = splines[z_max_interp].integrate(
            a=z_low, b=z_up
        )  # 24.4 ms per hit

    else:
        dimless_com = integrate.quad(cosmo.inv_efunc, z_low, z_up)[
            0
        ]  # 753.0 ms per hit

    return dimless_com


def comoving_distance(z_low, z_up, cosmo):
    """
    Computes the comoving distance between two redshifts. Scalar input only.

    :param z_low: lower redshift
    :type z_low: ndarray
    :param z_up: upper redshift, must have same shape as z_low
    :type z_up: ndarray
    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: comoving distance
    :rtype: ndarray
    """
    com = (
        dimensionless_comoving_distance(z_low, z_up, cosmo)
        * constants.c
        / cosmo.H0.value
    )
    return com


def a_of_r(r, cosmo):
    """
    Computes the scale factor at a given comoving distance in MpC. Scalar or vector input.
    Note only supports calculation up to redshift z=12.

    :param r: input comoving distance in MpC at which scale factor should we found
    :type r: float
    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: scale factor
    :rtype: float
    """

    zmax = 12  # maximum redshift we will interpolate to
    a_min = 1 / (1 + zmax)

    a_array = np.logspace(np.log10(a_min), 0, 2000)
    # This will span a sufficient redshift range but can we include an accuracy test
    z_array = 1 / a_array - 1
    r_array = np.array(
        [comoving_distance(0, z_array_elem, cosmo) for z_array_elem in z_array]
    )
    interp = interpolate.interp1d(r_array, a_array, kind="cubic")

    return interp(r)


def growth_z(z, cosmo):
    """
    Computes the normalized linear growth factor as a function of redshift (i.e. D(z)). Scalar input only.
    Normalized means D(z)=1 at z=0.

    :param z: redshift or array of redshifts at which growth factor should be calculated
    :type z: ndarray
    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: linear growth factor at z i.e. D(z)
    :rtype: ndarray
    """

    # handle correctly if scalar input
    z = np.atleast_1d(z)

    OmegaM = cosmo.Om0
    # growth factor calculation
    growth = lambda a: 1.0 / (a * cosmo.H(1.0 / a - 1.0).value) ** 3.0  # noqa

    g_array = np.zeros_like(z)

    for i, z in enumerate(z):
        a = 1.0 / (1.0 + z)  # convert input redshift to scale factor
        g = 5.0 * OmegaM / 2.0 * cosmo.efunc(z) * integrate.quad(growth, 0, a)[0]

        # Calculate the growth factor today
        g_norm = 5.0 * OmegaM / 2.0 * integrate.quad(growth, 0, 1)[0]

        # divide out to normalise growth factor
        g_array[i] = g / g_norm

    return g_array


def kappa_to_gamma(kappa_map, lmax=None, use_pixel_weights=True):
    """
    Computes a gamma_1- and gamma_2-map from a kappa-map, s.t. the kappa TT-spectrum equals the gamma EE-spectrum.

    :param kappa_map: kappa map as a HEALPix array
    :type kappa_map: ndarray
    :param lmax: maximum multipole to consider, default: 3 * nside - 1
    :type lmax: float
    :param use_pixel_weights: Use pixelweights for the map2alm transformation. This delivers the most accurate
                              transform according to healpy, but requires the pixel weights, which will be downloaded
                              automatically.
    :type use_pixel_weights: bool
    :return: gamma_1- and gamma_2-map
    :rtype: ndarray
    """

    nside = hp.npix2nside(kappa_map.size)

    if lmax is None:
        lmax = 3 * nside - 1

    kappa_alm = hp.map2alm(kappa_map, lmax=lmax, use_pixel_weights=use_pixel_weights)
    ell = hp.Alm.getlm(lmax)[0]

    # Add the appropriate factor to the kappa_alm
    fac = np.where(
        np.logical_and(ell != 1, ell != 0),
        -np.sqrt(((ell + 2.0) * (ell - 1)) / ((ell + 1) * ell)),
        0,
    )

    kappa_alm *= fac
    t, q, u = hp.alm2map(
        [np.zeros_like(kappa_alm), kappa_alm, np.zeros_like(kappa_alm)], nside=nside
    )

    return q, u
