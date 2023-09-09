# Copyright (C) 2022 ETH Zurich, Institute for Particle Physics and Astrophysics
# Author: Alexander Reeves, Raphael Sgier and Jörg Herbel
import numpy as np
import scipy.integrate as integrate
from scipy.interpolate import interp1d

from UFalcon import utils, constants


class Continuous:
    def __init__(
        self,
        n_of_z,
        interpolation_kind="linear",
        z_lim_low=0,
        z_lim_up=None,
        shift_nz=0.0,
    ):
        """
        Constructor.
        :param n_of_z: Either path to file containing n(z), assumed to be a text file readable with numpy with the
                        first column containing z and the second column containing n(z), a 2D array of shape (N, 2) or a callable
                        that is directly a redshift distribution.
        :type n_of_z: str or ndarray
        :param interpolation_kind: This argument specifies type of interpolation used, if the redshift distribution is
                                   read from a file. It is directly forwarded to scipy.interpolate.interp1d and
                                   defaults to 'linear'
        :type interpolation_kind: str
        :param z_lim_low: lower integration limit to use for n(z) normalization, default: 0
        :type z_lim_low: float
        :param z_lim_up: upper integration limit to use for n(z) normalization, default: last z-coordinate in n(z) file
        :type z_lim_up: float
        :param shift_nz: Can shift the n(z) function by some redshift (intended for easier implementation of photo z bias)
        :type shift_nz: float
        """

        # we handle the redshift dist depending on its type
        if callable(n_of_z):
            if z_lim_up is None:
                raise ValueError(
                    "An upper bound of the redshift normalization has to be defined if n_of_z is not a "
                    "tabulated function."
                )

            self.nz_intpt = n_of_z
            # set the integration limit and integration points
            self.lightcone_points = None
            self.limit = 1000
        else:
            # read from file
            if isinstance(n_of_z, str):
                nz = np.genfromtxt(n_of_z)
            elif isinstance(n_of_z, np.ndarray):
                nz = n_of_z.copy()
            else:
                raise ValueError("n_of_z type not understood...")

            # get the upper bound if necessary
            if z_lim_up is None:
                z_lim_up = nz[-1, 0]

            # get the callable function
            self.nz_intpt = interp1d(
                nz[:, 0] - shift_nz,
                nz[:, 1],
                bounds_error=False,
                fill_value=0.0,
                kind=interpolation_kind,
            )

            # points for integration
            self.lightcone_points = nz[
                np.logical_and(z_lim_low < nz[:, 0], nz[:, 0] < z_lim_up), 0
            ]

            # check if there are any points remaining for the integration
            if len(self.lightcone_points) == 0:
                self.lightcone_points = None
                self.limit = 1000
            else:
                self.limit = 10 * len(self.lightcone_points)

        self.z_lim_up = z_lim_up
        self.z_lim_low = z_lim_low

        # Normalization
        self.nz_norm = integrate.quad(
            lambda x: self.nz_intpt(x),
            z_lim_low,
            self.z_lim_up,
            points=self.lightcone_points,
            limit=self.limit,
        )[0]

    def get_weight_norm(self, z_low, z_up, cosmo):
        """
        Computes the normalization for lensing integrals.

        :param z_low: lower end of the redshift interval
        :type z_low: float
        :param z_up: upper end of the redshift interval
        :type z_up: float
        """

        # This is essentially the numerator in the expression in eqt. 3.4 of https://arxiv.org/pdf/2007.05735.pdf
        norm1 = utils.dimensionless_comoving_distance(z_low, z_up, cosmo) * self.nz_norm

        # Multiplied by the comoving distance to the shell squared as that is not included in kappa prefactor (Eqn 3.3 https://arxiv.org/pdf/2007.05735.pdf)
        norm2 = (
            utils.dimensionless_comoving_distance(0.0, (z_low + z_up) / 2.0, cosmo)
            ** 2.0
        )

        return norm1 * norm2


