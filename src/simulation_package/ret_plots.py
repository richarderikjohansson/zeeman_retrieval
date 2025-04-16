from .files import find_retrieval, imgs_path
from .hdf import read_hdf5
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
import matplotlib as mpl
import numpy as np


def calc_mr(avk: np.ndarray) -> np.ndarray:
    """Function to calculate measurement response

    Calculates the measurement response from the
    averaging kernels from a retrieval

    Args:
        avk: Averaging kernel matrix

    Returns:
        Measurement response
    """
    mr = [np.sum(row) for row in avk]
    return np.array(mr)


def spec_and_fit_plot():
    """Function to plot spectra and fit"""
    legend_fontsize = 12
    labelsize = 16
    ticksize = 14
    kimra_file = find_retrieval(name="234GHz_zeeman.hdf5")
    tempera_file = find_retrieval(name="53GHz_zeeman.hdf5")
    kimra = read_hdf5(filename=kimra_file)
    tempera = read_hdf5(filename=tempera_file)

    fig = plt.figure(figsize=(16, 7))
    gs = GridSpec(2, 2, height_ratios=[2, 1], wspace=0.5)

    upper_left = fig.add_subplot(gs[0, 0])
    lower_left = fig.add_subplot(gs[1, 0])
    upper_right = fig.add_subplot(gs[0, 1])
    lower_right = fig.add_subplot(gs[1, 1])

    for ax in fig.axes:
        ax.tick_params(axis="both", labelsize=ticksize)

    upper_left.set_ylabel(r"$T_{B}$ [K]", fontsize=labelsize)
    upper_left.set_title(r"233.95 GHz $O_{2}$ line", fontsize=17)
    lower_left.set_ylabel(r"$\Delta T_{B}$ [K]", fontsize=labelsize)
    lower_left.set_xlabel(r"$\nu$ [GHz]", fontsize=labelsize)

    f0 = 233.9461e9
    upper_left.plot(
        kimra["f_grid"] / 1e9,
        kimra["y"],
        color="black",
        label="Measurement",
    )
    upper_left.plot(
        kimra["f_grid"] / 1e9,
        kimra["yf"],
        color="red",
        label="Fit",
    )
    upper_left.tick_params(axis="x", labelbottom=False)
    upper_left.grid(axis="both", alpha=0.25)

    inset_ax = inset_axes(
        upper_left,
        width="30%",
        height="40%",
        loc="upper right",
        borderpad=0,
    )
    inset_ax.set_facecolor("white")
    inset_ax.patch.set_alpha(1.0)
    inset_ax.plot(kimra["f_grid"] / 1e9, kimra["y"], color="black")
    inset_ax.plot(kimra["f_grid"] / 1e9, kimra["yf"], color="red")
    inset_ax.set_xlim((f0 - 10e6) / 1e9, (f0 + 10e6) / 1e9)
    inset_ax.set_ylim(196, 201)
    inset_ax.set_xticks([])
    inset_ax.set_yticks([196, 197, 198, 199, 200, 201])
    inset_ax.yaxis.set_label_position("right")
    inset_ax.yaxis.tick_right()
    inset_ax.tick_params(bottom=False)

    upper_left.set_ylim(185, 201)
    upper_left.legend(loc="upper left", fontsize=legend_fontsize)
    mark_inset(
        upper_left,
        inset_ax,
        loc1=2,
        loc2=3,
        fc="none",
        ec="0.5",
    )

    upper_left.set_axisbelow(True)

    lower_left.plot(
        kimra["f_grid"] / 1e9,
        kimra["y"] - kimra["yf"],
        label="Residual",
        color="grey",
    )
    lower_left.set_ylim(-1.5, 1.5)
    lower_left.legend(fontsize=legend_fontsize)
    lower_left.grid(axis="both", alpha=0.25)

    # ~

    upper_right.set_title(r"53.07 GHz $O_{2}$ line", fontsize=17)
    lower_right.set_xlabel(r"$\nu$ [GHz]", fontsize=labelsize)

    f0 = 53.066906e9
    upper_right.plot(
        tempera["f_grid"] / 1e9,
        tempera["y"],
        color="black",
        label="Measurement",
    )
    upper_right.plot(
        tempera["f_grid"] / 1e9,
        tempera["yf"],
        color="red",
        label="Fit",
    )
    upper_right.tick_params(axis="x", labelbottom=False)
    upper_right.grid(axis="both", alpha=0.25)

    inset_ax = inset_axes(
        upper_right,
        width="30%",
        height="40%",
        loc="upper right",
        borderpad=0,
    )
    inset_ax.set_facecolor("white")
    inset_ax.patch.set_alpha(1.0)
    inset_ax.plot(tempera["f_grid"] / 1e9, tempera["y"], color="black")
    inset_ax.plot(tempera["f_grid"] / 1e9, tempera["yf"], color="red")
    inset_ax.set_xlim((f0 - 10e6) / 1e9, (f0 + 10e6) / 1e9)
    inset_ax.set_ylim(120, 170)
    inset_ax.set_xticks([])
    inset_ax.set_yticks([120, 130, 140, 150, 160, 170])
    inset_ax.yaxis.set_label_position("right")
    inset_ax.yaxis.tick_right()
    inset_ax.tick_params(bottom=False)

    # upper_right.set_ylim(185, 201)
    upper_right.legend(loc="upper left", fontsize=legend_fontsize)
    mark_inset(upper_right, inset_ax, loc1=2, loc2=3, fc="none", ec="0.5")
    upper_right.set_axisbelow(True)
    lower_right.plot(
        tempera["f_grid"] / 1e9,
        tempera["y"] - tempera["yf"],
        label="Residual",
        color="grey",
    )
    lower_right.set_ylim(-1.5, 1.5)
    lower_right.legend(fontsize=legend_fontsize)
    lower_right.grid(axis="both", alpha=0.25)
    lower_right.tick_params(axis="both", which="major", labelsize=labelsize)
    plt.tight_layout()

    fig.savefig(imgs_path() / "fig06.pdf")
    plt.close()


