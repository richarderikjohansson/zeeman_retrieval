import pyarts
import numpy as np
import h5py
import os
from simulation_package.make_grids import make_atm_grids, get_git_root
from simulation_package.hdf import read_hdf5, DottedDict


class Retrieval:
    def __init__(self, line, start=0, recalc=False):
        self.arts = pyarts.workspace.Workspace()
        self.line = line
        self.set_arts_path()
        self.set_frequency_grid()
        self.set_species()
        self.set_atm_grids(start)
        self.set_agendas()
        self.radiative_transfer()
        self.set_geometry()
        self.set_abs_file()
        self.propmat(recalc=recalc)
        self.check_calc()
        self.apply_hse()
        self.do_yCalc(recalc=recalc)
        self.init_retrieval()
        self.set_errors()
        self.config_sensor_and_iter_agendas()

    def set_arts_path(self):
        home = os.getenv("HOME")
        arts_catalogue_path = f"{home}/.cache/arts/"

        if not os.path.exists(arts_catalogue_path):
            pyarts.cat.download.retrieve(verbose=True)

        self.arts_catalogue_directory = f"{arts_catalogue_path}/arts-cat-data-2.6.10"
        self.arts_xml_directory = f"{arts_catalogue_path}/arts-xml-data-2.6.10"

    def set_frequency_grid(self):
        self.flen = 5000

        match self.line:
            case "tempera":
                f = np.linspace(5.3546e10, 5.3646e10, self.flen)
            case "kimra":
                f = np.linspace(23.35e10, 23.45e10, self.flen)

        self.start = f[0]
        self.stop = f[-1]
        self.arts.f_grid = f

    def set_atm_grids(self, start):
        self.atm = make_atm_grids(start)

    def set_geometry(self):
        self.arts.PlanetSet(option="Earth")
        self.arts.refellipsoidEarth(model="Sphere")
        self.arts.AtmosphereSet3D()
        self.arts.Wigner6Init()

        self.arts.p_grid = self.atm.pressure
        self.arts.lat_grid = np.linspace(55, 75)
        self.arts.lon_grid = np.linspace(10, 30)
        self.arts.AtmRawRead(
            basename=f"{self.arts_xml_directory}/planets/Earth/Fascod/subarctic-winter/subarctic-winter"
        )
        data = pyarts.arts.GriddedField3(
            [self.atm.pressure, [0], [0]],
            np.array(self.atm.temperature).reshape(self.atm.plen, 1, 1),
            gridnames=["Pressure", "Latitude", "Longitude"],
        )

        self.arts.t_field_raw = data
        self.arts.AtmFieldsCalcExpand1D()
        self.arts.MagFieldsCalcIGRF()
        self.z0 = min(self.arts.z_field.value[:, :, :].flatten())
        self.arts.z_surfaceConstantAltitude(altitude=self.z0 + 1)
        self.arts.t_surface = self.atm.temperature[1] + np.ones_like(
            self.arts.z_surface.value
        )

        self.arts.stokes_dim = 4
        self.arts.sensor_pos = [[self.z0 + 20, 67.84, 20.22]]
        self.arts.sensor_los = [[45, 90]]
        self.arts.f_backend = self.arts.f_grid
        self.arts.Touch(self.arts.sensor_time)
        self.arts.sensorOff()

    def set_species(self):
        self.arts.abs_speciesSet(
            species=[
                f"O2-Z-*-{self.start - 1}-{self.stop + 1}",
                f"O2-*-{self.start - 1}-{self.stop + 1}",
                f"O3-*-{self.start - 1}-{self.stop + 1}",
                "N2-SelfContStandardType",
                "H2O-PWR98",
            ]
        )

    def set_agendas(self):
        self.arts.water_p_eq_agendaSet(option="MK05")
        self.arts.ppath_agendaSet(option="FollowSensorLosPath")
        self.arts.iy_main_agendaSet(option="Emission")
        self.arts.surface_rtprop_agendaSet(option="Blackbody_SurfTFromt_field")
        self.arts.ppath_step_agendaSet(option="GeometricPath")
        self.arts.iy_space_agendaSet(option="CosmicBackground")
        self.arts.iy_surface_agendaSet(option="UseSurfaceRtprop")

    def radiative_transfer(self):
        self.arts.iy_unit = "PlanckBT"
        self.arts.ppath_lmax = 1e3
        self.arts.ppath_lraytrace = 1e3
        self.arts.rt_integration_option = "default"
        self.arts.rte_alonglos_v = 0.0
        self.arts.jacobianOff()
        self.arts.Touch(self.arts.time)
        self.arts.cloudboxOff()
        self.arts.nlteOff()

    def set_abs_file(self):
        abs_lines_per_species_path = f"{get_git_root()}/data/abs_lines_per_species"

        match self.line:
            case "tempera":
                self.abs_lines_per_species_file = (
                    f"{abs_lines_per_species_path}/tempera.xml"
                )
            case "kimra":
                self.abs_lines_per_species_file = (
                    f"{abs_lines_per_species_path}/kimra.xml"
                )

    def propmat(self, recalc=False):
        if recalc:
            print(f"recalculating abs_lines for {self.line} line")
            self.arts.abs_lines_per_speciesReadSpeciesSplitCatalog(
                basename=f"{self.arts_catalogue_directory}/lines/"
            )
            self.arts.WriteXML(
                input=self.arts.abs_lines_per_species,
                output_file_format="binary",
                filename=self.abs_lines_per_species_file,
            )
        else:
            self.arts.ReadXML(
                self.arts.abs_lines_per_species, self.abs_lines_per_species_file
            )
        self.arts.propmat_clearsky_agendaAuto()

    def check_calc(self):
        self.arts.atmgeom_checkedCalc()
        self.arts.lbl_checkedCalc()
        self.arts.atmfields_checkedCalc()
        self.arts.cloudbox_checkedCalc()
        self.arts.sensor_checkedCalc()
        self.arts.propmat_clearsky_agenda_checkedCalc()

    def apply_hse(self):
        self.arts.p_hse = self.atm.pressure[1]
        self.arts.z_hse_accuracy = 10
        self.arts.z_fieldFromHSE()

    def do_yCalc(self, recalc=False):
        self.ycalc_path = f"{get_git_root()}/data/simulated_spectras"
        self.ycalc_file_path = f"{self.ycalc_path}/{self.line}.hdf5"

        if recalc:
            print(f"Start ycalc for {self.line} line")
            self.arts.yCalc()
            self.save_ycalc()

    def save_ycalc(self):
        if not os.path.exists(self.ycalc_path):
            os.makedirs(self.ycalc_path)

        I = self.arts.y.value[0::4]
        Q = self.arts.y.value[1::4]
        U = self.arts.y.value[2::4]
        V = self.arts.y.value[3::4]
        f = self.arts.f_grid.value

        self.ycalc_file_path = f"{self.ycalc_path}/{self.line}.hdf5"
        y = I - Q + np.random.normal(loc=0, scale=0.3, size=self.flen)

        with h5py.File(self.ycalc_file_path, "w") as file:
            file["I"] = I
            file["Q"] = Q
            file["U"] = U
            file["V"] = V
            file["f"] = f
            file["y"] = y

    def init_retrieval(self):
        self.arts.retrievalDefInit()
        ycalc = DottedDict(read_hdf5(filename=self.ycalc_file_path))
        self.arts.y = ycalc.y
        self.arts.yf = []
        self.arts.x = []
        self.arts.jacobian = []
        self.arts.xa = self.atm.apriori

    def set_errors(self):

        # apriori error
        Sa = np.zeros(shape=(self.atm.plen)) + 100
        self.arts.retrievalAddTemperature(
            covmat_block=np.diag(Sa),
            covmat_inv_block=np.diag(1 / Sa),
            g1=self.atm.pressure,
            g2=[67.84],
            g3=[20.22],
        )

        # measurement error
        self.arts.covmat_seSet(
            covmat=pyarts.arts.Sparse(np.diag(np.zeros(shape=(self.flen)) + 1))
        )

        # Baseline Fit
        self.arts.retrievalAddPolyfit(
            poly_order=1,
            covmat_block=[],
            covmat_inv_block=[],
            no_pol_variation=1,
            no_los_variation=1,
        )

        # Add Baseline error to S_a
        self.arts.covmat_sxAddBlock(block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 100)))
        self.arts.covmat_sxAddInverseBlock(
            block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 1 / 100))
        )
        self.arts.covmat_sxAddBlock(block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 25)))
        self.arts.covmat_sxAddInverseBlock(
            block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 1 / 25))
        )

        # Add apriori baseline to xa
        self.arts.xa = np.append(self.arts.xa.value, [0, 0])

        # close definition of retrieval
        self.arts.retrievalDefClose()

    def config_sensor_and_iter_agendas(self):
        @pyarts.workspace.arts_agenda(ws=self.arts, set_agenda=True)
        def sensor_response_agenda(ws):
            ws.AntennaOff()
            ws.Ignore(ws.f_backend)
            ws.sensor_responseInit(sensor_norm=1)
            ws.sensor_responsePolarisation(instrument_pol=[6])

        self.arts.sensor_response_agenda.value.execute(self.arts)

        @pyarts.workspace.arts_agenda(ws=self.arts, set_agenda=True)
        def inversion_iterate_agenda(ws):
            ws.Ignore(ws.inversion_iteration_counter)
            ws.x2artsAtmAndSurf()
            ws.x2artsSensor()
            ws.yCalc(y=ws.yf)
            ws.VectorAddElementwise(ws.yf, ws.yf, ws.y_baseline)
            ws.jacobianAdjustAndTransform()

    def do_OEM(self, filename):
        print(f"Starting temperature retrieval of {self.line} line")
        self.arts.OEM(
            method="lm",
            lm_ga_settings=[200, 3, 1.5, 300, 5, 20],
            max_iter=20,
            display_progress=1,
        )
        self.arts.avkCalc()
        self.arts.covmat_ssCalc()
        self.arts.covmat_soCalc()
        self.arts.retrievalErrorsExtract()
        self.arts.x2artsSensor()
        self.retrieval_filename = filename

        self.save_ret(
            self.arts.f_grid,
            self.arts.xa,
            self.arts.x,
            self.arts.y,
            self.arts.yf,
            self.arts.jacobian,
            self.arts.z_field,
            self.arts.avk,
            self.arts.p_grid,
            self.arts.retrieval_ss,
            self.arts.retrieval_eo,
        )

    def save_ret(self, *argv):
        savepath = f"{get_git_root()}/data/retrieval"
        if not os.path.exists(savepath):
            os.makedirs(savepath)

        with h5py.File(f"{savepath}/{self.retrieval_filename}", "w") as file:
            for data in argv:
                file[data.name] = data.value
            file["plen"] = self.atm.plen

        print(f"Saved retrieval in {savepath}/{self.retrieval_filename}")