class Continuous_lensing(Continuous):
    """
    Computes the lensing weights for a continuous, user-defined n(z) distribution.
    The weight should then be multiplied by kappa_prefactor.
    """

    def __init__(
        self,
        n_of_z,
        interpolation_kind="linear",
        z_lim_low=0,
        z_lim_up=None,
        shift_nz=0.0,
        fast_mode=False,
        fast_mode_num_points_1d=13,
        fast_mode_num_points_2d=512,
    ):
        super().__init__(n_of_z, interpolation_kind, z_lim_low, z_lim_up, shift_nz)

        self.fast_mode = fast_mode
        self.fast_mode_num_points_1d = fast_mode_num_points_1d
        self.fast_mode_num_points_2d = fast_mode_num_points_2d

    def __call__(self, z_low, z_up, cosmo):
        """
        Computes the lensing weights for the redshift interval [z_low, z_up].

        :param z_low: lower end of the redshift interval
        :type z_low: float
        :param z_up: upper end of the redshift interval
        :type z_up: float
        :param cosmo: Astropy.Cosmo instance, controls the cosmology used
        :type cosmo: Astropy cosmology instance
        :return: lensing weight
        :rtype: float
        """

        norm = self.get_weight_norm(z_low, z_up, cosmo)

        # lensing weights
        if self.fast_mode:
            z_vals, dz = np.linspace(
                z_low, z_up, self.fast_mode_num_points_1d, retstep=True
            )
            quad_y_vals = self._integrand_1d(
                z_vals, cosmo
            )  # evaluate the integrand at these values
            numerator = integrate.simps(quad_y_vals, dx=dz, axis=0)

        else:
            numerator = integrate.quad(self._integrand_1d, z_low, z_up, args=(cosmo,))[
                0
            ]

        return numerator / norm

    def _integrand_2d(self, y, x, cosmo):
        """
        The 2d integrand of the continous lensing weights.

        :param y: float, redhsift that goes into the n(z)
        :param x: float, redshift for the Dirac part
        :param cosmo: Astropy.Cosmo instance, controls the cosmology used
        :type cosmo: Astropy cosmology instance
        :return: the 2d integrand function
        :rtype: ndarray
        """
        # TODO: check the return types and test fast_mode further

        return (
            self.nz_intpt(y)
            * utils.dimensionless_comoving_distance(0, x, cosmo)
            * utils.dimensionless_comoving_distance(x, y, cosmo)
            * (1 + x)
            * cosmo.inv_efunc(x)
            / utils.dimensionless_comoving_distance(0, y, cosmo)
        )

    def _integrand_1d(self, x, cosmo):
        """
        Function that integrates out y from the 2d integrand.

        :param x: which redshift to evaluate
        :type x: float
        :param cosmo: Astropy.Cosmo instance, controls the cosmology used
        :type cosmo: Astropy cosmology instance
        :return: the 1d integrant at x
        :rtype: float
        """
        if self.fast_mode:

            def quad_y(x):
                x = np.atleast_1d(x)
                # we need to protect against under and overflow
                y_vals = np.geomspace(
                    np.maximum(x, 1e-4),
                    self.z_lim_up + 1e-12,
                    self.fast_mode_num_points_2d,
                )
                f_vals = np.nan_to_num(self._integrand_2d(y_vals, x, cosmo))
                return integrate.simps(f_vals, x=y_vals, axis=0)

        else:
            if self.lightcone_points is not None:
                # Points of the distribution specified to quad algorithm to improve accuracy
                points = self.lightcone_points[
                    np.logical_and(
                        self.z_lim_low < self.lightcone_points,
                        self.lightcone_points < self.z_lim_up,
                    )
                ]
                quad_y = lambda x: integrate.quad(  # noqa
                    lambda y: self._integrand_2d(y, x, cosmo),
                    x,
                    self.z_lim_up,
                    limit=self.limit,
                    points=points,
                )[
                    0
                ]  # noqa
            else:
                quad_y = lambda x: integrate.quad(  # noqa
                    lambda y: self._integrand_2d(y, x, cosmo),
                    x,
                    self.z_lim_up,
                    limit=self.limit,
                )[
                    0
                ]  # noqa

        return quad_y(x)


