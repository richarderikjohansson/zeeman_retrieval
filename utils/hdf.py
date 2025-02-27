import os
from datetime import datetime, timedelta

import h5py
import numpy as np
import pandas as pd


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
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

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
        for key in dataset.keys():
            try:
                dictionary[key] = dataset[key][:]
            except ValueError:
                dictionary[key] = dataset[key][()]

        return dictionary


def read_mag(filename):
    """
    Function to read .hdf5 file

    Parameters:
    filename (str) : path to the file

    Returns:
    (dct) : dictionary with magnetic field strength and datetime

    """
    with h5py.File(filename, "r") as file:
        start = file["start"][()].decode("utf-8")  # pyright:ignore
        end = file["end"][()].decode("utf-8")  # pyright:ignore
        bfield = file["B"][:]  # pyright:ignore

        dt = make_date(start, end)

        return {"dt": dt, "bfield": bfield}


def save_ret(ROOT, filename, *argv):
    """
    Function to save retrieval data in hdf5 file in data/retrieval in current working directory

    Parameters:
    filename (str): name of the file
    argv (pyarts.arts.Workspace.variable): workspace variables we want to save
    """

    savepath = f"{ROOT}/data/retrieval"
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    with h5py.File(f"{savepath}/{filename}", "w") as file:
        for data in argv:
            file[data.name] = data.value


def mm_scaler(data):
    """
    A min max scaler function to scale the normalize the measurements so
    their features can be distinguished and compared

    Parameters:
    data (np.array) : The spectra to be normalzed

    Returns:

    (np.array) : The normalized spectra

    """

    minval = min(data)
    maxval = max(data)

    norm_data = (data - minval) / (maxval - minval)
    return norm_data


def get_bound(data, f0):
    """
    Function to get start end end index from frequency where the bandwith is 30 MHz
    and from a line center

    Parameters:
    data (np.array) : Frequency vector
    f0 (float) : Line center

    Returns:
    s (int) : Start index of slice
    s (int) : End index of slice
    """

    f = data - f0
    s = np.where(f > -1.5e7)[0][0]
    e = np.where(f > 1.5e7)[0][0]

    return s, e


def make_date(start, end):
    """
    Function to create a date range

    Parameters:
    start (str) : start date of in YYMMDD
    end (str) : end date in YYMMDD


    Returns:
    date_range (np.array) : numpy array containing datetimes
    """
    dt_start = datetime.strptime(start, "%y%m%d")
    dt_end = datetime.strptime(end, "%y%m%d")
    date_range = []
    current_date = dt_start

    while current_date < dt_end:
        date_range.append(current_date)
        current_date += timedelta(seconds=1)
    return np.array(date_range)


def grab_mag(filename, start_gmt, end_gmt, start, end, save_name):
    """
    Function to parse magnetic field data and save data in .hdf5 format

    Parameters:
    filename (str) : path to the file
    start_gmt (datetime) : start of data in CET
    start_gmt (datetime) : end of data in CET
    start (str) : start date for data
    end (str) : end date for data
    save_name (str) : path where the .hdf5 file should be saved

    """

    df = pd.read_csv(filename, skiprows=12, sep="\s+")

    dt = list()
    for date, time in zip(df["DATE"], df["TIME"]):
        hms = time.split(".")[0]
        dt.append(datetime.strptime(f"{date} {hms}", "%Y-%m-%d %H:%M:%S"))

    B = np.array([b for b in df["KIRF"]])

    # magfield in UTC spec in CET need to get correct data
    s = np.where(np.array(dt) >= start_gmt)[0][0]
    e = np.where(np.array(dt) >= end_gmt)[0][0]

    # save data between as .hdf5
    with h5py.File(f"{save_name}.hdf5", "w") as file:
        file["B"] = B[s:e]
        file["start"] = start
        file["end"] = end
