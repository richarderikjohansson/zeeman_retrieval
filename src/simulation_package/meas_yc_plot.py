import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib as mpl

from .files import find_file, find_files, imgs_path
from .hdf import get_bound, read_hdf5, read_mag, mm_scaler


def meas_plot():
    """Function to plot measurement related data"""
    labelsize = 18
    ticksize = 16
    path = find_file(filename="Data_2024-01-04_15-06-38_RPGFFTS.hdf5")
    measurement = read_hdf5(path)
    f0 = 233.9461e9  # linecenter
    s = 4635
    e = 5028

    # full spectrum plot
    freq = measurement["f"][20::]
    spec = measurement["y"][20::]
    s, e = get_bound(data=freq, f0=f0)

    xmin, xmax, ymin, ymax = freq[s] / 1e9, freq[e] / 1e9, 120, 134
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(freq / 1e9, spec, color="black")
    ax.tick_params(axis="both", labelsize=ticksize)
    ax.set_xlabel(r"$\nu$ [GHz]", fontsize=labelsize)
    ax.set_ylabel(r"$T_B$ [K]", fontsize=labelsize)
    ax.minorticks_on()

    inset_ax = inset_axes(ax, width="30%", height="50%", loc="center")
    inset_ax.plot(freq / 1e9, spec, color="black")
    inset_ax.set_xlim(xmin, xmax)
    inset_ax.set_ylim(ymin, ymax)
    inset_ax.set_title(
         r"Line center of $^{16}O^{18}O$",
         fontsize=15,
    )
    inset_ax.minorticks_on()
    inset_ax.tick_params(axis='x', labelbottom=False)
    inset_ax.grid(True, alpha=0.25)
    inset_ax.yaxis.set_label_position("right")
    inset_ax.yaxis.tick_right()
    imgpath = imgs_path()

    mark_inset(ax, inset_ax, loc1=2, loc2=3, fc="none", ec="0.5")
    plt.tight_layout()
    fig.savefig(imgpath / "fig02.pdf", transparent=True)


def mag_plot():
    """Function to plot magnetic field data"""
    mag_file = find_file(filename="magfield.hdf5")
    bfield = read_mag(mag_file)
    fill_range = [53, 53.5]

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

    fig, ax = plt.subplots(figsize=(14, 5))
    formatter = mpl.dates.DateFormatter("%H")
    ax.xaxis.set_major_formatter(formatter)
    ax.tick_params(axis="both", labelsize=18)
    ax.set_ylabel(r"B [$\mu T$]", fontsize=20)
    ax.set_xlabel(r"Hours [$CET$]", fontsize=20)
    ax.plot(bfield["dt"], bfield["bfield"] / 1e3, color="black")
    ax.fill_betweenx(
        y=fill_range,
        x1=mdates.date2num(fills["a"][0]),
        x2=mdates.date2num(fills["a"][1]),
        color="lightgray",
        edgecolor="gray",
    )
    ax.fill_betweenx(
        y=fill_range,
        x1=mdates.date2num(fills["b"][0]),
        x2=mdates.date2num(fills["b"][1]),
        color="lightgray",
        edgecolor="gray",
    )
    ax.fill_betweenx(
        y=fill_range,
        x1=mdates.date2num(fills["c"][0]),
        x2=mdates.date2num(fills["c"][1]),
        color="lightgray",
        edgecolor="gray",
    )
    ax.fill_betweenx(
        y=fill_range,
        x1=mdates.date2num(fills["d"][0]),
        x2=mdates.date2num(fills["d"][1]),
        color="lightgray",
        edgecolor="gray",
    )
    ax.text(
        0.188,
        0.90,
        r"$(a)$",
        transform=ax.transAxes,
        fontsize=20,
        color="black",
        verticalalignment="top",
    )
    ax.text(
        0.2655,
        0.90,
        r"$(b)$",
        transform=ax.transAxes,
        fontsize=20,
        color="black",
        verticalalignment="top",
    )
    ax.text(
        0.625,
        0.90,
        r"$(c)$",
        transform=ax.transAxes,
        fontsize=20,
        color="black",
        verticalalignment="top",
    )
    ax.text(
        0.664,
        0.90,
        r"$(d)$",
        transform=ax.transAxes,
        fontsize=20,
        color="black",
        verticalalignment="top",
    )
    ax.set_ylim((53, 53.5))
    plt.tight_layout()
    imgpath = imgs_path()
    fig.savefig(imgpath / "fig04.pdf")


