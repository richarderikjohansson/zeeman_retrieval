import h5py
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import matplotlib as mpl


def read_hdf5(filename):
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


# --- driver code ---


bfield = read_hdf5(filename="data/magfield/240104/magfield.hdf5")

# fill-boundaries associated with measurement
fills = {
    "a": (
        datetime(year=2024, month=1, day=4, hour=3, minute=35, second=9),
        datetime(year=2024, month=1, day=4, hour=4, minute=35, second=9),
    ),
    "b": (
        datetime(year=2024, month=1, day=4, hour=5, minute=37, second=27),
        datetime(year=2024, month=1, day=4, hour=6, minute=37, second=27),
    ),
    "c": (
        datetime(year=2024, month=1, day=4, hour=15, minute=6, second=38),
        datetime(year=2024, month=1, day=4, hour=16, minute=6, second=38),
    ),
    "d": (
        datetime(year=2024, month=1, day=4, hour=16, minute=7, second=17),
        datetime(year=2024, month=1, day=4, hour=17, minute=7, second=17),
    ),
}

# plot magfield strength with fills corresponding to KIMRA measurements
fig, ax = plt.subplots(figsize=(14, 5))
formatter = mpl.dates.DateFormatter("%H")  # pyright:ignore
ylim=(53.000, 53.500)
ax.xaxis.set_major_formatter(formatter)
ax.tick_params(axis="both", labelsize=23)
ax.set_ylabel(r"B [$\mu T$]", fontsize=25)
ax.set_xlabel(r"Hours [$CET$]", fontsize=25)
ax.plot(bfield["dt"], bfield["bfield"]/1e3, color="black")
ax.fill_betweenx(
    y=[ylim[0], ylim[1]],
    x1=mdates.date2num(fills["a"][0]),
    x2=mdates.date2num(fills["a"][1]),
    color="lightgray",
    edgecolor="gray",
)
ax.fill_betweenx(
    y=[ylim[0], ylim[1]],
    x1=mdates.date2num(fills["b"][0]),
    x2=mdates.date2num(fills["b"][1]),
    color="lightgray",
    edgecolor="gray",
)
ax.fill_betweenx(
    y=[ylim[0],ylim[1]],
    x1=mdates.date2num(fills["c"][0]),
    x2=mdates.date2num(fills["c"][1]),
    color="lightgray",
    edgecolor="gray",
)
ax.fill_betweenx(
    y=[ylim[0],ylim[1]],
    x1=mdates.date2num(fills["d"][0]),
    x2=mdates.date2num(fills["d"][1]),
    color="lightgray",
    edgecolor="gray",
)
ax.text(
    0.184,
    0.90,
    r"$(a)$",
    transform=ax.transAxes,
    fontsize=20,
    color="black",
    verticalalignment="top",
)
ax.text(
    0.2615,
    0.90,
    r"$(b)$",
    transform=ax.transAxes,
    fontsize=20,
    color="black",
    verticalalignment="top",
)
ax.text(
    0.621,
    0.90,
    r"$(c)$",
    transform=ax.transAxes,
    fontsize=20,
    color="black",
    verticalalignment="top",
)
ax.text(
    0.660,
    0.90,
    r"$(d)$",
    transform=ax.transAxes,
    fontsize=20,
    color="black",
    verticalalignment="top",
)
ax.set_ylim(ylim)
plt.tight_layout()

fig.savefig("imgs/fig04.pdf")
