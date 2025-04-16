import os
from datetime import datetime, timedelta

import h5py
import numpy as np


class DottedDict:
    """
     Class to create DottedDict object which is takes an dictionary and
     sets attributes from keys.

     It also handles nested dictionaries

    Args:
        dictionary (dict):

    Returns:
        (DottedDict): object with attributes for each key

    """

    def __init__(self, dictionary):
        # unravels nested dictionaries with recursion
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = DottedDict(value)
            self.__dict__[key] = value

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def attr(self, key=None):
        """
        Return the attributes of the object back as keys. Useful if
        you have to represent the attributes as keys again in a loop
        for example

        Returns:
            (dict_keys): attributes as keys

        """
        return self.__dict__.keys()

    def to_dict(self):
        return self.__dict__


def read_hdf5(filename: str) -> dict:
    """Function to read HDF5 file

    Args:
        filename: Name of the file

    Returns:
       Dictionary with key value pairs with data
    """
    with h5py.File(filename, "r") as file:
        if "kimra_data" in file.keys():
            dataset = file["kimra_data"]
        else:
            dataset = file

        dictionary = dict()
        for key in dataset.keys():
            try:
                dictionary[key] = dataset[key][:]
            except ValueError:
                dictionary[key] = dataset[key][()]

        return dictionary


def read_mag(filename: str) -> dict:
    """Function to read magnetic field data

    Args:
        filename: Name of the file

    Returns:
        Dictionary with key value pairs with data
    """
    with h5py.File(filename, "r") as file:
        start = file["start"][()].decode("utf-8")  # pyright:ignore
        end = file["end"][()].decode("utf-8")  # pyright:ignore
        bfield = file["B"][:]  # pyright:ignore

        dt = make_date(start, end)

        return {"dt": dt, "bfield": bfield}


def save_ret(ROOT: str, filename: str, *argv) -> None:
    """Function to save retrieval data

    Args:
        ROOT: File path to repository base
        filename: Save name of the data with retrieval
    """
    savepath = f"{ROOT}/data/retrieval"
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    with h5py.File(f"{savepath}/{filename}", "w") as file:
        for data in argv:
            file[data.name] = data.value


def mm_scaler(data: np.ndarray) -> np.ndarray:
    """Scaling data [0,1]

    Args:
        data: Array with data

    Returns:
        Scaled data
    """

    minval = min(data)
    maxval = max(data)

    norm_data = (data - minval) / (maxval - minval)
    return norm_data


def get_bound(data: np.ndarray, f0: float) -> tuple:
    """Function to get indexes

    Get indexes +- 15 Mhz from line center f0 for the frequency array
    data

    Args:
        data: Frequency array
        f0: Line center

    Returns:
        Tuple with start and end indexes
    """
    f = data - f0
    s = np.where(f > -1.5e7)[0][0]
    e = np.where(f > 1.5e7)[0][0]

    return s, e


def make_date(start: str, end: str) -> np.ndarray:
    """Function to make datetime range

    Creates a datetime range from a start date 'start' to an
    end date 'end' with 1 second increments

    Args:
        start: Start date
        end: End date

    Returns:
        Array with datetime values
    """
    dt_start = datetime.strptime(start, "%y%m%d")
    dt_end = datetime.strptime(end, "%y%m%d")
    date_range = []
    current_date = dt_start

    while current_date < dt_end:
        date_range.append(current_date)
        current_date += timedelta(seconds=1)
    return np.array(date_range)
