from utils.hdf import read_hdf5, DottedDict
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import pyarts

# --- Grids and constansts ---
f0 = 233.9461e9  # linecenter
prefix = "data/retrieval/"
retrieval_files = [prefix + file for file in sorted(os.listdir(prefix))]
retrievals = {}
ecmwf = pyarts.xml.load("data/grids/24010418_t.xml").to_dict()
t_true = [value[0][0] for value in ecmwf["data"]]

for file in retrieval_files:
    key = file.split("/")[-1].split(".")[0]
    retrievals[key] = read_hdf5(filename=file)
dd = DottedDict(retrievals)

# --- Simulated spectra ---
fig, ax = plt.subplots(figsize=(8, 4))
settings = DottedDict(
    {
        "xlabel": r"$\nu$ [GHz]",
        "ylabel": r"$T_B$ [K]",
        "yticks": [175, 180, 185, 190],
        "yticks_minor": [177.5, 182.5, 187.5],
        "labelsize": 15,
        "ticksize": 13,
        "legendsize": 11,
        "figname": "imgs/fig06.pdf",
        "grid_alpha": 0.25,
        "plot": {
            "label": "Simulated spectra with noise",
            "color": "black",
        },
    }
)

ax.plot(
    dd.ret_zeeman_on.f_grid / 1e9,
    dd.ret_zeeman_on.y,
    color=settings.plot.color,
    label=settings.plot.label,
)

ax.grid(which="both", axis="both", alpha=settings.grid_alpha)
ax.set_yticks(settings.yticks)
# Automatically place minor ticks
ax.set_yticks(settings.yticks_minor, minor=True)
ax.set_xlabel(settings.xlabel, fontsize=settings.labelsize)
ax.set_ylabel(settings.ylabel, fontsize=settings.labelsize)
ax.tick_params(axis="both", labelsize=settings.ticksize)
ax.legend(fontsize=settings.legendsize)
fig.tight_layout()
fig.savefig(settings.figname, transparent=True)


fig = plt.figure(figsize=(14, 7))
settings = DottedDict(
    {
        "gridspec": {"height_ratio": [0.75, 0.4]},
        "zeeman_on": {"label": "Zeeman on", "color": "black"},
        "zeeman_off": {"label": "Zeeman off", "color": "darkgoldenrod"},
        "zeeman_on_wrong_pol": {
            "label": "Zeeman on (wrong polarization)",
            "color": "red",
        },
        "difference": {"label": "Difference", "color": "dimgray"},
        "xaxis": {"label": r"$\nu - \nu_0$ [MHz]", "fontsize": 15},
        "yaxis": {
            "bottom": {"label": r"$\Delta T_B$ [K]"},
            "top": {"label": r"$T_B$ [K]"},
            "fontsize": 15,
        },
        "figname": "imgs/fig07.pdf",
    }
)
gs = GridSpec(2, 2, figure=fig, height_ratios=settings.gridspec.height_ratio)

ax_upper_left = fig.add_subplot(gs[0, 0])
ax_upper_right = fig.add_subplot(gs[0, 1])
ax_bottom_left = fig.add_subplot(gs[1, 0])
ax_bottom_right = fig.add_subplot(gs[1, 1])


zeeman_on_color = "black"
zeeman_off_color = "goldenrod"
zeeman_on_wrong_pol_color = "red"

# --- set limits ---
for ax in [ax_upper_left, ax_upper_right, ax_bottom_left, ax_bottom_right]:
    ax.set_xlim((-40, 40))
    ax.grid(which="both", axis="both", alpha=0.25)

for ax in [ax_upper_left, ax_upper_right]:
    ax.set_ylim(180, 196)
    ax.tick_params(axis="x", which="both", bottom=False, top=False)

for ax in [ax_bottom_right, ax_bottom_left]:
    ax.set_ylim((-8, 8))


ax_upper_left.plot(
    (dd.ret_zeeman_on.f_grid - f0) / 1e6,
    dd.ret_zeeman_on.yf,
    label=settings.zeeman_on.label,
    color=settings.zeeman_on.color,
)
ax_upper_left.plot(
    (dd.ret_zeeman_off.f_grid - f0) / 1e6,
    dd.ret_zeeman_off.yf,
    label=settings.zeeman_off.label,
    color=settings.zeeman_off.color,
)

ax_bottom_left.plot(
    (dd.ret_zeeman_on.f_grid - f0) / 1e6,
    dd.ret_zeeman_on.yf - dd.ret_zeeman_off.yf,
    label=settings.difference.label,
    color=settings.difference.color,
)

ax_upper_left.legend()
ax_bottom_left.legend()

