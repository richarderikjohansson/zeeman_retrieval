import pyarts
import os
import numpy as np
from simulation_package.make_grids import make_atm_grids
from simulation_package.files import find_file, find_dir
import h5py


def set_abs_file(line):
    match line:
        case "tempera":
            abs_lines_per_species_file = find_file(filename="tempera.xml")
        case "kimra":
            abs_lines_per_species_file = find_file(filename="kimra.xml")
    return abs_lines_per_species_file


def save_ycalc(zenith, azimuth, sI, sQ, sU, sV, filename, *argv):
    savepath = find_dir(dirname="simulation")
    with h5py.File(f"{savepath}/{filename}", "w") as file:
        for data in argv:
            file[data.name] = data.value
        file["azimuth"] = azimuth
        file["za"] = zenith
        file["sI"] = sI
        file["sQ"] = sQ
        file["sU"] = sU
        file["sV"] = sV


def set_arts_path():
    home = os.getenv("HOME")
    arts_catalogue_path = f"{home}/.cache/arts/"

    if not os.path.exists(arts_catalogue_path):
        pyarts.cat.download.retrieve(verbose=True)

    arts_catalogue_directory = f"{arts_catalogue_path}/arts-cat-data-2.6.10"
    arts_xml_directory = f"{arts_catalogue_path}/arts-xml-data-2.6.10"
    return arts_catalogue_directory, arts_xml_directory


def set_jacobian(ws, pressure, latitude, longitude):
    ws.jacobianInit()
    ws.jacobianAddTemperature(g1=pressure, g2=[latitude], g3=[longitude])
    ws.jacobianClose()
    return ws


def set_line(ws, line, flen, zeeman):
    f0 = 233.9461e9
    f = np.linspace(f0 - 15e6, f0 + 15e6, flen)

    start = f[0]
    stop = f[-1]
    ws.f_grid = f
    if zeeman:
        ws.abs_speciesSet(
            species=[
                f"O2-Z-*-{start - 1}-{stop + 1}",
                f"O3-*-{start - 1}-{stop + 1}",
                "N2-SelfContStandardType",
                "H2O-PWR98",
            ]
        )
    else:
        ws.abs_speciesSet(
            species=[
                f"O2-*-{start - 1}-{stop + 1}",
                f"O3-*-{start - 1}-{stop + 1}",
                "N2-SelfContStandardType",
                "H2O-PWR98",
            ]
        )
    return ws


def set_atm_grids(start, disturb_flag=False, index=None):
    grids = make_atm_grids(start=0, disturb_flag=disturb_flag, index=index)
    return grids


def ycalc_zeeman(
    zenith, azimuth, zeeman, line, filename, disturb_flag=False, index=None
):
    ARTS_CAT, ARTS_XML = set_arts_path()
    ATMBASE = f"{ARTS_XML}/planets/Earth/Fascod/subarctic-winter/subarctic-winter"
    LAT = 67.8
    LON = 20.22
    FLEN = 5000

    ws = pyarts.workspace.Workspace()
    ws = set_line(ws=ws, line=line, flen=FLEN, zeeman=zeeman)
    abs_lines_per_species_file = set_abs_file(line=line)
    grids = set_atm_grids(start=0, disturb_flag=disturb_flag, index=index)

    ws.ppath_agendaSet(option="FollowSensorLosPath")
    ws.iy_main_agendaSet(option="Emission")
    ws.surface_rtprop_agendaSet(option="Blackbody_SurfTFromt_surface")
    ws.ppath_step_agendaSet(option="GeometricPath")
    ws.iy_space_agendaSet()
    ws.iy_surface_agendaSet()
    ws.water_p_eq_agendaSet()
    ws.iy_unit = "PlanckBT"
    ws.ppath_lmax = 10e3
    ws.ppath_lraytrace = 1e3
    ws.rt_integration_option = "default"
    ws.rte_alonglos_v = 0.0
    ws.nlteOff()

    ws.Wigner6Init()
    ws.ReadXML(ws.abs_lines_per_species, str(abs_lines_per_species_file))
    ws.propmat_clearsky_agendaAuto()

    ws.p_grid = grids.pressure
    ws.lat_grid = np.linspace(50, 80)
    ws.lon_grid = np.linspace(-180, 180)
    ws.refellipsoidEarth(model="Sphere")

    ws.AtmRawRead(basename=ATMBASE)
    data = pyarts.arts.GriddedField3(
        [grids.pressure, [0], [0]],
        np.array(grids.temperature).reshape(grids.plen, 1, 1),
        gridnames=["Pressure", "Latitude", "Longitude"],
    )

    ws.t_field_raw = data

    ws.AtmosphereSet3D()
    ws.AtmFieldsCalcExpand1D()
    z0 = min(ws.z_field.value[:, :, :].flatten())
    ws.z_surfaceConstantAltitude(altitude=z0)
    ws.t_surface = grids.temperature[0] + np.ones_like(ws.z_surface.value)
    ws.Touch(ws.wind_u_field)
    ws.Touch(ws.wind_v_field)
    ws.Touch(ws.wind_w_field)
    ws.MagFieldsCalcIGRF(time=pyarts.arts.Time("2024-01-04 19:00:00"))
    ws = set_jacobian(ws=ws, pressure=grids.pressure, latitude=LAT, longitude=LON)
    ws.cloudboxOff()

    if zeeman:
        ws.stokes_dim = 4
    else:
        ws.stokes_dim = 1

    ws.sensor_pos = [[z0 + 30, LAT, LON]]
    ws.sensor_los = [[zenith, azimuth]]
    ws.sensorOff()

    ws.atmgeom_checkedCalc()
    try:
        ws.lbl_checkedCalc()
    except RuntimeError:
        ws.abs_lines_per_speciesReadSpeciesSplitCatalog(basename=f"{ARTS_CAT}/lines/")
        ws.WriteXML(
            output_file_format="binary",
            input=ws.abs_lines_per_species,
            filename=str(abs_lines_per_species_file),
        )
    ws.lbl_checkedCalc()
    ws.atmfields_checkedCalc()
    ws.cloudbox_checkedCalc()
    ws.sensor_checkedCalc()
    ws.propmat_clearsky_agenda_checkedCalc()

    ws.yCalc()
    if zeeman:
        y = ws.y.value[::1].reshape(FLEN, 4)

        # Stokes components
        sI = np.reshape(y[:, 0], (FLEN, 1))
        sQ = np.reshape(y[:, 1], (FLEN, 1))
        sU = np.reshape(y[:, 2], (FLEN, 1))
        sV = np.reshape(y[:, 3], (FLEN, 1))
    else:
        sI = ws.y.value
        sQ = np.zeros(shape=FLEN)
        sU = np.zeros(shape=FLEN)
        sV = np.zeros(shape=FLEN)

    save_ycalc(
        zenith,
        azimuth,
        sI,
        sQ,
        sU,
        sV,
        filename,
        ws.f_grid,
        ws.jacobian,
        ws.p_grid,
        ws.z_field,
    )
