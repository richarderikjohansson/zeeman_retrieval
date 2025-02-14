import pyarts
import numpy as np
import sys
import os
import h5py
import json

ROOT = sys.argv[1]
ATMBASE = f"{ROOT}/catalogue/subarctic-winter/subarctic-winter"


def read_hdf5(filename):
    """
    Function to read hdf5 files

    Parameters:
    filename (str) : path to the file

    Returns:
    dictionary (dict): A dictionary with the data
    """

    with h5py.File(filename, "r") as file:
        if "kimra_data" in file.keys():
            dataset = file["kimra_data"]

        else:
            dataset = file

        dictionary = dict()
        for key in dataset.keys():  # pyright:ignore
            try:
                dictionary[key] = dataset[key][:]  # pyright:ignore
            except ValueError:
                dictionary[key] = dataset[key][()]  # pyright:ignore

        return dictionary


def save_ret(filename, *argv):
    """
    Function to save simulation date in hdf5 file

    Parameters:
    I (np.array): Intensity of the radiation
    Q (np.array): Stoke component associated with the linear polarization (vertical and horizontal)
    U (np.array): Stoke component associated with the linear polarization (45°)
    V (np.array): Stoke component associated with the circular polarization (right and left hand)
    f (np.array): Frequency vector
    azi (float): azimuth angle for the line of sight
    filename (str): name of the file
    """

    savepath = f"{ROOT}/data/retrieval"
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    with h5py.File(f"{savepath}/{filename}", "w") as file:
        for data in argv:
            file[data.name] = data.value