class Continuous_intrinsic_alignment(Continuous):
    """
    Computes the intrinsic alignment weights for a continuous, user-defined n(z) distribution.
    N.B: the weight should then be multiplied by delta_prefactor.
    """

    def __init__(
        self,
        n_of_z,
        interpolation_kind="linear",
        z_lim_low=0,
        z_lim_up=None,
        shift_nz=0.0,
        IA=1.0,
        eta=0.0,
        z_0=0.5,
    ):
        super().__init__(n_of_z, interpolation_kind, z_lim_low, z_lim_up, shift_nz)

        self.IA = IA
        self.eta = eta
        self.z_0 = z_0

    def __call__(self, z_low, z_up, cosmo):
        """
        Computes the IA weights for the redshift interval [z_low, z_up].

        :param z_low: lower end of the redshift interval
        :type z_low: float
        :param z_up: upper end of the redshift interval
        :type z_up: float
        :param cosmo: Astropy.Cosmo instance, controls the cosmology used
        :type cosmo: Astropy cosmology instance
        :return: lensing weight
        :rtype: float
        """

        norm = self.get_weight_norm(z_low, z_up, cosmo)

        numerator = w_IA(
            self.IA,
            self.eta,
            z_low,
            z_up,
            cosmo,
            self.nz_intpt,
            z_0=self.z_0,
            points=self.lightcone_points,
        )

        return numerator / norm


class Dirac_lensing:
    """
    Computes the lensing weights for a single-source redshift.
    """

    def __init__(self, z_source):
        """
        Constructor
        :param z_source: source redshift
        :type z_source: float
        """
        self.z_source = z_source

    def __call__(self, z_low, z_up, cosmo):
        """
        Computes the lensing weights for the redshift interval [z_low, z_up].

        :param z_low: lower end of the redshift interval
        :type z_low: float
        :param z_up: upper end of the redshift interval
        :type z_up: float
        :param cosmo: Astropy.Cosmo instance, Astropy.Cosmo instance, controls the cosmology used
        :type cosmo: Astropy cosmology instance
        :return: lensing weight
        :rtype: float
        """

        # source is below the shell --> zero weight
        if self.z_source <= z_low:
            w = 0

        # source is inside the shell --> error
        elif self.z_source < z_up:
            raise NotImplementedError(
                "Attempting to call UFalcon.lensing_weights.Dirac with z_low < z_source < z_up, "
                "this is not implemented"
            )

        # source is above the shell --> usual weight
        else:
            numerator = integrate.quad(self._integrand, z_low, z_up, args=(cosmo,))[0]

            norm = utils.dimensionless_comoving_distance(
                z_low, z_up, cosmo
            ) * utils.dimensionless_comoving_distance(0, self.z_source, cosmo)

            # Multiplied by the comoving distance to the shell squared as that is not included in kappa prefactor (Eqn 3.3 https://arxiv.org/pdf/2007.05735.pdf)
            norm *= (
                utils.dimensionless_comoving_distance(0.0, (z_low + z_up) / 2.0, cosmo)
                ** 2.0
            )

            w = numerator / norm

        return w

    def _integrand(self, x, cosmo):
        return (
            utils.dimensionless_comoving_distance(0, x, cosmo)
            * utils.dimensionless_comoving_distance(x, self.z_source, cosmo)
            * (1 + x)
            * cosmo.inv_efunc(x)
        )


