import numpy as np
from scipy import special, optimize


def get_jl(x, ell):
    """
    Returns the spherical bessel function at x for mode ell.

    :param x: x coordinate.
    :type x: float
    :param ell: Desired spherical Bessel mode.
    :type ell: int
    :return: Spherical Bessel Function value at x for mode ell.
    :rtype: float
    """
    return special.spherical_jn(ell, x)


def get_der_jl(x, ell):
    """
    Returns the spherical bessel function derivative at x for mode ell.

    :param x: x coordinate.
    :type x: float
    :param ell: Desired spherical Bessel mode.
    :type ell: int
    :return: Derivative of the Spherical Bessel Function value at x for mode ell.
    :rtype: float
    """
    return special.spherical_jn(ell, x, derivative=True)


def get_qln(ell, nmax, nstop=100, zerolminus2=None, zerolminus1=None):
    """
    Returns the zeros of the spherical Bessel function. Begins by assuming
    that the zeros of the spherical Bessel function for l lie exactly between
    the zeros of the Bessel function between l and l+1. This allows us to use
    scipy's jn_zeros function. However, this function fails to return for high n.
    To work around this we estimate the first 100 zeros using scipy's jn_zero
    function and then iteratively find the roots of the next zero by assuming the
    next zero occurs pi away from the last one. Brent's method is then used to
    find a zero between pi/2 and 3pi/2 from the last zero.

    :param ell: Desired spherical Bessel mode.
    :type ell: int
    :param nmax: The maximum zero found for the spherical Bessel Function.
    :type nmax: int
    :param nstop: For n <= nstop we use scipy's jn_zeros to guess where the first nstop zeros are. These estimates are improved using Brent's method and assuming zeros lie between -pi/2 and pi/2 from the estimates.
    :type nstop: int
    :return: Derivative of the Spherical Bessel Function value at x for mode ell.
    :rtype: float
    """
    if nmax <= nstop:
        nstop = nmax
    if zerolminus2 is None and zerolminus1 is None:
        z1 = special.jn_zeros(ell, nstop)
        z2 = special.jn_zeros(ell + 1, nstop)
        zeros_approx = np.ndarray.tolist(0.5 * (z1 + z2))
        zeros = []
        for i in range(0, len(zeros_approx)):
            a = zeros_approx[i] - 0.5 * np.pi
            b = zeros_approx[i] + 0.5 * np.pi
            val = optimize.brentq(get_jl, a, b, args=(ell))
            zeros.append(val)
        if nstop != nmax:
            n = nstop
            while n < nmax:
                zero_last = zeros[-1]
                a = zero_last + 0.5 * np.pi
                b = zero_last + 1.5 * np.pi
                val = optimize.brentq(get_jl, a, b, args=(ell))
                zeros.append(val)
                n += 1
    else:
        dz = zerolminus1 - zerolminus2
        z1 = zerolminus1 + 0.5 * dz
        z2 = zerolminus2 + 1.5 * dz
        zeros_approx = np.ndarray.tolist(0.5 * (z1 + z2))
        zeros = []
        for i in range(0, len(zeros_approx)):
            a = zeros_approx[i] - 0.5 * np.pi
            b = zeros_approx[i] + 0.5 * np.pi
            val = optimize.brentq(get_jl, a, b, args=(ell))
            zeros.append(val)
    zeros = np.array(zeros)
    return zeros


def get_der_qln(ell, nmax, nstop=100, zerolminus2=None, zerolminus1=None):
    """
    Returns the zeros of the spherical Bessel function derivative. Begins by
    assuming that the zeros of the spherical Bessel function for l lie exactly
    between the zeros of the Bessel function between l and l+1. This allows us
    to use scipy's jn_zeros function. However, this function fails to return for
    high n. To work around this we estimate the first 100 zeros using scipy's
    jn_zero function and then iteratively find the roots of the next zero by
    assuming the next zero occurs pi away from the last one. Brent's method is
    then used to find a zero between pi/2 and 3pi/2 from the last zero.

    :param ell: Desired spherical Bessel mode.
    :type ell: int
    :param nmax: The maximum zero found for the spherical Bessel Function.
    :type nmax: int
    :param nstop: For n <= nstop we use scipy's jn_zeros to guess where the first nstop zeros are. These estimates are improved using Brent's method and assuming zeros lie between -pi/2 and pi/2 from the estimates.
    :type nstop: int
    :return: Derivative of the Spherical Bessel Function value at x for mode ell.
    :rtype: float
    """
    if nmax <= nstop:
        nstop = nmax
    if zerolminus2 is None and zerolminus1 is None:
        z1 = special.jnp_zeros(ell, nstop)
        z2 = special.jnp_zeros(ell + 1, nstop)
        zeros_approx = np.ndarray.tolist(0.5 * (z1 + z2))
        zeros = []
        for i in range(0, len(zeros_approx)):
            a = zeros_approx[i] - 0.5 * np.pi
            b = zeros_approx[i] + 0.5 * np.pi
            val = optimize.brentq(get_der_jl, a, b, args=(ell))
            zeros.append(val)
        if nstop != nmax:
            n = nstop
            while n < nmax:
                zero_last = zeros[-1]
                a = zero_last + 0.5 * np.pi
                b = zero_last + 1.5 * np.pi
                val = optimize.brentq(get_der_jl, a, b, args=(ell))
                zeros.append(val)
                n += 1
    else:
        dz = zerolminus1 - zerolminus2
        z1 = zerolminus1 + 0.5 * dz
        z2 = zerolminus2 + 1.5 * dz
        zeros_approx = np.ndarray.tolist(0.5 * (z1 + z2))
        zeros = []
        for i in range(0, len(zeros_approx)):
            a = zeros_approx[i] - 0.5 * np.pi
            b = zeros_approx[i] + 0.5 * np.pi
            val = optimize.brentq(get_der_jl, a, b, args=(ell))
            zeros.append(val)
    zeros = np.array(zeros)
    return zeros
