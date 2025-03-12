import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from simulation_package.hdf import read_hdf5, DottedDict
from simulation_package.make_grids import get_git_root
import numpy as np

KIMRA = "kimra"
TEMPERA = "tempera"
LINECENTERS = [233946098286.277, 53.5957e9]


def read_files(filename):
    gitroot = get_git_root()
    saved_path = f"{gitroot}/data/simulated_spectras/ECMWF"
    kimra_file = f"{saved_path}/{KIMRA}_{filename}.hdf5"
    tempera_file = f"{saved_path}/{TEMPERA}_{filename}.hdf5"

    tempera = DottedDict(read_hdf5(tempera_file))
    kimra = DottedDict(read_hdf5(kimra_file))

    return kimra, tempera


def get_bounds(data, f0):
    s = np.where(data.f_grid > f0 - 20e6)[0][0]
    e = np.where(data.f_grid > f0 + 20e6)[0][0]
    return s, e


def plot_spectra_with_components(filename):
    kimra, tempera = read_files(filename)
    fig = plt.figure(figsize=(10, 8))
    gs = gridspec.GridSpec(4, 2, width_ratios=[1, 1], wspace=0.8, hspace=0.1)

    s, e = get_bounds(kimra, LINECENTERS[0])
    for i in range(4):
        ax = fig.add_subplot(gs[i, 0])
        ax.grid(which="both", alpha=0.2)
        if i < 3:
            ax.set_xticklabels([])
        match i:
            case 0:
                ax.set_title("233.9 GHz Oxygen line")
                ax.set_ylabel(r"$T_b$ [K]")
                ax.plot(
                    (kimra.f_grid[s:e] - LINECENTERS[0]) / 1e6, kimra.sI[s:e], label="I"
                )
            case 1:
                ax.set_ylabel(r"$T_b$ [K]")
                ax.plot(
                    (kimra.f_grid[s:e] - LINECENTERS[0]) / 1e6, kimra.sQ[s:e], label="Q"
                )
            case 2:
                ax.set_ylabel(r"$T_b$ [K]")
                ax.plot(
                    (kimra.f_grid[s:e] - LINECENTERS[0]) / 1e6, kimra.sU[s:e], label="U"
                )
            case 3:
                ax.set_ylabel(r"$T_b$ [K]")
                ax.set_xlabel(r"$\nu-\nu_0$ [MHz]")
                ax.plot(
                    (kimra.f_grid[s:e] - LINECENTERS[0]) / 1e6, kimra.sV[s:e], label="V"
                )

        ax.legend()

    s, e = get_bounds(tempera, LINECENTERS[1])
    for i in range(4):
        ax = fig.add_subplot(gs[i, 1])
        ax.grid(which="both", alpha=0.2)
        if i < 3:
            ax.set_xticklabels([])
        match i:
            case 0:
                ax.set_title("53.6 GHz Oxygen line")
                ax.set_ylabel(r"$T_b$ [K]")
                ax.plot(
                    (tempera.f_grid[s:e] - LINECENTERS[1]) / 1e6,
                    tempera.sI[s:e],
                    label="I",
                )
            case 1:
                ax.set_ylabel(r"$T_b$ [K]")
                ax.plot(
                    (tempera.f_grid[s:e] - LINECENTERS[1]) / 1e6,
                    tempera.sQ[s:e],
                    label="Q",
                )
            case 2:
                ax.set_ylabel(r"$T_b$ [K]")
                ax.plot(
                    (tempera.f_grid[s:e] - LINECENTERS[1]) / 1e6,
                    tempera.sU[s:e],
                    label="U",
                )
            case 3:
                ax.set_ylabel(r"$T_b$ [K]")
                ax.set_xlabel(r"$\nu-\nu_0$ [MHz]")
                ax.plot(
                    (tempera.f_grid[s:e] - LINECENTERS[1]) / 1e6,
                    tempera.sV[s:e],
                    label="V",
                )

        ax.legend()

    plt.savefig(f"{filename}_with_components.pdf")


def plot_spectra(filename):
    kimra, tempera = read_files(filename)

    fig = plt.figure(figsize=(12, 6))
    gs = gridspec.GridSpec(1, 2)
    left = fig.add_subplot(gs[0, 0])
    right = fig.add_subplot(gs[0, 1])

    left.plot((kimra.f_grid - LINECENTERS[0]) / 1e6, kimra.sI, label="I")
    right.plot((tempera.f_grid - LINECENTERS[1]) / 1e6, tempera.sI, label="I")

    left.set_title("233.9 GHz Oxygen line")
    left.set_ylabel(r"$T_b$ [K]")
    left.set_xlabel(r"$\nu-\nu_0$ [MHz]")

    right.set_title("53.6 GHz Oxygen line")
    right.set_xlabel(r"$\nu-\nu_0$ [MHz]")

    for ax in fig.axes:
        ax.grid(which="both", alpha=0.2)
        ax.legend()

    plt.savefig(f"{filename}_spectra.pdf")


def plot_temperature_jacobian(filename, zeeman):
    kimra, tempera = read_files(filename)
    fig = plt.figure(figsize=(15, 8))
    gs = gridspec.GridSpec(1, 2)

    left = fig.add_subplot(gs[0, 0])
    right = fig.add_subplot(gs[0, 1])
    left.set_title(r"Temperature Jacobian for 233.9 GHz line")
    left.set_xlabel(r"$\nu-\nu_0$ [GHz]")
    left.set_ylabel(r"Altitude [km]")
    right.set_title(r"Temperature Jacobian for 53.6 GHz line")
    right.set_xlabel(r"$\nu-\nu_0$ [GHz]")

    zx, zy = np.meshgrid(
        (kimra.f_grid - LINECENTERS[0]) / 1e9, kimra.z_field[:, 0, 0] / 1e3
    )
    if zeeman:
        jac = kimra.jacobian[::4, :]
    else:
        jac = kimra.jacobian[:, :]
    contour_left = left.contourf(zx, zy, jac.T, cmap="jet", levels=15)

    zx, zy = np.meshgrid(
        (tempera.f_grid - LINECENTERS[1]) / 1e9, tempera.z_field[:, 0, 0] / 1e3
    )
    if zeeman:
        jac = tempera.jacobian[::4, :]
    else:
        jac = tempera.jacobian[:, :]
    contour_right = right.contourf(zx, zy, jac.T, cmap="jet", levels=15)
    fig.colorbar(contour_left, ax=left, orientation="horizontal", label="Jacobian")
    fig.colorbar(contour_right, ax=right, orientation="horizontal", label="Jacobian")
    plt.savefig(f"{filename}_temperature_jacobian.pdf")
