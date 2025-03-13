import pyarts
import numpy as np
from simulation_package.hdf import DottedDict
import subprocess


def get_git_root():
    try:
        return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], universal_newlines=True).strip()
    except subprocess.CalledProcessError:
        return None  # Not inside a Git repo


def make_atm_grids(start, disturb_flag=False, index=None):
    grids_path = f"{get_git_root()}/data/grids"
    z = pyarts.xml.load(f"{grids_path}/24010418_z.xml")
    t = pyarts.xml.load(f"{grids_path}/24010418_t.xml")
    p = pyarts.xml.load(f"{grids_path}/p_grid_137.xml")
    apriori = pyarts.xml.load(f"{grids_path}/ECMWF_jan.xml")

    z = z.to_dict()["data"]
    t = t.to_dict()["data"]

    grids = DottedDict(
        {
            "temperature": np.array([i[0][0] for i in t]),
            "altitude": np.array([i[0][0] for i in z]),
            "pressure": np.array([i for i in p]),
            "apriori": np.array([i for i in apriori]),
        }
    )

    s = np.where(grids.altitude >= start)[0][0]
    altered_grids = DottedDict(
        {
            "temperature": grids.temperature[s:],
            "altitude": grids.altitude[s:],
            "pressure": grids.pressure[s:],
            "apriori": grids.apriori[s:],
            "plen": len(grids.pressure[s:])
        }
    )
    if disturb_flag and index is not None:
        altered_grids = distrub(altered_grids, index)
    return altered_grids


def distrub(grids, index):
    grids.temperature[index] += 5
    return grids
