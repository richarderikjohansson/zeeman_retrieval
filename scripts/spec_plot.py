import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
from utils.hdf import read_hdf5, mm_scaler, get_bound
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

# --- functions ---




# --- driver code ---

f0 = 233.9461e9  # linecenter
s = 4635  # index where frequency is -15 MHz from linecenter
e = 5028  # index where frequency is 15 MHz from linecenter


# list comprehensions to read all data
simulations = [
    read_hdf5("data/simulation/" + file)
    for file in sorted(os.listdir("data/simulation"))
]
measurements = [
    read_hdf5("data/measurements/240104/" + file)
    for file in sorted(os.listdir("data/measurements/240104"))
]

# subplots all directions
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
    ncols=2, nrows=2, figsize=(15, 9), sharey=True, sharex=True
)

# phi = 0
ax1.plot(
    (measurements[0]["f"][s:e] - f0) / 1e6,
    mm_scaler(measurements[0]["y"][s:e]),
    label="Measurement",
    color="black",
)
ax1.plot(
    simulations[0]["f"],
    mm_scaler(simulations[0]["I"] + simulations[0]["Q"]),
    label="Simulation (I+Q)",
    color="red",
)
ax1.legend(loc="best", fontsize=12, frameon=True, bbox_to_anchor=(0.97, 0.95))
ax1.set_ylabel(r"$T_B$" + " (Normalized)", fontsize=20)
ax1.tick_params(axis="both", labelsize=18)
ax1.minorticks_on()
ax1.grid(which="major", color="black", linestyle="-", linewidth=0.75, alpha=0.2)
ax1.grid(which="minor", color="gray", linestyle=":", linewidth=0.5, alpha=0.2)
ax1.text(
    0.10,
    0.90,
    r"$(a)$",
    transform=ax1.transAxes,
    fontsize=17,
    color="black",
    verticalalignment="top",
)
ax1.text(
    0.67,
    0.75,
    rf"$\phi\;=${round(measurements[0]['azimuth'])}$^\circ$",
    transform=ax1.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)
ax1.text(
    0.67,
    0.67,
    rf"$\theta_z=${measurements[0]['za']}$^\circ$",
    transform=ax1.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)

# phi = 180
ax2.plot(
    (measurements[1]["f"][s:e] - f0) / 1e6,
    mm_scaler(measurements[1]["y"][s:e]),
    label="Measurement",
    color="black",
)
ax2.plot(
    simulations[1]["f"],
    mm_scaler(simulations[1]["I"] + simulations[1]["Q"]),
    label="Simulation (I+Q)",
    color="red",
)
ax2.legend(loc="best", fontsize=12, frameon=True, bbox_to_anchor=(0.97, 0.95))
ax2.tick_params(axis="both", labelsize=18)
ax2.minorticks_on()
ax2.grid(which="major", color="black", linestyle="-", linewidth=0.75, alpha=0.2)
ax2.grid(which="minor", color="gray", linestyle=":", linewidth=0.5, alpha=0.2)
ax2.text(
    0.10,
    0.90,
    r"$(b)$",
    transform=ax2.transAxes,
    fontsize=17,
    color="black",
    verticalalignment="top",
)
ax2.text(
    0.67,
    0.75,
    rf"$\phi\;=${round(measurements[1]['azimuth'])}$^\circ$",
    transform=ax2.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)
ax2.text(
    0.67,
    0.67,
    rf"$\theta_z=${measurements[1]['za']}$^\circ$",
    transform=ax2.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)

