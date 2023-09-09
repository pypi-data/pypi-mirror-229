# Copyright (C) 2022 ETH Zurich, Institute for Particle Physics and Astrophysics
# Author: Alexander Reeves and Luis Marchado

import numpy as np
from scipy import integrate, interpolate
import healpy as hp
import subprocess
import os
from astropy import units
from UFalcon import bessel, utils, constants
from scipy.interpolate import interp1d

import logging

healpy_logger = logging.getLogger("healpy")
healpy_logger.setLevel(logging.ERROR)


class SphericalBesselISW:

    """
    Modified version of https://github.com/knaidoo29/pyGenISW/.
    Class for computing the ISW using spherical Bessel Transforms from maps
    of the density contrast given in redshift slices.

    :param cosmo: Astropy.Cosmo instance, controls the cosmology used when computing linear growth
    :type cosmo: Astropy cosmology instance
    """

    def __init__(self, cosmo):
        self.Tcmb = cosmo.Tcmb0.value
        self.temp_path = None
        self.sbt_zmin = None
        self.sbt_zmax = None
        self.sbt_zedge_min = None
        self.sbt_zedge_max = None
        self.slice_in_range = None
        self.sbt_rmin = None
        self.sbt_rmax = None
        self.sbt_kmin = None
        self.sbt_kmax = None
        self.sbt_lmax = None
        self.sbt_nmax = None
        self.sbt_redge_min = None
        self.sbt_redge_max = None
        self.uselightcone = None
        self.temp_path = None
        self.boundary_conditions = None
        self.sim_dens = None

        self.alpha = None

        self.cosmo = cosmo

        self.H0 = cosmo.H0.value
        self.Om0 = cosmo.Om0

    def calc_table(
        self,
        zmin=0.0,
        zmax=10.0,
        zbin_num=1000,
        zbin_mode="linear",
        alpha=0.55,
        kind="cubic",
    ):
        """
        Constructs table of cosmological linear functions to be interpolated for speed.

        :param zmin: Minimum redshift for tabulated values of the linear growth functions.
        :type zmin: float
        :param zmax: Maximum redshift for tabulated values of the linear growth functions.
        :type zmax: float
        :param zbin_num: Number of redshift values to compute the growth functions.
        :type zbin_num: int
        :param zbin_mode: Redshift binning, either linear or log of 1+z.
        :type zbin_mode: str
        :param alpha: The power in the approximation to f(z) = Omega_m(z)**alpha.
        :type alpha: float
        :param kind: The kind of interpolation used by the created interpolation functions as function of z and r.
        :type kind: str
        :return: None
        :rtype: None
        """
        # store some variables for table generation
        self.zmin = zmin  # minimum redshift for table
        self.zmax = zmax  # maximum redshift for table
        self.zbin_num = zbin_num  # size of array
        self.zbin_mode = zbin_mode  # linear or log
        self.f_alpha = alpha  # for fz approximation
        # construct z array
        if zbin_mode == "linear":
            self.z_table = np.linspace(self.zmin, self.zmax, self.zbin_num)
        else:
            self.z_table = (
                np.logspace(np.log10(zmin + 1.0), np.log10(zmax + 1.0), zbin_num) - 1.0
            )
        # constructs table of linear growth functions rz, Hz, Dz and fz
        self.rz_table = np.array(
            [self.get_rz_no_interp(z_val) for z_val in self.z_table]
        )
        self.Hz_table = np.array([self.get_Hz(z_val) for z_val in self.z_table])
        self.Dz_table = self.get_Dz(self.z_table)
        self.fz_table = self.get_fz_numerical(self.z_table[::-1], self.Dz_table[::-1])[
            ::-1
        ]

        # constructs callable interpolators for rz, Hz, Dz and fz
        self.rz_interpolator = interp1d(self.z_table, self.rz_table, kind=kind)
        self.Hz_interpolator = interp1d(self.z_table, self.Hz_table, kind=kind)
        self.Dz_interpolator = interp1d(self.z_table, self.Dz_table, kind=kind)
        self.fz_interpolator = interp1d(self.z_table, self.fz_table, kind=kind)
        # constructs callable interpolators for rz, Hz, Dz and fz as a function of r
        self.zr_interpolator = interp1d(self.rz_table, self.z_table, kind=kind)
        self.Hr_interpolator = interp1d(self.rz_table, self.Hz_table, kind=kind)
        self.Dr_interpolator = interp1d(self.rz_table, self.Dz_table, kind=kind)
        self.fr_interpolator = interp1d(self.rz_table, self.fz_table, kind=kind)

    def setup(
        self,
        zmin,
        zmax,
        zedge_min,
        zedge_max,
        temp_path,
        alpha,
        kmin=None,
        kmax=0.1,
        lmax=None,
        nmax=None,
        uselightcone=True,
        boundary_conditions="normal",
    ):
        """
        Configure instance for future computations.

        :param zmin: Minimum redshift for spherical Bessel transform.
        :type zmin: float
        :param zmax: Maximum redshift for spherical Bessel transform.
        :type zmax: float
        :param zedge_min: Minimum redshift edge for each slice.
        :type zedge_min: array
        :param zedge_max: Maximum redshift edge for each slice.
        :type zedge_max: array
        :param kmin: Minium Fourier mode to consider.
        :type kmin: float
        :param kmax: Maximum Fourier mode to consider.
        :type kmax: float
        :param lmax: Maximum l mode to compute to, if None will be computed based on kmax.
        :type lmax: int
        :param nmax: Maximum n mode to compute to, if None will be computed based on kmax.
        :type nmax: int
        :param uselightcone: True if density contrast maps are given as a lightcone and not all at redshift 0.
        :type uselightcone: bool
        :param boundary_conditions: Setting for boundary conditions used. This can assume the following values:
            - normal: boundaries where spherical bessel function is zero.
            - derivative: boundaries where the derivative of the spherical Bessel function is zero.
        :type boundary_conditions: str
        :return: None
        :rtype: None
        """
        if zedge_min.min() > zmin:
            print(
                "zmin given,",
                zmin,
                "is smaller than the zmin of the redshift slices. Converting zmin to zmin_edges.zmin().",
            )
            self.sbt_zmin = zedge_min.min()
        else:
            self.sbt_zmin = zmin
        if zedge_max.max() < zmax:
            print(
                "zmax given,",
                zmax,
                "is larger than the zmax of the redshift slices. Converting zmax to zmax_edges.zmax().",
            )
            self.sbt_zmax = zedge_max.max()
        else:
            self.sbt_zmax = zmax

        self.sbt_zedge_min = zedge_min
        self.sbt_zedge_max = zedge_max
        self.slice_in_range = np.where((self.sbt_zedge_min <= self.sbt_zmax))[0]

        self.sbt_rmin = self.get_rz(self.sbt_zmin)
        self.sbt_rmax = self.get_rz(self.sbt_zmax)

        self.sbt_kmin = kmin
        self.sbt_kmax = kmax
        if lmax is None:
            self.sbt_lmax = int(self.sbt_rmax * self.sbt_kmax) + 1
        else:
            self.sbt_lmax = lmax
        if nmax is None:
            self.sbt_nmax = int(self.sbt_rmax * self.sbt_kmax / np.pi) + 1
        else:
            self.sbt_nmax = nmax

        self.sbt_redge_min = self.get_rz(self.sbt_zedge_min)
        self.sbt_redge_max = self.get_rz(self.sbt_zedge_max)

        self.uselightcone = uselightcone
        self.temp_path = temp_path

        self.alpha = alpha

        self.create_folder(self.temp_path)

        if boundary_conditions == "normal" or boundary_conditions == "derivative":
            self.boundary_conditions = boundary_conditions
        else:
            print(
                "boundary_conditions can only be 'normal' or 'derivative', not",
                boundary_conditions,
            )

    # ------------------------------------------------------------------------------------------------------------------------#
    # Now define the replacement functions from PyCosmo

    # numerical derivative implementation in TheoryCL -- we can replace this but leave for now
    def numerical_differentiate(
        self, x, f, equal_spacing=False, interpgrid=1000, kind="cubic"
    ):
        """
        For unequally spaced data we interpolate onto an equal spaced 1d grid. Then, we use the symmetric two-point derivative and the non-symmetric three point derivative estimator.

        :param x: X-axis.
        :type x: array
        :param f: Function values at x.
        :type f: array
        :param equal_spacing: Automatically assumes data is not equally spaced and will interpolate from it.
        :type equal_spacing: bool, optional
        :param interpgrid: Grid spacing for the interpolation grid, if equal spacing is False.
        :type interpgrid: int, optional
        :param kind: Interpolation kind.
        :type kind: str, optional
        :return: df, the numerical differentiation values for f evaluated at points x.
        :rtype: array

        Notes
        -----
        For non-boundary values:
        df/dx = (f(x + dx) - f(x - dx)) / (2*dx)

        For boundary values:
        df/dx = (- f(x + 2dx) + 4f(x + dx) - 3f(x)) / (2*dx)
        """
        if equal_spacing is False:
            interpf = interp1d(x, f, kind=kind)
            x_equal = np.linspace(x.min(), x.max(), interpgrid)
            f_equal = interpf(x_equal)
        else:
            x_equal = np.copy(x)
            f_equal = np.copy(f)
        dx = x_equal[1] - x_equal[0]
        df_equal = np.zeros(len(x_equal))
        # boundary differentials
        df_equal[0] = (-f_equal[2] + 4 * f_equal[1] - 3.0 * f_equal[0]) / (2.0 * dx)
        df_equal[-1] = (f_equal[-3] - 4 * f_equal[-2] + 3.0 * f_equal[-1]) / (2.0 * dx)
        # non-boundary differentials
        df_equal[1:-1] = (f_equal[2:] - f_equal[:-2]) / (2.0 * dx)
        if equal_spacing is False:
            interpdf = interp1d(x_equal, df_equal, kind=kind)
            df = interpdf(x)
        else:
            df = np.copy(df_equal)
        return df

    def create_folder(self, root, path=None):
        """
        Creates a folder with the name 'root' either in the current folder if path
        is None or a specified path.
        :param root: The name of the created folder.
        :type root: str
        :param path: The name of the path of the created folder.
        :type path: str, optional
        :return: None
        :rtype: None
        """
        if path is None:
            if os.path.isdir(root) is False:
                subprocess.call("mkdir " + root, shell=True)
        else:
            if os.path.isdir(path + root) is False:
                subprocess.call("mkdir " + path + root, shell=True)

    def get_a(self, r):
        """
        Compute the scale factor a as a function of comoving distance r from an interpolation. Wrapper around utils function.

        :param r: Comoving distance in Mpc
        :type r: float
        :return: scale factor
        :rtype: float
        """

        return utils.a_of_r(r, self.cosmo)

    def get_rz(self, z):
        """
        Compute the corresponding comoving distance value for the input redshift, using this instance's linear interpolator.

        :param z: Input redshift value.
        :type z: float
        :return: Corresponding comoving distance value.
        :rtype: float
        """
        return self.rz_interpolator(z)

    def get_rz_no_interp(self, z):
        """
        Compute the corresponding comoving distance value for the input redshift, without using interpolation. Instead, use the cosmology instance for a direct calculation.

        :param z: Input redshift value.
        :type z: float
        :return: Corresponding comoving distance value.
        :rtype: float
        """
        return (self.H0 / 100) * self.cosmo.comoving_distance(z).to(
            units.Mpc
        ).value  # comoving_distance returns Mpc. Multiplying by h gives Mpc/h.

    def get_zr(self, r):
        """
        Compute the corresponding redshift for the input comoving distance, using interpolation.

        :param r: Input comoving distance value.
        :type r: float
        :return: Corresponding redshift value.
        :rtype: float
        """
        return self.zr_interpolator(r)

    def get_zr_no_interp(self, r):
        """
        Compute the corresponding redshift for the input comoving distance, without using interpolation. Instead, use the cosmology instance for a direct calculation.

        :param r: Input comoving distance value.
        :type r: float
        :return: Corresponding redshift value.
        :rtype: float
        """
        a = utils.a_of_r(r, self.cosmo)

        return 1 / a - 1

    def get_Dr(self, r):
        """
        Compute the linear growth factor D at the input comoving distance r, using interpolation.

        :param r: Input comoving distance value.
        :type r: float
        :return: Corresponding linear growth factor.
        :rtype: float
        """
        return self.Dr_interpolator(r)

    def get_Dz(self, z):
        """
        Compute the linear growth factor D at the input redshift z, using a direct calculation with this instance's cosmology object.

        :param z: Input redshift value.
        :type z: float
        :return: Corresponding linear growth factor.
        :rtype: float
        """
        return utils.growth_z(z, self.cosmo)

    def get_Hr(self, r):
        """
        Compute the Hubble parameter H at the input comoving distance r, using interpolation.

        :param r: Input comoving distance value.
        :type r: float
        :return: Corresponding Hubble parameter.
        :rtype: float
        """
        return self.Hr_interpolator(r)

    def get_Hz(self, z):
        """
        Compute the Hubble parameter H at the input redshift z, using a direct calculation with this instance's cosmology object.

        :param z: Input redshift value.
        :type z: float
        :return: Corresponding Hubble parameter.
        :rtype: float
        """
        return self.cosmo.H(z).value

    def get_fr(self, r):
        """
        Compute the linear growth rate f at the input comoving distance r, using interpolation.

        :param r: Input comoving distance value.
        :type r: float
        :return: Corresponding linear growth rate.
        :rtype: float
        """
        return self.fr_interpolator(r)

    def get_fz(self, z):
        """
        Compute the linear growth rate f at the input redshift z, using interpolation.

        :param z: Input redshift value.
        :type z: float
        :return: Corresponding linear growth rate.
        :rtype: float
        """
        return self.fz_interpolator(z)

    def z2a(self, z):
        """
        Convert an input redshift z into the corresponding scale factor a.

        :param z: Input redshift value.
        :type z: float or array
        :return: Corresponding scale factor.
        :rtype: float or array
        """
        return 1.0 / (1.0 + z)

    def get_fz_numerical(self, z, Dz, **kwargs):
        """
        Compute the linear growth rate f at the input redshifts z, by numerically differentiating the input linear growth factors Dz.

        :param z: Input redshift value.
        :type z: array
        :param Dz: Input linear growth factor value.
        :type Dz: array
        :return: Corresponding linear growth rates.
        :rtype: array
        """
        a = self.z2a(z)
        loga = np.log(a)
        logD = np.log(Dz)
        fz = self.numerical_differentiate(loga, logD, **kwargs)
        return fz

    # ------------------------------------------------------------------------------------------------------------------------#

    def slice2alm(self, map_slice, index):
        """
        Given a density contrast map and its corresponding index (used to obtain the map's
        zedges minimum and maximum), slice2alm will convert the map to its
        spherical harmonics and save the corresponding output files.

        :param map_slice: Healpix density contrast map.
        :type map_slice: array
        :param index: Index of the slice, used to determine the slice's zedges.
        :type index: int
        :return: None
        :rtype: None
        """
        if index in self.slice_in_range:
            map_ = map_slice
            wl = hp.sphtfunc.pixwin(hp.get_nside(map_), lmax=self.sbt_lmax)
            alm = hp.map2alm(map_, lmax=self.sbt_lmax)
            alm = hp.almxfl(alm, 1.0 / wl)
            condition = np.where(self.slice_in_range == index)[0]
            np.savetxt(
                self.temp_path + "map_alm_" + str(condition[0]) + ".txt",
                np.dstack((alm.real, alm.imag))[0],
            )
        else:
            print("Slice not in zmin and zmax range.")

    def alm2sbt(self):
        """
        Converts spherical harmonic coefficients in redshift slices to spherical
        Bessel coefficients. Stored as delta_lmn in units of (Mpc/h)^(1.5).

        :return: None
        :rtype: None
        """
        ell = np.arange(self.sbt_lmax + 1)[2:]
        n = np.arange(self.sbt_nmax + 1)[1:]
        l_grid, n_grid = np.meshgrid(ell, n, indexing="ij")
        self.l_grid = l_grid
        self.n_grid = n_grid
        qln_grid = np.zeros(np.shape(self.l_grid))
        print("Finding zeros for Bessel function up to n = " + str(self.sbt_nmax))
        for i in range(0, len(self.l_grid)):
            l_val = self.l_grid[i][0]
            if i < 10:
                if self.boundary_conditions == "normal":
                    qln_grid[i] = bessel.get_qln(l_val, self.sbt_nmax, nstop=100)
                elif self.boundary_conditions == "derivative":
                    qln_grid[i] = bessel.get_der_qln(l_val, self.sbt_nmax, nstop=100)
            else:
                if self.boundary_conditions == "normal":
                    qln_grid[i] = bessel.get_qln(
                        l_val,
                        self.sbt_nmax,
                        nstop=100,
                        zerolminus1=qln_grid[i - 1],
                        zerolminus2=qln_grid[i - 2],
                    )
                elif self.boundary_conditions == "derivative":
                    qln_grid[i] = bessel.get_der_qln(
                        l_val,
                        self.sbt_nmax,
                        nstop=100,
                        zerolminus1=qln_grid[i - 1],
                        zerolminus2=qln_grid[i - 2],
                    )

        self.kln_grid = qln_grid / self.sbt_rmax
        print("Constructing l and n value grid")
        if self.boundary_conditions == "normal":
            self.Nln_grid = ((self.sbt_rmax**3.0) / 2.0) * bessel.get_jl(
                self.kln_grid * self.sbt_rmax, self.l_grid + 1
            ) ** 2.0
        elif self.boundary_conditions == "derivative":
            self.Nln_grid = ((self.sbt_rmax**3.0) / 2.0) * (
                1.0
                - self.l_grid
                * (self.l_grid + 1.0)
                / ((self.kln_grid * self.sbt_rmax) ** 2.0)
            )
            self.Nln_grid *= (
                bessel.get_jl(self.kln_grid * self.sbt_rmax, self.l_grid) ** 2.0
            )
        if self.sbt_kmin is None and self.sbt_kmax is None:
            l_grid_masked = self.l_grid
            n_grid_masked = self.n_grid
            kln_grid_masked = self.kln_grid
            Nln_grid_masked = self.Nln_grid
        else:
            l_grid_masked = []
            n_grid_masked = []
            kln_grid_masked = []
            Nln_grid_masked = []
            for i in range(0, len(self.l_grid)):
                if self.sbt_kmin is None and self.sbt_kmax is None:
                    condition = np.arange(len(self.kln_grid[i]))
                elif self.sbt_kmin is None:
                    condition = np.where(self.kln_grid[i] <= self.sbt_kmax)[0]
                elif self.sbt_kmax is None:
                    condition = np.where(self.kln_grid[i] >= self.sbt_kmin)[0]
                else:
                    condition = np.where(
                        (self.kln_grid[i] >= self.sbt_kmin)
                        & (self.kln_grid[i] <= self.sbt_kmax)
                    )[0]
                if len(condition) != 0:
                    l_grid_masked.append(self.l_grid[i, condition])
                    n_grid_masked.append(self.n_grid[i, condition])
                    kln_grid_masked.append(self.kln_grid[i, condition])
                    Nln_grid_masked.append(self.Nln_grid[i, condition])
            l_grid_masked = np.array(l_grid_masked, dtype=object)
            n_grid_masked = np.array(n_grid_masked, dtype=object)
            kln_grid_masked = np.array(kln_grid_masked, dtype=object)
            Nln_grid_masked = np.array(Nln_grid_masked, dtype=object)
        self.l_grid_masked = l_grid_masked
        self.n_grid_masked = n_grid_masked
        self.kln_grid_masked = kln_grid_masked
        self.Nln_grid_masked = Nln_grid_masked
        # New part
        print("Pre-compute spherical Bessel integrals")
        _interpolate_jl_int = []
        for i in range(0, len(self.l_grid_masked)):
            _xmin = 0.0
            _xmax = (self.kln_grid_masked[i] * self.sbt_rmax).max() + 1.0
            _x = np.linspace(_xmin, _xmax, 10000)
            _jl_int = np.zeros(len(_x))
            _jl_int[1:] = integrate.cumtrapz(
                (_x**2.0) * bessel.get_jl(_x, l_grid[i][0]), _x
            )
            _interpolate_jl_int.append(
                interpolate.interp1d(
                    _x, _jl_int, kind="cubic", bounds_error=False, fill_value=0.0
                )
            )

        print("Computing spherical Bessel Transform from spherical harmonics")
        for which_slice in range(0, len(self.slice_in_range)):
            index = self.slice_in_range[which_slice]
            print(
                f"mean redshift of slice {1 + which_slice} / {len(self.slice_in_range)}:",
                f"{(self.sbt_zedge_max[index] + self.sbt_zedge_min[index]) / 2:.2f}",
            )

            k_fact = self.alpha(
                (self.sbt_zedge_max[index] + self.sbt_zedge_min[index]) / 2
            )

            l_grid_masked = []
            n_grid_masked = []
            kln_grid_masked = []
            Nln_grid_masked = []
            for i in range(0, len(self.l_grid)):
                if self.sbt_kmin is None and self.sbt_kmax is None:
                    condition = np.arange(len(self.kln_grid[i]))
                elif self.sbt_kmin is None:
                    condition = np.where(self.kln_grid[i] <= self.sbt_kmax)[0]
                elif self.sbt_kmax is None:
                    condition = np.where(self.kln_grid[i] >= self.sbt_kmin)[0]
                else:
                    condition = np.where(
                        (self.kln_grid[i] >= k_fact * self.sbt_kmin)
                        & (self.kln_grid[i] <= self.sbt_kmax)
                    )[0]
                if len(condition) != 0:
                    l_grid_masked.append(self.l_grid[i, condition])
                    n_grid_masked.append(self.n_grid[i, condition])
                    kln_grid_masked.append(self.kln_grid[i, condition])
                    Nln_grid_masked.append(self.Nln_grid[i, condition])
            l_grid_masked = np.array(l_grid_masked, dtype=object)
            n_grid_masked = np.array(n_grid_masked, dtype=object)
            kln_grid_masked = np.array(kln_grid_masked, dtype=object)
            Nln_grid_masked = np.array(Nln_grid_masked, dtype=object)

            r_eff = (
                (3.0 / 4.0)
                * (self.sbt_redge_max[index] ** 4.0 - self.sbt_redge_min[index] ** 4.0)
                / (self.sbt_redge_max[index] ** 3.0 - self.sbt_redge_min[index] ** 3.0)
            )
            Dz_eff = self.get_Dr(r_eff)
            Sln = np.zeros(np.shape(self.kln_grid))
            for i in range(0, len(l_grid)):
                if self.sbt_kmin is None and self.sbt_kmax is None:
                    condition = np.arange(len(self.kln_grid[i]))
                elif self.sbt_kmin is None:
                    condition = np.where(self.kln_grid[i] <= self.sbt_kmax)[0]
                elif self.sbt_kmax is None:
                    condition = np.where(self.kln_grid[i] >= self.sbt_kmin)[0]
                else:
                    # condition = np.where((self.kln_grid[i] >= self.sbt_kmin) & (self.kln_grid[i] <= self.sbt_kmax))[0]
                    # AR update: a redshift dependent kmin
                    condition = np.where(
                        (self.kln_grid[i] >= k_fact * self.sbt_kmin)
                        & (self.kln_grid[i] <= self.sbt_kmax)
                    )[0]
                if len(condition) != 0:
                    Sln[i, condition] += np.array(
                        [
                            (
                                1.0
                                / (
                                    np.sqrt(Nln_grid_masked[i][j])
                                    * kln_grid_masked[i][j] ** 3.0
                                )
                            )
                            * (
                                _interpolate_jl_int[i](
                                    kln_grid_masked[i][j] * self.sbt_redge_max[index]
                                )
                                - _interpolate_jl_int[i](
                                    kln_grid_masked[i][j] * self.sbt_redge_min[index]
                                )
                            )
                            for j in range(0, len(l_grid_masked[i]))
                        ]
                    )

                    # Sln[i, condition] += np.array([(1./(np.sqrt(self.Nln_grid_masked[i][j])*self.kln_grid_masked[i][j]**3.))*(_interpolate_jl_int[i](self.kln_grid_masked[i][j]*self.sbt_redge_max[index]) - _interpolate_jl_int[i](self.kln_grid_masked[i][j]*self.sbt_redge_min[index])) for j in range(0, len(self.l_grid_masked[i]))])
            data = np.loadtxt(
                self.temp_path + "map_alm_" + str(which_slice) + ".txt", unpack=True
            )
            delta_lm_real = data[0]
            delta_lm_imag = data[1]
            delta_lm = delta_lm_real + 1j * delta_lm_imag
            if self.uselightcone is True:
                delta_lm /= Dz_eff
            if which_slice == 0:
                l_map, m_map = hp.Alm.getlm(hp.Alm.getlmax(len(delta_lm)))
                delta_lmn = np.zeros((self.sbt_nmax, len(delta_lm)), dtype="complex")
                conditions1 = []
                conditions2 = []
                for i in range(0, len(Sln[0])):
                    if self.sbt_kmin is None and self.sbt_kmax is None:
                        condition = np.arange(len(self.kln_grid[:, i]))
                    elif self.sbt_kmin is None:
                        condition = np.where(self.kln_grid[:, i] <= self.sbt_kmax)[0]
                    elif self.sbt_kmax is None:
                        condition = np.where(self.kln_grid[:, i] >= self.sbt_kmin)[0]
                    else:
                        # condition = np.where((self.kln_grid[:, i] >= self.sbt_kmin) & (self.kln_grid[:, i] <= self.sbt_kmax))[0]
                        # AR update: a redshift dependent kmin
                        condition = np.where(
                            (self.kln_grid[:, i] >= k_fact * self.sbt_kmin)
                            & (self.kln_grid[:, i] <= self.sbt_kmax)
                        )[0]
                    if len(condition) == 0:
                        lmax = 0
                    else:
                        lmax = self.l_grid[condition, i].max()
                    condition1 = np.where(self.l_grid[:, i] <= lmax)[0]
                    condition2 = np.where(l_map <= lmax)[0]
                    conditions1.append(condition1)
                    conditions2.append(condition2)
                conditions1 = np.array(conditions1, dtype=object)
                conditions2 = np.array(conditions2, dtype=object)
            for i in range(0, len(Sln[0])):
                _delta_lmn = np.zeros(len(delta_lm), dtype="complex")
                _delta_lmn[conditions2[i].astype("int")] = hp.almxfl(
                    delta_lm[conditions2[i].astype("int")],
                    np.concatenate([np.zeros(2), Sln[conditions1[i].astype("int"), i]]),
                )
                delta_lmn[i] += _delta_lmn

        self.delta_lmn = delta_lmn

    def save_sbt(self, prefix=None):
        """
        Saves spherical Bessel transform coefficients.

        :param prefix: Prefix for file containing spherical Bessel transform.
        :type prefix: str
        :return: None
        :rtype: None
        """
        if prefix is None:
            fname = (
                "sbt_zmin_"
                + str(self.sbt_zmin)
                + "_zmax_"
                + str(self.sbt_zmax)
                + "_lmax_"
                + str(self.sbt_lmax)
                + "_nmax_"
                + str(self.sbt_nmax)
            )
        else:
            fname = (
                prefix
                + "_sbt_zmin_"
                + str(self.sbt_zmin)
                + "_zmax_"
                + str(self.sbt_zmax)
                + "_lmax_"
                + str(self.sbt_lmax)
                + "_nmax_"
                + str(self.sbt_nmax)
            )
        if self.boundary_conditions == "normal":
            fname += "_normal.npz"
        elif self.boundary_conditions == "derivative":
            fname += "_derivative.npz"
        np.savez(
            fname,
            kln_grid=self.kln_grid,
            kln_grid_masked=self.kln_grid_masked,
            l_grid_masked=self.l_grid_masked,
            Nln_grid_masked=self.Nln_grid_masked,
            delta_lmn=self.delta_lmn,
        )

    def sbt2isw_alm(self, zmin=None, zmax=None):
        """
        Compute the ISW spherical harmonics between zmin and zmax from the computed
        spherical Bessel Transform.

        :param zmin: Minimum redshift for ISW computation.
        :type zmin: float
        :param zmax: Maximum redshift for ISW computation.
        :type zmax: float
        :return: Array of alm coefficients for the spherical harmonics.
        :rtype: array
        """
        if zmin is None:
            zmin = self.sbt_zmin
        if zmax is None:
            zmax = self.sbt_zmax
        r = np.linspace(self.get_rz(zmin), self.get_rz(zmax), 1000)

        Dz = self.get_Dr(r)
        Hz = self.get_Hr(r)
        fz = self.get_fr(r)

        DHF = Dz * Hz * (1.0 - fz)
        Iln = np.zeros(np.shape(self.kln_grid))
        for i in range(0, len(self.kln_grid)):
            if self.sbt_kmin is None and self.sbt_kmax is None:
                condition = np.arange(len(self.kln_grid[i]))
            elif self.sbt_kmin is None:
                condition = np.where(self.kln_grid[i] <= self.sbt_kmax)[0]
            elif self.sbt_kmax is None:
                condition = np.where(self.kln_grid[i] >= self.sbt_kmin)[0]
            else:
                condition = np.where(
                    (self.kln_grid[i] >= self.sbt_kmin)
                    & (self.kln_grid[i] <= self.sbt_kmax)
                )[0]
            if len(condition) != 0:
                Iln[i, condition] += np.array(
                    [
                        (1.0 / np.sqrt(self.Nln_grid_masked[i][j]))
                        * integrate.simps(
                            DHF
                            * bessel.get_jl(
                                self.kln_grid_masked[i][j] * r, self.l_grid_masked[i][j]
                            ),
                            r,
                        )
                        for j in range(0, len(self.l_grid_masked[i]))
                    ]
                )

        alm_isw = np.zeros(len(self.delta_lmn[0]), dtype="complex")
        for i in range(0, len(self.delta_lmn)):
            alm_isw += hp.almxfl(
                self.delta_lmn[i],
                np.concatenate([np.zeros(2), Iln[:, i] / (self.kln_grid[:, i] ** 2.0)]),
            )

        alm_isw *= 3.0 * self.Om0 * (self.H0**2.0) / ((constants.c * 1000) ** 3.0)
        alm_isw *= 1e9 / ((self.H0 * 1e-2) ** 3.0)

        return alm_isw

    def sbt2isw_map(self, zmin, zmax, nside=256):
        """
        Returns a healpix map of the ISW between zmin and zmax computed from
        the spherical Bessel Transform.

        :param zmin: Minimum redshift for ISW computation.
        :type zmin: float
        :param zmax: Maximum redshift for ISW computation.
        :type zmax: float
        :param nside: NSIDE for healpix map.
        :type nside: int
        :return: Corresponding ISW map.
        :rtype: array
        """
        alm_isw = self.sbt2isw_alm(zmin, zmax)
        map_isw = hp.alm2map(alm_isw, nside) * self.Tcmb
        return map_isw