def oem_O2_O3(filename, config):
    with open(config) as json_file:
        config = json.load(json_file)
        abs_file = config["abs_file"]
        config["abs_file"] = f"{ROOT}/catalogue/abs_lines/{abs_file}"

    data = read_hdf5(filename)

    # profiles
    p_a = pyarts.xml.load(ROOT + "/data/grids/p_grid_137.xml")
    x_a = pyarts.xml.load(ROOT + "/data/grids/ECMWF_jan.xml")
    f_resolution = np.array([76300])
    plen = len(p_a)
    geo_pos = [67.84, 20.22]

    # open workspace
    arts = pyarts.workspace.Workspace()
    arts.ppath_agendaSet(option="FollowSensorLosPath")
    arts.iy_main_agendaSet(option="Emission")
    arts.surface_rtprop_agendaSet(option="Blackbody_SurfTFromt_field")
    arts.ppath_step_agendaSet(option="GeometricPath")
    arts.iy_space_agendaSet(option="CosmicBackground")
    arts.iy_surface_agendaSet(option="UseSurfaceRtprop")

    arts.iy_unit = "RJBT"
    arts.ppath_lmax = 250
    arts.ppath_lraytrace = 1e3
    arts.rt_integration_option = "default"
    arts.rte_alonglos_v = 0.0
    arts.jacobianOff()
    arts.Touch(arts.time)
    arts.cloudboxOff()
    arts.nlteOff()

    arts.Wigner6Init()
    arts.abs_speciesSet(species=config["species"])
    arts.ReadXML(arts.abs_lines_per_species, config["abs_file"])
    y = data["I"] - data["Q"]
    f = data["f"]
    noise = np.random.normal(0, 0.08, len(y))
    arts.y = y + noise
    arts.f_grid = f
    arts.f_backend = arts.f_grid
    arts.propmat_clearsky_agendaAuto()
    arts.water_p_eq_agendaSet(option="MK05")

    ###############################################################################
    # %% Grids and planet
    ###############################################################################

    arts.PlanetSet(option="Earth")
    arts.refellipsoidEarth(model="Sphere")
    arts.AtmosphereSet3D()

    arts.p_grid = p_a
    arts.lat_grid = np.linspace(65, 70, 200)
    arts.lon_grid = np.linspace(10, 35, 200)
    arts.z_surfaceConstantAltitude(altitude=460.0)
    arts.t_surface = x_a[1] + np.ones_like(arts.z_surface.value)

    ###############################################################################
    # %% Atmosphere
    ###############################################################################

    arts.AtmRawRead(basename=ATMBASE)
    t_raw_iter = pyarts.xml.load(ROOT + "/data/grids/24010418_t.xml")
    t_raw = [val for val in t_raw_iter]
    data = pyarts.arts.GriddedField3(
        [p_a, [0], [0]],
        np.array(t_raw).reshape(len(p_a), 1, 1),
        gridnames=["Pressure", "Latitude", "Longitude"],
    )

    arts.t_field_raw = data
    arts.AtmFieldsCalcExpand1D()
    arts.MagFieldsCalcIGRF()

    ###############################################################################
    # %% Sensor
    ###############################################################################

    if config["flag"]:
        arts.stokes_dim = 4
    else:
        arts.stokes_dim = 1

    arts.sensor_pos = [[460, 67.9, 20.4]]
    arts.sensor_los = [[77.6, 90]]
    arts.Touch(arts.sensor_time)
    arts.sensorOff()
    arts.backend_channel_responseGaussianConstant(fwhm=f_resolution[0])
    arts.sensor_norm = 1

    ###############################################################################
    # %% Computechecks
    ###############################################################################

    arts.atmgeom_checkedCalc()
    arts.lbl_checkedCalc()
    arts.atmfields_checkedCalc()
    arts.cloudbox_checkedCalc()
    arts.sensor_checkedCalc()
    arts.propmat_clearsky_agenda_checkedCalc()

    ###############################################################################
    # %% HSE
    ###############################################################################

    arts.p_hse = p_a[1]
    arts.z_hse_accuracy = 10
    arts.z_fieldFromHSE()

    ###############################################################################
    # %% Set Retrieval quantities
    ###############################################################################

    # Initialize Retrieval
    arts.retrievalDefInit()

    arts.yf = []
    arts.x = []
    arts.jacobian = []
    arts.xa = x_a

    # Apriori error S_a for temperature
    Sa = np.zeros(shape=(plen)) + 100
    arts.retrievalAddTemperature(
        covmat_block=np.diag(Sa),
        covmat_inv_block=np.diag(1 / Sa),
        g1=p_a,
        g2=[geo_pos[0]],
        g3=[geo_pos[1]],
    )

    # Measurement error S_e for spectrum
    arts.covmat_seSet(covmat=pyarts.arts.Sparse(np.diag(np.zeros(shape=(len(f))) + 2)))

    # Baseline Fit
    arts.retrievalAddPolyfit(
        poly_order=1,
        covmat_block=[],
        covmat_inv_block=[],
        no_pol_variation=1,
        no_los_variation=1,
    )

    # Add Baseline error to S_a
    arts.covmat_sxAddBlock(block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 100)))
    arts.covmat_sxAddInverseBlock(
        block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 1 / 100))
    )
    arts.covmat_sxAddBlock(block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 25)))
    arts.covmat_sxAddInverseBlock(
        block=pyarts.arts.Sparse(np.diag(np.zeros(shape=(1)) + 1 / 25))
    )

    # Add apriori baseline to xa
    arts.xa = np.append(arts.xa.value, [0, 0])
    arts.retrievalDefClose()

    ###############################################################################
    # %% sensor response agenda
    ###############################################################################

    if config["flag"]:
        instrument_pol = config["instrument_pol"]

        @pyarts.workspace.arts_agenda(ws=arts, set_agenda=True)
        def sensor_response_agenda(ws):
            ws.AntennaOff()
            ws.Ignore(ws.f_backend)
            ws.sensor_responseInit()
            ws.sensor_responsePolarisation(instrument_pol=[instrument_pol]) # vertically (pi lines) = 5. horizontally (sigma lines) = 6
    else:
        @pyarts.workspace.arts_agenda(ws=arts, set_agenda=True)
        def sensor_response_agenda(ws):
            ws.AntennaOff()
            ws.Ignore(ws.f_backend)
            ws.sensor_responseInit()


    arts.sensor_response_agenda.value.execute(arts)

    ###############################################################################
    # %% Iteration schema
    ###############################################################################

    @pyarts.workspace.arts_agenda(ws=arts, set_agenda=True)
    def inversion_iterate_agenda(ws):
        ws.Ignore(ws.inversion_iteration_counter)
        ws.x2artsAtmAndSurf()
        ws.x2artsSensor()
        ws.yCalc(y=ws.yf)
        ws.VectorAddElementwise(ws.yf, ws.yf, ws.y_baseline)
        ws.jacobianAdjustAndTransform()

    ###############################################################################
    # %% Start OEM
    ###############################################################################
    print("OEM started")
    arts.OEM(
        method="lm",
        max_iter=20,
        display_progress=1,
        lm_ga_settings=[10, 10, 10, 1000000000000000.0, 1, 100],
    )
    print("OEM finished")
    ###############################################################################
    # %% Compute Retrieval quantities
    ###############################################################################

    arts.avkCalc()
    arts.covmat_ssCalc()
    arts.covmat_soCalc()
    arts.retrievalErrorsExtract()
    arts.x2artsSensor()

    save_ret(
        config["filename"],
        arts.f_grid,
        arts.xa,
        arts.x,
        arts.y,
        arts.yf,
        arts.jacobian,
        arts.z_field,
        arts.avk,
        arts.p_grid,
        arts.retrieval_ss,
        arts.retrieval_eo,
    )


# --- driver code ---
configs = [
    f"{ROOT}/data/configs/zeeman_on.json",
    f"{ROOT}/data/configs/zeeman_off.json",
    f"{ROOT}/data/configs/zeeman_on_wrong_component.json",
           ]

file = f"{ROOT}/data/simulation/ycalc_O2_zeeman_on.hdf5"
for config in configs:
    oem_O2_O3(filename=file, config=config)