class Continuous_clustering(Continuous):
    """
    Computes the clustering weights for a continuous, user-defined n(z) distribution.
    """

    def __init__(
        self,
        n_of_z,
        interpolation_kind="linear",
        z_lim_low=0,
        z_lim_up=None,
        shift_nz=0.0,
    ):
        """
        Constructor.

        :param n_of_z: Either path to file containing n(z), assumed to be a text file readable with numpy with the
                        first column containing z and the second column containing n(z), a 2D array of shape (N, 2) or a callable
                        that is directly a redshift distribution.
        :type n_of_z: str or ndarray
        :param interpolation_kind: This argument specifies type of interpolation used, if the redshift distribution is
                                   read from a file. It is directly forwarded to scipy.interpolate.interp1d and
                                   defaults to 'linear'
        :type interpolation_kind: str
        :param z_lim_low: lower integration limit to use for n(z) normalization, default: 0
        :type z_lim_low: float
        :param z_lim_up: upper integration limit to use for n(z) normalization, default: last z-coordinate in n(z) file
        :type z_lim_up: float
        :param shift_nz: Can shift the n(z) function by some redshift (intended for easier implementation of photo z bias)
        :type shift_nz: float
        """

        super().__init__(n_of_z, interpolation_kind, z_lim_low, z_lim_up, shift_nz)

    def __call__(self, z_low, z_up, lin_bias, cosmo):
        """
        Computes the lensing weights for the redshift interval [z_low, z_up].
        :param z_low: lower end of the redshift interval
        :type z_low: float
        :param z_up: upper end of the redshift interval
        :type z_up: float
        :param lin_bias: the linear bias for the galaxy clustering weight
        :type lin_bias: float
        :param cosmo: Astropy.Cosmo instance, Astropy.Cosmo instance, controls the cosmology used
        :type cosmo: Astropy cosmology instance
        :return: clustering weight
        :rtype: float
        """

        weight_clustering = (
            # utils.hubble((z_low + z_up) / 2.0, cosmo)
            cosmo.H((z_low + z_up) / 2.0).value
            * self.nz_intpt((z_low + z_up) / 2.0)
            * lin_bias
            * (
                1.0
                / utils.dimensionless_comoving_distance(
                    0.0, (z_low + z_up) / 2.0, cosmo
                )
                ** 2.0
            )
        )

        return weight_clustering / self.nz_norm


def kappa_prefactor(n_pix, n_particles, boxsize, cosmo):
    """
    Computes the prefactor to transform from number of particles to convergence, see https://arxiv.org/abs/0807.3651,
    eq. (A.1).

    :param n_pix: number of healpix pixels used
    :type n_pix: int
    :param n_particles: number of particles
    :type n_particles: int
    :param boxsize: size of the box in Gigaparsec
    :type boxsize: float
    :param cosmo: Astropy.Cosmo instance, Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: convergence prefactor
    :rtype: float
    """

    convergence_factor = (
        (3.0 * cosmo.Om0 / 2.0)
        * (n_pix / (4.0 * np.pi))
        * (cosmo.H0.value / constants.c) ** 3
        * (boxsize * 1000.0) ** 3
        / n_particles
    )

    return convergence_factor


def delta_prefactor(n_pix, n_particles, boxsize, cosmo):
    """
    Computes the prefactor to transform from number of particles to clustering see: https://arxiv.org/pdf/2007.05735.pdf.

    :param n_pix: number of healpix pixels used
    :type n_pix: int
    :param n_particles: number of particles
    :type n_particles: int
    :param boxsize: size of the box in Gigaparsec
    :type boxsize: float
    :param cosmo: Astropy.Cosmo instance, Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: clustering prefactor
    :rtype: float
    """

    clustering_factor = (
        (n_pix / (4.0 * np.pi))
        * (cosmo.H0.value) ** 2.0
        / (constants.c) ** 3
        * (boxsize * 1000.0) ** 3
        / n_particles
    )

    return clustering_factor


def kappa_prefactor_nosim(cosmo):
    """
    Computes the simualtion independent prefactor to transform to convergence, see https://arxiv.org/abs/0807.3651,
    eq. (A.1), cosmology dependent part.
    This function does not include the factor depending on box size, number of particles and number of pixels.
    Remember to also multiply by this using the function sim_spec_prefactor.

    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: cosmology dependent convergence prefactor
    :rtype: float
    """

    # convergence_factor = (3.0 * cosmo.Om0 / 2.0) * (n_pix / (4.0 * np.pi)) * (cosmo.H0.value / constants.c) ** 3 * (boxsize * 1000.0) ** 3 / n_particles
    # * (n_pix * (boxsize * 1000.0) ** 3 / n_particles

    convergence_factor = (
        (3.0 * cosmo.Om0 / 2.0)
        / (4.0 * np.pi)
        * (cosmo.H0.value / constants.c) ** 3
        / (cosmo.H0.value / 100) ** 3
    )

    return convergence_factor


