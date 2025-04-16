import pyarts
import numpy as np
from simulation_package.hdf import DottedDict
from simulation_package.files import find_file


def make_atm_grids(
    start: float,
    disturb_flag: bool = False,
    index: int | None = None,
) -> DottedDict:
    """Function to make atmospheric grids

    Args:
        start: Start altitude
        disturb_flag: Boolean if disturbance should be used
        index: Index of where disturbance should be done

    Returns:
        DottedDict object with grids
    """

    z = pyarts.xml.load(
        str(find_file(filename="24010418_z.xml", skip="local")),
    )
    t = pyarts.xml.load(
        str(find_file(filename="24010418_t.xml", skip="local")),
    )
    p = pyarts.xml.load(
        str(find_file(filename="p_grid_137.xml", skip="local")),
    )
    apriori = pyarts.xml.load(
        str(find_file(filename="ECMWF_jan.xml", skip="local")),
    )

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
            "plen": len(grids.pressure[s:]),
        }
    )
    if disturb_flag and index is not None:
        altered_grids = distrub(altered_grids, index)
    return altered_grids


def distrub(grids, index):
    grids.temperature[index] += 5
    return grids
