import h5py
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import numpy as np
import matplotlib as mpl
from matplotlib.gridspec import GridSpec


def read_hdf5(filename, mag):
    """
    Function to read hdf5 files

    Parameters:
    filename (str) : path to the file
    mag (bool) : flag if the file is either magnetic field data or spectra/simulation

    Returns:
    dictionary (dict): A dictionary with the data
    """

    with h5py.File(filename, "r") as file:
        if mag:
            with h5py.File(filename, "r") as file:
                start = file["start"][()].decode("utf-8")  # pyright:ignore
                end = file["end"][()].decode("utf-8")  # pyright:ignore
                bfield = file["B"][:]  # pyright:ignore

                dt = make_date(start, end)

                return {"dt": dt, "bfield": bfield}

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


# --- driver code ---
measurement = read_hdf5(
    filename=f"data/measurements/231202/{os.listdir('data/measurements/231202/')[0]}",
    mag=False,
)
simulation = read_hdf5(
    filename=f"data/simulation/{os.listdir('data/simulation/')[-1]}", mag=False
)
bfield2 = read_hdf5(filename="data/magfield/231202/magfield.hdf5", mag=True)

s = 4635  # index where frequency is -15 MHz from linecenter
e = 5028  # index where frequency is 15 MHz from linecenter
f0 = 233.9461e9  # line-center


norm_sim = mm_scaler(data=simulation["I"] - simulation["Q"])
norm_meas = mm_scaler(data=measurement["y"][s:e])

fill = [
    datetime(year=2023, month=12, day=2, hour=1, minute=40, second=4),
    datetime(year=2023, month=12, day=2, hour=3, minute=40, second=17),
]

fig = plt.figure(figsize=(17, 9))
gs = GridSpec(2, 3, figure=fig, height_ratios=[1.5, 1], width_ratios=[0.75, 2, 0.75])
ax_lower = fig.add_subplot(gs[1, :])
formatter = mpl.dates.DateFormatter("%H")  # pyright:ignore
ax_lower.xaxis.set_major_formatter(formatter)
ax_lower.tick_params(axis="both", labelsize=24)
ax_lower.set_ylabel(r"B [$\mu T$]", fontsize=27)
ax_lower.set_xlabel(r"Hours [$CET$]", fontsize=27)
ax_lower.plot(bfield2["dt"], bfield2["bfield"] / 1e3, color="black")
ax_lower.fill_betweenx(
    y=[53.000, 53.500],
    x1=mdates.date2num(fill[0]),
    x2=mdates.date2num(fill[1]),
    color="lightgray",
    edgecolor="gray",
)
ax_lower.set_ylim((53.000, 53.500))

ax_lower.set_xlim(
    (
        datetime(year=2023, month=12, day=1, hour=23, minute=0, second=0),  # pyright:ignore
        datetime(year=2023, month=12, day=2, hour=15, minute=0, second=0),
    )
)

ax_upper = fig.add_subplot(gs[0, 1])
ax_upper.plot(
    (measurement["f"][s:e] - f0) / 1e6, norm_meas, label="Measurement", color="black"
)
ax_upper.plot(simulation["f"], norm_sim, label="Simulation (I-Q)", color="red")
ax_upper.set_ylabel(r"$T_B$ (Normalized)", fontsize=27)
ax_upper.set_xlabel(r"$\nu - \nu_0$ [MHz]", fontsize=27)
ax_upper.tick_params(axis="both", labelsize=24)
ax_upper.minorticks_on()
ax_upper.grid(which="major", color="black", linestyle="-", linewidth=0.75, alpha=0.2)
ax_upper.grid(which="minor", color="gray", linestyle=":", linewidth=0.5, alpha=0.2)
ax_upper.legend(loc="best", fontsize=17, frameon=True)
ax_upper.text(
    0.63,
    0.75,
    rf"$\phi\;=${round(measurement['azimuth'])}$^\circ$",
    transform=ax_upper.transAxes,
    fontsize=17,
    color="black",
    verticalalignment="top",
)
ax_upper.text(
    0.63,
    0.67,
    rf"$\theta_z=${measurement['za']}$^\circ$",
    transform=ax_upper.transAxes,
    fontsize=17,
    color="black",
    verticalalignment="top",
)
plt.tight_layout()
plt.close()

fig.savefig("imgs/fig05.pdf", transparent=True)
