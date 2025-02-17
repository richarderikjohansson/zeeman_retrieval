import os

import h5py
import numpy as np
import pyarts
import sys

# Global
ATMBASE = "catalogue/subarctic-winter/subarctic-winter"
CENTRAL_LINE_FREQ = 233946098286.277
SPECTROMETER_HW = 15e6
NF = 100051
ROOT = sys.argv[1]


# --- functions ---


def save_ycalc(I, Q, U, V, f, azi, filename):
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

    savepath = f"{ROOT}/data/simulation"
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    with h5py.File(f"{savepath}/{filename}.hdf5", "w") as file:
        file["I"] = I
        file["Q"] = Q
        file["U"] = U
        file["V"] = V
        file["f"] = f
        file["azi"] = azi


def ycalc(azi):
    """
    Simulation of Zeeman affected rotational transition of O2 233.9 GHz

    Parameters:
    azi (float): azimuth angle for the line of sight

    Returns:
    I (np.array): Intensity of the radiation
    Q (np.array): Stoke component associated with the linear polarization (vertical and horizontal)
    U (np.array): Stoke component associated with the linear polarization (45°)
    V (np.array): Stoke component associated with the circular polarization (right and left hand)
    f (np.array): Frequency vector
    azi (float): azimuth angle for the line of sight
    """

    ws = pyarts.workspace.Workspace()

    # %% Agendas
    ws.ppath_agendaSet(option="FollowSensorLosPath")
    ws.iy_main_agendaSet(option="Emission")
    ws.surface_rtprop_agendaSet(option="Blackbody_SurfTFromt_surface")
    ws.ppath_step_agendaSet(option="GeometricPath")
    ws.iy_space_agendaSet()
    ws.iy_surface_agendaSet()
    ws.water_p_eq_agendaSet()

    # %% Calculations
    ws.jacobianOff()
    ws.iy_unit = "PlanckBT"
    ws.ppath_lmax = 10e3
    ws.ppath_lraytrace = 1e3
    ws.rt_integration_option = "default"
    ws.rte_alonglos_v = 0.0
    ws.nlteOff()

    # %% Species and line absorption
    ws.abs_speciesSet(
        species=[
            f"O2-Z-68-{CENTRAL_LINE_FREQ - 10e6}-{CENTRAL_LINE_FREQ + 10e6}",
            "O2-PWR98",
            "H2O-PWR98",
        ]
    )
    ws.Touch(ws.abs_lines_per_species)
    ws.ReadXML(
        ws.abs_lines_per_species,
        f"{ROOT}/catalogue/abs_lines/abs_lines_per_species.xml",
    )
    ws.Wigner6Init()

    # %% Use the automatic agenda setter
    ws.propmat_clearsky_agendaAuto()

    # %% Grids and planet
    ws.p_grid = np.logspace(np.log10(105000), np.log10(0.1))
    ws.lat_grid = np.linspace(50, 80)
    ws.lon_grid = np.linspace(10, 30)
    ws.refellipsoidEarth(model="Sphere")
    ws.z_surfaceConstantAltitude(altitude=410)
    ws.t_surface = 293.15 + np.ones_like(ws.z_surface.value)

    # %% Atmosphere
    ws.AtmRawRead(basename=ATMBASE)
    ws.AtmosphereSet3D()
    ws.AtmFieldsCalcExpand1D()
    ws.Touch(ws.wind_u_field)
    ws.Touch(ws.wind_v_field)
    ws.Touch(ws.wind_w_field)
    ws.MagFieldsCalcIGRF(time=pyarts.arts.Time("2024-01-04 19:00:00"))
    ws.cloudboxOff()

    # %% Sensor
    ws.stokes_dim = 4
    ws.f_grid = np.linspace(-SPECTROMETER_HW, SPECTROMETER_HW, NF) + CENTRAL_LINE_FREQ
    ws.sensor_pos = [[460, 67.9, 20.4]]
    ws.sensor_los = [[77.6, azi]]
    ws.sensorOff()

    # %% Computechecks
    ws.atmgeom_checkedCalc()
    ws.lbl_checkedCalc()
    ws.atmfields_checkedCalc()
    ws.cloudbox_checkedCalc()
    ws.sensor_checkedCalc()
    ws.propmat_clearsky_agenda_checkedCalc()

    # %% Compute

    ws.yCalc()

    # %% Plot current
    I = ws.y.value[0::4]
    Q = ws.y.value[1::4]
    U = ws.y.value[2::4]
    V = ws.y.value[3::4]
    f = (ws.f_grid.value - CENTRAL_LINE_FREQ) / 1e6  # MHz
    return I, Q, U, V, f, azi


# --- driver code ---
azimuth = np.array([0, 90, 180, -90])
for azi in azimuth:
    I, Q, U, V, f, azi = ycalc(azi)

    hm = {0: 0, 90: 90, 180: 180, -90: 270}
    azi_map = hm[azi]

    filename = f"ycalc_O2_{azi_map}"
    save_ycalc(I, Q, U, V, f, azi, filename)