# phi = 90
ax3.plot(
    (measurements[2]["f"][s:e] - f0) / 1e6,
    mm_scaler(measurements[2]["y"][s:e]),
    label="Measurement",
    color="black",
)
ax3.plot(
    simulations[3]["f"],
    mm_scaler(simulations[3]["I"] - simulations[3]["Q"]),
    label="Simulation (I-Q)",
    color="red",
)
ax3.legend(loc="best", fontsize=12, frameon=True, bbox_to_anchor=(0.97, 0.95))
ax3.set_xlabel(r"$\nu - \nu_0$ [MHz]", fontsize=20)
ax3.set_ylabel(r"$T_B$" + " (Normalized)", fontsize=20)
ax3.tick_params(axis="both", labelsize=18)
ax3.minorticks_on()
ax3.grid(which="major", color="black", linestyle="-", linewidth=0.75, alpha=0.2)
ax3.grid(which="minor", color="gray", linestyle=":", linewidth=0.5, alpha=0.2)
ax3.text(
    0.10,
    0.90,
    r"$(c)$",
    transform=ax3.transAxes,
    fontsize=17,
    color="black",
    verticalalignment="top",
)
ax3.text(
    0.68,
    0.75,
    rf"$\phi\;=${round(measurements[2]['azimuth'])}$^\circ$",
    transform=ax3.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)
ax3.text(
    0.68,
    0.67,
    rf"$\theta_z=${measurements[2]['za']}$^\circ$",
    transform=ax3.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)

# phi = 270
ax4.plot(
    (measurements[3]["f"][s:e] - f0) / 1e6,
    mm_scaler(measurements[3]["y"][s:e]),
    label="Measurement",
    color="black",
)
ax4.plot(
    simulations[2]["f"],
    mm_scaler(simulations[2]["I"] - simulations[2]["Q"]),
    label="Simulation (I-Q)",
    color="red",
)
ax4.legend(loc="best", fontsize=12, frameon=True, bbox_to_anchor=(0.97, 0.95))
ax4.set_xlabel(r"$\nu - \nu_0$ [MHz]", fontsize=20)
ax4.tick_params(axis="both", labelsize=18)
ax4.minorticks_on()
ax4.grid(which="major", color="black", linestyle="-", linewidth=0.75, alpha=0.2)
ax4.grid(which="minor", color="gray", linestyle=":", linewidth=0.5, alpha=0.2)
ax4.text(
    0.10,
    0.90,
    r"$(d)$",
    transform=ax4.transAxes,
    fontsize=17,
    color="black",
    verticalalignment="top",
)
ax4.text(
    0.68,
    0.75,
    rf"$\phi\;=${round(measurements[3]['azimuth']) + 360}$^\circ$",
    transform=ax4.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)
ax4.text(
    0.68,
    0.67,
    rf"$\theta_z=${measurements[3]['za']}$^\circ$",
    transform=ax4.transAxes,
    fontsize=13,
    color="black",
    verticalalignment="top",
)
plt.tight_layout()

fig.savefig("imgs/fig03.pdf", transparent=True)

# full spectrum plot
freq = measurements[2]["f"][20::]
spec = measurements[2]["y"][20::]
s, e = get_bound(data=freq, f0=f0)

xmin, xmax, ymin, ymax = freq[s] / 1e9, freq[e] / 1e9, 120, 134
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(freq / 1e9, spec, color="black")
ax.tick_params(axis="both", labelsize=23)
ax.set_xlabel(r"$\nu$ [GHz]", fontsize=25)
ax.set_ylabel(r"$T_B$ [K]", fontsize=25)

inset_ax = inset_axes(ax, width="40%", height="60%", loc="center")
inset_ax.plot(freq / 1e9, spec, color="black")
inset_ax.set_xlim(xmin, xmax)
inset_ax.set_ylim(ymin, ymax)
inset_ax.set_title(r"Zeeman affected transition of $^{16}O^{18}O$", fontsize=20)

# Mark the zoomed area on the main plot
inset_ax.set_xticks([])
inset_ax.set_yticks([])
inset_ax.tick_params(left=False, bottom=False)  # Hide tick marks

mark_inset(ax, inset_ax, loc1=2, loc2=3, fc="none", ec="0.5")
plt.tight_layout()

fig.savefig("imgs/fig02.pdf", transparent=True)
