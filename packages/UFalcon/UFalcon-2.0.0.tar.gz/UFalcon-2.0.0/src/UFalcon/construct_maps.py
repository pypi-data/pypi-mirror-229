# Copyright (C) 2022 ETH Zurich, Institute for Particle Physics and Astrophysics
# Author: Alexander Reeves

import numpy as np
import healpy as hp
import UFalcon
from UFalcon import probe_weights


class construct_map_cosmogrid:
    """
    Class to compute cosmological signal maps given an input set of lightcone shells and some deatils on the simualtions

    :param maps: An array of HEALPix maps that represent the lightcone shells from a simulation as raw projected particle counts
    :type maps: ndarray
    :param z_low: An array of floats corresponding to the lower redshift value of each lightcone shell
    :type z_low: ndarray
    :param z_high: An array of floats corresponding to the upper redshift value of each lightcone shell
    :type z_high: ndarray
    :param nside: HEALPix nside of output maps (must be lower or equal to the nside of the input simualtion lightcone maps)
    :type nside: int
    :param boxsize: size of the box in Gigaparsec
    :type boxsize: float
    :param cosmo: Astropy.Cosmo instance, controls the cosmology used
    :type cosmo: Astropy cosmology instance
    :param n_particles: total number of parciles used in the N-Body simulation, i.e. (No. of part. per side)^3
    :type n_particles: int
    :param zi: the starting redshift at which lightcone maps should be considered (default 0)
    :type zi: float
    :param zf: the final redshift at which lightcone maps should be considered (default 2)
    :type zf: float
    """

    def __init__(
        self, maps, z_low, z_high, nside, boxsize, cosmo, n_particles, zi=0, zf=2
    ):
        self.maps = maps
        self.z_low = z_low
        self.z_high = z_high
        self.nside = nside
        self.cosmo = cosmo
        self.n_particles = n_particles
        self.boxsize = boxsize
        self.weight_function = {}
        self.zi = zi
        self.zf = zf

    def construct_kappa_map(
        self,
        n_of_z,
        shift_nz=0.0,
        IA=None,
        eta=0.0,
        z_0=0.5,
        fast_mode=False,
        fast_mode_num_points_1d=13,
        fast_mode_num_points_2d=512,
    ):
        """
        Computes kappa_map from precomputed shells in numpy format containing particles counts
        User can define whether they desire a pure cosmological signal or cosmogical signal + IA contribution (nb if IA is not 0 then
        returns signal + IA contribution)

        :param n_of_z: Either path to file containing n(z), assumed to be a text file readable with numpy with the
                        first column containing z and the second column containing n(z), a 2D array of shape (N, 2) or a callable
                        that is directly a redshift distribution.
        :type n_of_z: str or ndarray
        :param shift_nz: Shift the n(z) function by some fixed redshift (intended for easier implementation of photo z bias).
        :type shift_nz: float
        :param IA: Intrinsic alignment amplitude for the NLA model.
        :type IA: float
        :param eta: Parameter for the redshift dependence of the NLA model.
        :type eta: float
        :param z_0: Pivot parameter for the redshift dependence of the NLA model.
        :type z_0: float
        :param fast_mode: Instead of using quad from scipy, use a simple simpson rule, note that this will drastically
                          decrease the runtime of the weight calculation if you n(z) is not continuous, while reducing
                          the accuracy and increasing the memory usage. This mode is intended for large scale runs
                          that use the same or very similar redshift distributions. You should always benchmark the
                          fast mode against the normal mode before you start such a run to see if the accuracy is
                          sufficient. The possibility to tweak the accuracy parameter of the fast mode will come in
                          future versions.
        :param fast_mode_num_points_1d: number of points for computing 1D integral for weak lensing fast mode (default is
                                        tested for cosmogrid lightcones and KiDS-1000 set-up)
        :type fast_mode_num_points_1d: int
        :param fast_mode_num_points_2d: number of points for computing 2D integral for weak lensing fast mode (default is
                                        tested for cosmogrid lightcones and KiDS-1000 set-up)
        :type fast_mode_num_points_2d: int
        :return: HEALPix array representing kappa map with shape (Npix,).
        :rtype: ndarray
        """

        # initialize weight function

        w_nz = probe_weights.Continuous_lensing(
            n_of_z,
            shift_nz=shift_nz,
            fast_mode=fast_mode,
            fast_mode_num_points_1d=fast_mode_num_points_1d,
            fast_mode_num_points_2d=fast_mode_num_points_2d,
        )  # the pure signal weight

        if IA is None or abs(IA - 0.0) < 1e-10:
            use_IA = False
            print("PURE COSMOLOGICAL SIGNAL WITH NO IA BEING COMPUTED")
            w_tot = w_nz
        else:
            use_IA = True
            print("ADDING IA CONTRIBUTION")
            w_IA = probe_weights.Continuous_intrinsic_alignment(
                n_of_z, shift_nz=shift_nz, IA=IA, eta=eta, z_0=z_0, fast_mode=fast_mode
            )

        kappa_map = np.zeros(hp.nside2npix(self.nside), dtype=np.float32)

        zs_tot = np.append(self.z_low, self.z_high[-1])
        zs_in_range = zs_tot[(zs_tot <= self.zf) & (zs_tot >= self.zi)]

        kappa_prefactor = probe_weights.kappa_prefactor(
            n_pix=hp.nside2npix(self.nside),
            n_particles=self.n_particles,
            boxsize=self.boxsize,
            cosmo=self.cosmo,
        )

        delta_prefactor = probe_weights.delta_prefactor(
            n_pix=hp.nside2npix(self.nside),
            n_particles=self.n_particles,
            boxsize=self.boxsize,
            cosmo=self.cosmo,
        )

        for i, map_slice in enumerate(self.maps):
            if self.z_high[i] <= self.zf and self.z_low[i] >= self.zi:
                print(
                    "Processing shell {} / {}".format(i + 1, len(zs_in_range) - 1),
                    flush=True,
                )

                # load shell and downgrade to desired nside
                shell = hp.ud_grade(map_slice, self.nside, power=-2).astype(np.float32)

                if use_IA is False:
                    shell *= (
                        w_nz(self.z_low[i], self.z_high[i], self.cosmo)
                        * kappa_prefactor
                    )

                else:
                    # N.B multiplying the IA contribution by the delta prefactor
                    w_tot = (
                        w_nz(self.z_low[i], self.z_high[i], self.cosmo)
                        * kappa_prefactor
                        + w_IA(self.z_low[i], self.z_high[i], self.cosmo)
                        * delta_prefactor
                    )
                    shell *= w_tot

                kappa_map += shell

            else:
                print(
                    "shell at redshifts {} to {} is outside of specified range so not processing".format(
                        self.z_low[i], self.z_high[i]
                    ),
                    flush=True,
                )

        # remove monopole
        kappa_map -= np.mean(kappa_map)

        return kappa_map

    def construct_IA_map(
        self, n_of_z, shift_nz=0.0, IA=None, eta=0.0, z_0=0.5, fast_mode=False
    ):
        """
        Computes IA only-map from precomputed shells in numpy format containing particle counts.

        :param n_of_z: Either path to file containing n(z), assumed to be a text file readable with numpy with the
                        first column containing z and the second column containing n(z), a 2D array of shape (N, 2) or a callable
                        that is directly a redshift distribution.
        :type n_of_z: str or ndarray
        :param shift_nz: Shift the n(z) function by some fixed redshift (intended for easier implementation of photo z bias).
        :type shift_nz: float
        :param IA: Intrinsic alignment amplitude for the NLA model.
        :type IA: float
        :param eta: Parameter for the redshift dependence of the NLA model.
        :type eta: float
        :param z_0: Pivot parameter for the redshift dependence of the NLA model.
        :type z_0: float
        :param fast_mode: Instead of using quad from scipy, use a simple simpson rule. Note that this will drastically
                        decrease the runtime of the weight calculation if your n(z) is not continuous, while reducing
                        the accuracy and increasing the memory usage. This mode is intended for large scale runs
                        that use the same or very similar redshift distributions. You should always benchmark the
                        fast mode against the normal mode before you start such a run to see if the accuracy is
                        sufficient. The possibility to tweak the accuracy parameter of the fast mode will come in
                        future versions.
        :type fast_mode: bool
        :return: HEALPix array representing IA map with shape (Npix,).
        :rtype: ndarray
        """

        # initialize weight function
        w_IA = probe_weights.Continuous_intrinsic_alignment(
            n_of_z, shift_nz=shift_nz, IA=IA, eta=eta, z_0=z_0
        )

        IA_map = np.zeros(hp.nside2npix(self.nside), dtype=np.float32)

        zs_tot = np.append(self.z_low, self.z_high[-1])
        zs_in_range = zs_tot[(zs_tot <= self.zf) & (zs_tot >= self.zi)]

        delta_prefactor = probe_weights.delta_prefactor(
            n_pix=hp.nside2npix(self.nside),
            n_particles=self.n_particles,
            boxsize=self.boxsize,
            cosmo=self.cosmo,
        )

        for i, map_slice in enumerate(self.maps):
            if self.z_high[i] <= self.zf and self.z_low[i] >= self.zi:
                print(
                    "Processing shell {} / {}".format(i + 1, len(zs_in_range) - 1),
                    flush=True,
                )

                # load shell and downgrade to desired nside
                shell = hp.ud_grade(map_slice, self.nside, power=-2).astype(np.float32)

                shell *= (
                    w_IA(self.z_low[i], self.z_high[i], self.cosmo)
                    * delta_prefactor
                    * self.cosmo.H0.value
                )  # ar added extra H_0 as this seems to be in the equations!

                IA_map += shell

            else:
                print(
                    "shell at redshifts {} to {} is outside of specified range so not processing".format(
                        self.z_low[i], self.z_high[i]
                    ),
                    flush=True,
                )

        # remove monopole
        IA_map -= np.mean(IA_map)

        return IA_map

    def construct_delta_map(self, n_of_z, lin_bias):
        """
        Computes clustering map from precomputed shells in numpy format containing particles counts.

        :param n_of_z: Either path to file containing n(z), assumed to be a text file readable with numpy with the
                        first column containing z and the second column containing n(z), a 2D array of shape (N, 2) or a callable
                        that is directly a redshift distribution.
        :type n_of_z: str or ndarray
        :param lin_bias: the linear bias applied to each clustering map
        :type lin_bias: float
        :return: HEALPix array representing clustering map with shape (Npix,).
        :rtype: ndarray
        """
        # initialize weight function

        w_nz = probe_weights.Continuous_clustering(n_of_z)

        delta_map = np.zeros(hp.nside2npix(self.nside), dtype=np.float32)

        zs_tot = np.append(self.z_low, self.z_high[-1])
        zs_in_range = zs_tot[(zs_tot <= self.zf) & (zs_tot >= self.zi)]

        for i, map_slice in enumerate(self.maps):
            if self.z_high[i] <= self.zf and self.z_low[i] >= self.zi:
                print(
                    "Processing shell {} / {}".format(i + 1, len(zs_in_range) - 1),
                    flush=True,
                )

                # load shell and downgrade to desired nside
                shell = hp.ud_grade(map_slice, self.nside, power=-2).astype(np.float32)

                shell *= w_nz(self.z_low[i], self.z_high[i], lin_bias, self.cosmo)

                delta_map += shell

            else:
                print(
                    "shell at redshifts {} to {} is outside of specified range so not processing".format(
                        self.z_low[i], self.z_high[i]
                    ),
                    flush=True,
                )

        return delta_map * probe_weights.delta_prefactor(
            n_pix=hp.nside2npix(self.nside),
            n_particles=self.n_particles,
            boxsize=self.boxsize,
            cosmo=self.cosmo,
        )

    def construct_kappa_cmb_map(self):
        """
        Computes cmb kappa_map from precomputed shells in numpy format containing particles counts. The redshift of recombination is
        fixed to 1090.0 and this code prints out the zmax up to which the CMB lensing contribution has been calculated (beyond this consider
        adding a gaussian synfast realization).

        :return: HEALPix array representing CMB lensing map with shape (Npix,).
        :rtype: ndarray
        """

        # initialize weight function
        z_cmb = 1090.0

        w_nz = probe_weights.Dirac_lensing(z_source=z_cmb)

        kappa_map = np.zeros(hp.nside2npix(self.nside), dtype=np.float32)

        zs_tot = np.append(self.z_low, self.z_high[-1])
        zs_in_range = zs_tot[(zs_tot <= self.zf) & (zs_tot >= self.zi)]

        print("actual zmax for cmb kappa:", zs_in_range[-1])

        for i, map_slice in enumerate(self.maps):
            if self.z_high[i] <= self.zf and self.z_low[i] >= self.zi:
                print(
                    "Processing shell {} / {}".format(i + 1, len(zs_in_range) - 1),
                    flush=True,
                )

                # load shell and downgrade to desired nside
                shell = hp.ud_grade(map_slice, self.nside, power=-2).astype(np.float32)

                shell *= w_nz(self.z_low[i], self.z_high[i], self.cosmo)

                kappa_map += shell

            else:
                print(
                    "shell at redshifts {} to {} is outside of specified range so not processing".format(
                        self.z_low[i], self.z_high[i]
                    ),
                    flush=True,
                )

        return kappa_map * probe_weights.kappa_prefactor(
            n_pix=hp.nside2npix(self.nside),
            n_particles=self.n_particles,
            boxsize=self.boxsize,
            cosmo=self.cosmo,
        )

    def construct_isw_map(self, temp_path="./temp/", zmax_for_box=None, alpha=None):
        """
        Computes cmb ISW from precomputed shells in numpy format containing particles counts. This function is still experimental and should be used
        with caution. In particular, we have found unphysical features due to box-edges in some of the maps computed using this algorithm and we
        caution the user to visually and statistically inspect any produced maps for unphysical features. NB this only computes the contribution to the ISW
        signal until z=zmax_for_box which is defined as the redshift beyond which there would be significant features due to box replication.

        :param temp_path: the temporary path where intermediate alms will be stored (recommended
                          to put this in the local scratch space)
        :type temp_path: str
        :param zmax_for_box: a maximum user-defined redshift that the ISW contribution is computed until. If not supplied the default value
                            of zmax_for_box=1.5*z(boxsize) i.e. the redshift at the edge of a single box multiplied by 1.5.
                            The factor of 1.5 is motivated by experimentation with boxsizes 900 Mpc/h and 2250 Mpc/h.
        :type zmax_for_box: float
        :param alpha: a function that takes an input redshift (alpha(z)). This determines the factor by which
                      the nominal minimum k mode (2pi/lbox) should be multiplied by to avoid unphysical features for redshifts ranges
                      requiring box replications. If nothing supplied the default function is used alpha(z)=1.5 + 0.02 * np.exp((z - zmax_for_box))
                      which has been shown to remove unphysical features for a Cosmogrid-like set of simulations.
        :type alpha: callable
        :return: HEALPix array representing CMB ISW map with shape (Npix,) in units of K.
        :rtype: ndarray
        """

        # boxsize factor: ISW algorithm boxsize in Mpc/h so we have to convert back from the value in Gpc given to UFalcon
        boxsize_isw = self.boxsize * 1000.0 * (self.cosmo.H0.value / 100.0)

        # initialize SBT class
        print("Creating SBT class. This may take a few seconds...")
        SBT = self.get_SBT_class_instance()

        # If zmax is not passed in, the pipeline will choose the recommended value,
        # The factor of 1.5 is motivated by experimentation with boxsizes 900 Mpc/h and 2250 Mpc/h.
        # In both boxsizes, going up to larger zmax (i.e. beyond this factor of 1.5 in comoving distance)
        # leads to large, non-physical features in the resulting ISW maps from healpy.
        if zmax_for_box is None:
            zmax_for_box = SBT.get_zr(1.5 * boxsize_isw)
            print(
                f"zmax_for_box = None was passed. Using the recommended value of {zmax_for_box:.2f} computed based on the boxsize {boxsize_isw:.2f} Mpc/h."
            )

        if alpha is None:
            print(
                "Warning: no alpha function provided, so the default is being used. However, this default has only been tested on a Cosmogrid set up, so proceed with caution."
            )

            def alpha(z):
                if z < zmax_for_box:
                    return 1
                else:
                    fac = 1.5 + 0.02 * np.exp((z - zmax_for_box))
                    return fac

        SBT.setup(
            self.zi,
            zmax_for_box,
            self.z_low,
            self.z_high,
            kmin=2 * np.pi / boxsize_isw,
            kmax=0.3,
            temp_path=temp_path,
            alpha=alpha,
        )

        for i, map_slice in enumerate(self.maps):
            print(
                "converting to alm shell {} / {}".format(i + 1, len(self.maps)),
                flush=True,
            )

            # load shell and downgrade to desired nside
            shell = hp.ud_grade(map_slice, self.nside, power=-2).astype(np.float32)

            overdensity_map_slice = self.get_zero_mean_overdensity_from_map(shell)

            SBT.slice2alm(overdensity_map_slice, i)

        print("Converting to sbt...")
        SBT.alm2sbt()

        isw_map = SBT.sbt2isw_map(zmin=self.zi, zmax=zmax_for_box, nside=self.nside)

        return isw_map

    def get_zero_mean_overdensity_from_map(self, map_slice):
        """
        Function to get the zero-mean overdensity given an input lightcone shell

        :param map_slice: lightcone shell
        :type map_slice: ndarray
        :return: zero mean overdensity map
        :rtype: ndarray
        """
        mean_count = np.mean(map_slice)
        return (map_slice - mean_count) / mean_count

    def get_SBT_class_instance(self):
        """
        Function to initialize the SBT class for the ISW map making algorithm.
        """

        zmin_lookup = 0.0
        zmax_lookup = 10.0
        zbin_num = 10000
        zbin_mode = "log"

        SBT = UFalcon.sbt_class.SphericalBesselISW(self.cosmo)
        SBT.calc_table(
            zmin=zmin_lookup, zmax=zmax_lookup, zbin_num=zbin_num, zbin_mode=zbin_mode
        )

        return SBT