def meas_sim_comparison():
    """Function to plot measurement and simulation

    Plots comparison between measured spectras and simulated in
    four different lines of sight: 0, 90, 180 and 270 deg
    """
    measp, simp = find_files()
    meas = [read_hdf5(file) for file in sorted(measp)]
    sims = [read_hdf5(file) for file in sorted(simp)]
    hmap = {0: "0", 90: "90", 180: "180", -90: "270"}
    measurements = {}
    simulations = {}

    for m in meas:
        azimuth = m["azimuth"]
        measurements[hmap[azimuth]] = m

    for s in sims:
        azimuth = s["azimuth"]
        simulations[hmap[azimuth]] = s

    f0 = 233.9461e9
    s = 4635
    e = 5028

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
        ncols=2,
        nrows=2,
        figsize=(15, 9),
        sharey=True,
        sharex=True,
    )

    # phi = 0
    ax1.plot(
        (measurements["0"]["f"][s:e] - f0) / 1e6,
        mm_scaler(measurements["0"]["y"][s:e]),
        label="Measurement",
        color="black",
    )
    ax1.plot(
        (simulations["0"]["f_grid"] - f0) / 1e6,
        mm_scaler(simulations["0"]["sI"] + simulations["0"]["sQ"]),
        label="Simulation (I+Q)",
        color="red",
    )
    ax1.legend(
        loc="best",
        fontsize=12,
        frameon=True,
        bbox_to_anchor=(0.97, 0.95),
    )
    ax1.set_ylabel(r"$T_B$" + " (Normalized)", fontsize=16)
    ax1.tick_params(axis="both", labelsize=13)
    ax1.minorticks_on()
    ax1.grid(
        which="major",
        color="black",
        linestyle="-",
        linewidth=0.75,
        alpha=0.2,
    )
    ax1.grid(
        which="minor",
        color="gray",
        linestyle=":",
        linewidth=0.5,
        alpha=0.2,
    )
    ax1.text(
        0.10,
        0.90,
        r"$(a)$",
        transform=ax1.transAxes,
        fontsize=17,
        color="black",
        verticalalignment="top",
    )

    # phi = 180
    ax2.plot(
        (measurements["180"]["f"][s:e] - f0) / 1e6,
        mm_scaler(measurements["180"]["y"][s:e]),
        label="Measurement",
        color="black",
    )
    ax2.plot(
        (simulations["180"]["f_grid"] - f0) / 1e6,
        mm_scaler(simulations["180"]["sI"] + simulations["180"]["sQ"]),
        label="Simulation (I+Q)",
        color="red",
    )
    ax2.legend(
        loc="best",
        fontsize=12,
        frameon=True,
        bbox_to_anchor=(0.97, 0.95),
    )
    ax2.tick_params(axis="both", labelsize=13)
    ax2.minorticks_on()
    ax2.grid(
        which="major",
        color="black",
        linestyle="-",
        linewidth=0.75,
        alpha=0.2,
    )
    ax2.grid(
        which="minor",
        color="gray",
        linestyle=":",
        linewidth=0.5,
        alpha=0.2,
    )
    ax2.text(
        0.10,
        0.90,
        r"$(b)$",
        transform=ax2.transAxes,
        fontsize=17,
        color="black",
        verticalalignment="top",
    )

    # phi = 90
    ax3.plot(
        (measurements["90"]["f"][s:e] - f0) / 1e6,
        mm_scaler(measurements["90"]["y"][s:e]),
        label="Measurement",
        color="black",
    )
    ax3.plot(
        (simulations["90"]["f_grid"] - f0) / 1e6,
        mm_scaler(simulations["90"]["sI"] - simulations["90"]["sQ"]),
        label="Simulation (I-Q)",
        color="red",
    )
    ax3.legend(
        loc="best",
        fontsize=12,
        frameon=True,
        bbox_to_anchor=(0.97, 0.95),
    )
    ax3.set_xlabel(r"$\nu - \nu_0$ [MHz]", fontsize=16)
    ax3.set_ylabel(r"$T_B$" + " (Normalized)", fontsize=16)
    ax3.tick_params(axis="both", labelsize=13)
    ax3.minorticks_on()
    ax3.grid(
        which="major",
        color="black",
        linestyle="-",
        linewidth=0.75,
        alpha=0.2,
    )
    ax3.grid(
        which="minor",
        color="gray",
        linestyle=":",
        linewidth=0.5,
        alpha=0.2,
    )
    ax3.text(
        0.10,
        0.90,
        r"$(c)$",
        transform=ax3.transAxes,
        fontsize=17,
        color="black",
        verticalalignment="top",
    )

    # phi = 270
    ax4.plot(
        (measurements["270"]["f"][s:e] - f0) / 1e6,
        mm_scaler(measurements["270"]["y"][s:e]),
        label="Measurement",
        color="black",
    )
    ax4.plot(
        (simulations["270"]["f_grid"] - f0) / 1e6,
        mm_scaler(simulations["270"]["sI"] - simulations["270"]["sQ"]),
        label="Simulation (I-Q)",
        color="red",
    )
    ax4.legend(
        loc="best",
        fontsize=12,
        frameon=True,
        bbox_to_anchor=(0.97, 0.95),
    )
    ax4.set_xlabel(r"$\nu - \nu_0$ [MHz]", fontsize=16)
    ax4.tick_params(axis="both", labelsize=13)
    ax4.minorticks_on()
    ax4.grid(
        which="major",
        color="black",
        linestyle="-",
        linewidth=0.75,
        alpha=0.2,
    )
    ax4.grid(
        which="minor",
        color="gray",
        linestyle=":",
        linewidth=0.5,
        alpha=0.2,
    )
    ax4.text(
        0.10,
        0.90,
        r"$(d)$",
        transform=ax4.transAxes,
        fontsize=17,
        color="black",
        verticalalignment="top",
    )
    plt.tight_layout()
    imgpath = imgs_path()

    fig.savefig(imgpath / "fig03.pdf", transparent=True)
