import numpy as np
import pyarts
import sys
import os
import h5py
from datetime import datetime

# Global
ROOT = sys.argv[1]
ATMBASE = f"{ROOT}/catalogue/subarctic-winter/subarctic-winter"
START = 233596117200.0
END = 234296169700.0

sys.path.append(f"{ROOT}/utils")
from utils.temperature import get_temperature

# --- functions ---
def save_ycalc(I, Q, U, V, f, filename):
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


def ycalc(zeeman):
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
    if zeeman:
        species = [
            f"O2-Z-68-{START - 10e6}-{END + 10e6}",
            f"O3-*-{START - 10e6}-{END + 10e6}",
            "O2-PWR98",
            "H2O-PWR98",
        ]
        abs_file = f"{ROOT}/catalogue/abs_lines/abs_lines_per_species_zeeman_on.xml"
    else:
        species = [
            f"O2-68-{START - 10e6}-{END + 10e6}",
            f"O3-*-{START - 10e6}-{END + 10e6}",
            "O2-PWR98",
            "H2O-PWR98",
        ]
        abs_file = f"{ROOT}/catalogue/abs_lines/abs_lines_per_species_zeeman_off.xml"

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

    ws.abs_speciesSet(species=species)
    ws.Touch(ws.abs_lines_per_species)
    ws.ReadXML(
       ws.abs_lines_per_species,
       abs_file 
    )
    ws.Wigner6Init()

    # %% Use the automatic agenda setter
    ws.propmat_clearsky_agendaAuto()

    # %% Grids and planet
    
    p_a = pyarts.xml.load(ROOT + "/data/grids/p_grid_137.xml").value
    t_raw_iter = pyarts.xml.load(ROOT + "/data/grids/24010418_t.xml")
    t_raw = [val for val in t_raw_iter]
    ws.p_grid = p_a
    ws.lat_grid = np.linspace(50, 80)
    ws.lon_grid = np.linspace(10, 30)
    ws.refellipsoidEarth(model="Sphere")
    ws.z_surfaceConstantAltitude(altitude=410)
    dt = datetime.strptime("24010418", "%y%m%d%H")
    temperature = get_temperature(dt)
    ws.t_surface = temperature + np.ones_like(ws.z_surface.value)

    # %% Atmosphere
    ws.AtmRawRead(basename=ATMBASE)
    data = pyarts.arts.GriddedField3(
        [p_a, [0], [0]],
        np.array(t_raw).reshape(len(p_a), 1, 1),
        gridnames=["Pressure", "Latitude", "Longitude"],
    )
    ws.t_field_raw = data
    ws.AtmosphereSet3D()
    ws.AtmFieldsCalcExpand1D()
    ws.Touch(ws.wind_u_field)
    ws.Touch(ws.wind_v_field)
    ws.Touch(ws.wind_w_field)
    ws.MagFieldsCalcIGRF(time=pyarts.arts.Time("2024-12-15 21:00:00"))
    ws.cloudboxOff()

    # %% Sensor
    ws.stokes_dim = 4
    ws.f_grid = np.linspace(START, END, 10000)
    ws.sensor_pos = [[460, 67.9, 20.4]]
    ws.sensor_los = [[77.6, 90]]
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

    I = ws.y.value[0::4]
    Q = ws.y.value[1::4]
    U = ws.y.value[2::4]
    V = ws.y.value[3::4]
    f = ws.f_grid.value
    return I, Q, U, V, f


# --- driver code ---
bools = (True, False)
for b in bools:
    if b:
        filename = "ycalc_O2_zeeman_on"
    else:
        filename = "ycalc_O2_zeeman_off"
    I, Q, U, V, f = ycalc(zeeman=b)
    save_ycalc(I, Q, U, V, f, filename)