def avk_plot():
    """Function to plot averaging kernels"""
    plen = 137
    kimra_file = find_retrieval(name="234GHz_zeeman.hdf5")
    tempera_file = find_retrieval(name="53GHz_zeeman.hdf5")

    kimra = read_hdf5(filename=kimra_file)
    tempera = read_hdf5(filename=tempera_file)
    z = kimra["z_field"][:, 0, 0]
    assert np.all(z == tempera["z_field"][:, 0, 0]), "Check altitude"

    mr_kimra = calc_mr(kimra["avk"][0:plen, 0:plen])
    mr_tempera = calc_mr(tempera["avk"][0:plen, 0:plen])

    cmap = mpl.colormaps.get_cmap("jet")
    cmap_arr = np.linspace(0, 1, plen)
    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=plt.Normalize(vmin=z[0] / 1e3, vmax=z[-1] / 1e3),
    )

    fig = plt.figure(figsize=(20, 10))
    gs = GridSpec(1, 2)

    left = fig.add_subplot(gs[0, 0])
    right = fig.add_subplot(gs[0, 1])
    for i, row in enumerate(kimra["avk"][0:plen, 0:plen]):
        left.plot(
            row * 20,
            z / 1e3,
            color=cmap(cmap_arr[i]),
            linewidth=0.5,
        )
        if i == 60:
            left.plot(
                row * 20,
                z / 1e3,
                color=cmap(cmap_arr[i]),
                linewidth=0.5,
                label="20AVK",
            )

    for i, row in enumerate(tempera["avk"][0:plen, 0:plen]):
        right.plot(
            row * 20,
            z / 1e3,
            color=cmap(cmap_arr[i]),
            linewidth=0.5,
        )
        if i == 60:
            right.plot(
                row * 20,
                z / 1e3,
                color=cmap(cmap_arr[i]),
                linewidth=0.5,
                label="20AVK",
            )

    left.plot(
        mr_kimra,
        z / 1e3,
        color="red",
        linewidth=2,
        label="Measurement response",
    )
    right.plot(
        mr_tempera,
        z / 1e3,
        color="red",
        linewidth=2,
        label="Measurement response",
    )

    for ax in fig.axes:
        ax.tick_params(axis="both", labelsize=12)
        ax.legend()
        ax.grid(which="both", alpha=0.25)
        ax.set_xlabel("Average Kernel (rows) [-]", fontsize=14)

    left.set_ylabel("Altitude [km]", fontsize=14)
    cbar = plt.colorbar(sm, ax=right)
    cbar.set_label("Altitude [km]", fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    fig.savefig(imgs_path() / "avk.pdf", transparent=True)
    plt.close()


def jac_plot():
    """Function to plot max of Jacobian"""
    legend_fontsize = 12
    labelsize = 16
    ticksize = 14
    plen = 137
    kimra_file = find_retrieval(name="234GHz_zeeman.hdf5")
    tempera_file = find_retrieval(name="53GHz_zeeman.hdf5")

    kimra = read_hdf5(filename=kimra_file)
    tempera = read_hdf5(filename=tempera_file)

    kimra_jac = kimra["jacobian"][:, 0:plen]
    tempera_jac = tempera["jacobian"][:, 0:plen]
    z = kimra["z_field"][:, 0, 0]
    assert np.all(z == tempera["z_field"][:, 0, 0]), "Check altitude"
    z = z / 1e3

    kimra_max = []
    tempera_max = []

    for r1, r2 in zip(kimra_jac.transpose(), tempera_jac.transpose()):
        kimra_max.append(r1.max())
        tempera_max.append(r2.max())

    fig = plt.figure(figsize=(8, 10))
    gs = GridSpec(1, 1)
    center = fig.add_subplot(gs[0, 0])

    center.minorticks_on()
    center.plot(kimra_max, z, color="black", label="233.95 GHz line")
    center.plot(tempera_max, z, color="tomato", label="53.07 GHz line")
    center.grid(True, alpha=0.25)
    center.tick_params(labelsize=ticksize)
    center.set_ylabel("Altitude [km]", fontsize=labelsize)
    center.set_xlabel(r"$k_{max}$ [K$^{-1}$]", fontsize=labelsize)
    center.legend(fontsize=legend_fontsize)
    plt.tight_layout()
    fig.savefig(imgs_path() / "fig05.pdf", transparent=True)
    plt.close()


def jac_mr_plot():
    """Function to plot max of Jacobian and measurement response"""
    plen = 137
    kimra_file = find_retrieval(name="234GHz_zeeman.hdf5")
    tempera_file = find_retrieval(name="53GHz_zeeman.hdf5")

    kimra = read_hdf5(filename=kimra_file)
    tempera = read_hdf5(filename=tempera_file)

    kimra_jac = kimra["jacobian"][:, 0:plen]
    tempera_jac = tempera["jacobian"][:, 0:plen]
    z = kimra["z_field"][:, 0, 0]
    assert np.all(z == tempera["z_field"][:, 0, 0]), "Check altitude"
    z = z / 1e3

    kimra_max = []
    tempera_max = []

    for r1, r2 in zip(kimra_jac.transpose(), tempera_jac.transpose()):
        kimra_max.append(r1.max())
        tempera_max.append(r2.max())
    kimra_mr = calc_mr(kimra["avk"][0:plen, 0:plen])
    tempera_mr = calc_mr(tempera["avk"][0:plen, 0:plen])

    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(1, 2)

    left = fig.add_subplot(gs[0, 0])
    right = fig.add_subplot(gs[0, 1])
    for ax in fig.axes:
        ax.grid(True, alpha=0.25)
        ax.minorticks_on()
    left.set_ylabel("Altitude [km]", fontsize=14)
    left.set_title("Maximum values of Jacobian matrix")
    left.plot(kimra_max, z, color="black", label="233.95 GHz line")
    left.plot(tempera_max, z, color="tomato", label="53.07 GHz line")
    left.set_xlabel(r"$\underset{j}{max}(k_{ji})$", fontsize=14)
    left.legend()

    right.set_title("Measurement response calculated from average kernals")
    right.plot(kimra_mr, z, color="black", label="233.95 GHz line")
    right.plot(tempera_mr, z, color="tomato", label="53.07 GHz line")
    right.set_xlabel("Measurement Response", fontsize=14)
    right.legend()

    fig.savefig(imgs_path() / "avk_mr.pdf")
    plt.close()


def jac_pcolormesh():
    """Function to plot the whole Jacobian matrix"""
    labelsize = 16
    ticksize = 14
    plen = 137
    tempera_file = find_retrieval(name="53GHz_zeeman.hdf5")
    kimra_file = find_retrieval(name="234GHz_zeeman.hdf5")
    tempera = read_hdf5(tempera_file)
    kimra = read_hdf5(kimra_file)

    jacobian_tempera = tempera["jacobian"][:, 0:plen]
    jacobian_kimra = kimra["jacobian"][:, 0:plen]
    z = tempera["z_field"][:, 0, 0] / 1e3
    f_tempera = tempera["f_grid"] / 1e9
    f_kimra = kimra["f_grid"] / 1e9

    fig = plt.figure(figsize=(16, 10))
    gs = plt.GridSpec(1, 2)
    left = fig.add_subplot(gs[0, 0])
    right = fig.add_subplot(gs[0, 1])
    left.set_ylabel("Altitude [km]", fontsize=labelsize)
    left.set_title("Jacobian for 233.95 GHz line", fontsize=17)
    right.set_title("Jacobian for 53.07 GHz line", fontsize=17)

    pmesh_right = right.pcolormesh(
        f_tempera,
        z,
        jacobian_tempera.transpose(),
        cmap="viridis",
        shading="nearest",
    )
    pmesh_left = left.pcolormesh(
        f_kimra,
        z,
        jacobian_kimra.transpose(),
        cmap="viridis",
        shading="nearest",
    )
    for ax in fig.axes:
        ax.tick_params(labelsize=ticksize)
        ax.set_xlabel(r"$\nu$ [GHz]", fontsize=labelsize)

    cbar = plt.colorbar(pmesh_left, ax=left, location="top")
    cbar.ax.tick_params(labelsize=ticksize)

    cbar = plt.colorbar(pmesh_right, ax=right, location="top")
    cbar.ax.tick_params(labelsize=ticksize)
    fig.savefig(imgs_path() / "jac_mat.pdf")
    plt.close()