ax_upper_right.plot(
    (dd.ret_zeeman_on.f_grid - f0) / 1e6,
    dd.ret_zeeman_on.yf,
    label=settings.zeeman_on.label,
    color=settings.zeeman_on.color,
)
ax_upper_right.plot(
    (dd.ret_zeeman_on_wrong_component.f_grid - f0) / 1e6,
    dd.ret_zeeman_on_wrong_component.yf,
    label=settings.zeeman_on_wrong_pol.label,
    color=settings.zeeman_on_wrong_pol.color,
)

ax_bottom_right.plot(
    (dd.ret_zeeman_on.f_grid - f0) / 1e6,
    dd.ret_zeeman_on.yf - dd.ret_zeeman_on_wrong_component.yf,
    label=settings.difference.label,
    color=settings.difference.color,
)

ax_upper_right.legend()
ax_bottom_right.legend()

ax_bottom_left.set_xlabel(settings.xaxis.label, fontsize=settings.xaxis.fontsize)
ax_bottom_left.set_ylabel(settings.yaxis.bottom.label, fontsize=settings.yaxis.fontsize)
ax_upper_left.set_ylabel(settings.yaxis.top.label, fontsize=settings.yaxis.fontsize)
ax_bottom_right.set_xlabel(settings.xaxis.label, fontsize=settings.xaxis.fontsize)

fig.savefig(settings.figname, transparent=True)


fig = plt.figure(figsize=(10, 10))
gs = GridSpec(1, 2, figure=fig)

ax_left = fig.add_subplot(gs[0, 0])
ax_right = fig.add_subplot(gs[0, 1])
ax_left.grid(which="both", axis="both", alpha=0.25)
ax_right.grid(which="both", axis="both", alpha=0.25)
ax_left.set_xlim([160, 300])
ax_right.set_xlim([-20, 20])
ax_left.set_yticks([5, 15, 25, 35, 45, 55, 65, 75], minor=True)
ax_right.set_yticks([5, 15, 25, 35, 45, 55, 65, 75], minor=True)
ax_right.vlines(
    x=0, ymin=-5, ymax=80, color="dimgrey", label=r"$\Delta$T=0", linestyle="dashed"
)

ax_left.plot(
    retrievals["ret_zeeman_on"]["x"][0:137],
    retrievals["ret_zeeman_on"]["z_field"][:, 0, 0] / 1e3,
    label="Zeeman on",
    color=zeeman_on_color,
)
ax_left.plot(
    retrievals["ret_zeeman_off"]["x"][0:137],
    retrievals["ret_zeeman_off"]["z_field"][:, 0, 0] / 1e3,
    label="Zeeman off",
    color=zeeman_off_color,
)
ax_left.plot(
    retrievals["ret_zeeman_on_wrong_component"]["x"][0:137],
    retrievals["ret_zeeman_on_wrong_component"]["z_field"][:, 0, 0] / 1e3,
    label="Zeeman on (wrong polarization)",
    color=zeeman_on_wrong_pol_color,
)
ax_left.plot(
    t_true,
    retrievals["ret_zeeman_on"]["z_field"][:, 0, 0] / 1e3,
    label="ECMWF",
    color="gray",
    linestyle="dashed",
)
ax_left.set_xlabel("Temperature [K]", fontsize=15)
ax_left.set_ylabel("Altitude [km]", fontsize=15)
ax_left.set_title("Retrived profiles", fontsize=16)

ax_right.plot(
    t_true - retrievals["ret_zeeman_on"]["x"][0:137],
    retrievals["ret_zeeman_on"]["z_field"][:, 0, 0] / 1e3,
    label="Zeeman on",
    color=zeeman_on_color,
)
ax_right.plot(
    t_true - retrievals["ret_zeeman_off"]["x"][0:137],
    retrievals["ret_zeeman_on"]["z_field"][:, 0, 0] / 1e3,
    label="Zeeman off",
    color=zeeman_off_color,
)
ax_right.plot(
    t_true - retrievals["ret_zeeman_on_wrong_component"]["x"][0:137],
    retrievals["ret_zeeman_on"]["z_field"][:, 0, 0] / 1e3,
    label="Zeeman on (wrong polarization)",
    color=zeeman_on_wrong_pol_color,
)
ax_right.set_xlabel(r"$\Delta$Temperature [K]", fontsize=15)
ax_right.set_title("Difference (ECMWF - Retrived)", fontsize=16)
for ax in [ax_left, ax_right]:
    ax.set_ylim(-5, 85)
    ax.legend(loc="center", fontsize=8.2, ncol=2, bbox_to_anchor=(0.50, 0.97))

fig.savefig("imgs/fig08.pdf", transparent=True)