def delta_prefactor_nosim(cosmo):
    """
    Computes the simualtion independent prefactor to transform to clustering see: https://arxiv.org/pdf/2007.05735.pdf, cosmology dependent part.
    This function does not include the factor depending on box size, number of particles and number of pixels.
    Remember to also multiply by this using the function sim_spec_prefactor.

    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: cosmology dependent clustering prefactor
    :rtype: float
    """

    # clustering_factor = (n_pix / (4.0 * np.pi)) * (cosmo.H0.value)**2. / (constants.c) ** 3 * (boxsize * 1000.0) ** 3 / n_particles
    # n_pix * (boxsize * 1000.0) ** 3 / n_particles

    clustering_factor = (
        (1 / (4.0 * np.pi))
        * (cosmo.H0.value) ** 2.0
        / (constants.c) ** 3
        / (cosmo.H0.value / 100) ** 3
    )

    return clustering_factor


def sim_spec_prefactor(n_pix, box_size, n_particles):
    """
    Calculate the prefactors depending on the box size, number of particles and number of pixels.
    See https://arxiv.org/abs/0807.3651, https://arxiv.org/pdf/2007.05735.pdf.
    This should be used together with delta_prefactor and kappa_prefactor.

    :param n_pix: number of healpix pixels used
    :type n_pix: int
    :param boxsize: size of the box in Gigaparsec
    :type boxsize: float
    :param n_particles: number of particles
    :type n_particles: int
    :return prefactor: prefactor to use
    :rtype: float
    """

    return n_pix * box_size**3 / n_particles


def F_NLA_model(z, IA, eta, z_0, cosmo):
    """
    Calculates the NLA kernel used to calculate the IA shell weight.

    :param z: Redshift where to evaluate
    :type z: float
    :param IA: Galaxy intrinsic alignment amplitude
    :type IA: float
    :param eta: Galaxy Intrinsic alignment redshift dependence
    :type eta: float
    :param z_0: Pivot parameter for the redshift dependence of the NLA model
    :type z_0: float
    :param cosmo: Astropy.Cosmo instance, Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :return: NLA kernel at redshift z
    :rtype: float
    """
    OmegaM = cosmo.Om0
    H0 = cosmo.H0.value

    # growth factor calculation
    growth = lambda a: 1.0 / (a * cosmo.H(1.0 / a - 1.0).value) ** 3.0  # noqa
    a = 1.0 / (1.0 + z)

    g = 5.0 * OmegaM / 2.0 * cosmo.efunc(z) * integrate.quad(growth, 0, a)[0]

    # Calculate the growth factor today
    g_norm = 5.0 * OmegaM / 2.0 * integrate.quad(growth, 0, 1)[0]

    # divide out a
    g = g / g_norm

    # critical density today = 3*H^2/(8piG)
    rho_c = cosmo.critical_density0.to("Msun Mpc^-3").value

    # Proportionality constant Msun^-1 Mpc^3
    C1 = 5e-14 / (H0 / 100.0) ** 2

    # redshift dependece term
    red_dep = ((1 + z) / (1 + z_0)) ** eta

    return -IA * rho_c * C1 * OmegaM / g * red_dep


def w_IA(IA, eta, z_low, z_up, cosmo, nz_intpt, z_0=0.5, points=None):
    """
    Calculates the weight per slice for the NLA model given a
    distribution of source redshifts n(z).

    :param IA: Galaxy intrinsic alignments amplitude
    :type IA: float
    :param eta: Galaxy Intrinsic alignment redshift dependence
    :type eta: float
    :param z_low: Lower redshift limit of the shell
    :type z_low: float
    :param z_up: Upper redshift limit of the shell
    :type z_up: float
    :param cosmo: Astropy.Cosmo instance, Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :param nz_intpt: nz function
    :type nz_intp: callable
    :param z_0: Pivot parameter for the redshift dependence of the NLA model
    :type z_0: float
    :param points: array-like, Points in redshift where integrand is evaluated (used for better numerical integration), can be None
    :type points: ndarray
    :return: Shell weight for NLA model
    :rtype: float
    """

    def f(x):
        return F_NLA_model(x, IA, eta, z_0, cosmo) * nz_intpt(x)

    if points is not None:
        break_points = points[np.logical_and(z_low < points, points < z_up)]

        try:
            dbl = integrate.quad(
                f, z_low, z_up, points=break_points, limit=10 * len(break_points)
            )[0]
        except Exception as err:
            print(err)
            dbl = integrate.quad(f, z_low, z_up)[0]

    else:
        dbl = integrate.quad(f, z_low, z_up)[0]

    return dbl
