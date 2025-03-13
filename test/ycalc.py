import optparse
from tqdm import tqdm
import os

from simulation_package.ycalc import ycalc_zeeman
from simulation_package.make_grids import get_git_root
from simulation_package.plot_ycalc import (
    plot_spectra,
    plot_spectra_with_components,
    plot_temperature_jacobian,
)

parser = optparse.OptionParser()
parser.add_option("-z", "--zenith", default=45)
parser.add_option("-a", "--azimuth", default=0)
parser.add_option("-p", "--zeeman", action="store_true", dest="zeeman", default=False)
parser.add_option("-f", "--filename", default="ycalc")
parser.add_option("-s", "--plot", action="store_true", default=False, dest="plot")
parser.add_option("-d", "--disturb", action="store_true", default=False, dest="disturb")
opts, args = parser.parse_args()

lines = ["kimra", "tempera"]
disturbed_path = f"{get_git_root()}/data/simulated_spectras/ECMWF/disturbed"

print(
    (
        "Starting yCalc for 233.9 and 53.6 Ghz lines\n"
        f"Zenith: {opts.zenith}\n"
        f"Azimuth: {opts.azimuth}\n"
        f"Zeeman: {opts.zeeman}\n"
        f"Distrubed Temperature: {opts.disturb}"
    )
)
for line in lines:
    if opts.disturb:
        for i in tqdm(range(137)):
            if not os.path.exists(disturbed_path):
                os.makedirs(disturbed_path)
            ycalc_zeeman(
                zenith=float(opts.zenith),
                azimuth=float(opts.azimuth),
                line=line,
                zeeman=opts.zeeman,
                disturb_flag=opts.disturb,
                index=i,
                filename=f"disturbed/{line}_{opts.filename}_p_{i}.hdf5",
            )
    else:
        ycalc_zeeman(
            zenith=float(opts.zenith),
            azimuth=float(opts.azimuth),
            line=line,
            zeeman=opts.zeeman,
            filename=f"{line}_{opts.filename}.hdf5",
        )


if opts.plot:
    plot_spectra_with_components(opts.filename)
    plot_spectra(filename=opts.filename)
    plot_temperature_jacobian(filename=opts.filename, zeeman=opts.zeeman)
