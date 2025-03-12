import optparse

from simulation_package.ycalc import ycalc_zeeman
from simulation_package.plot_ycalc import plot_spectra, plot_spectra_with_components, plot_temperature_jacobian

parser = optparse.OptionParser()
parser.add_option("-z", "--zenith", default=45)
parser.add_option("-a", "--azimuth", default=0)
parser.add_option("-p", "--zeeman", action="store_true", dest="zeeman", default=False)
parser.add_option("-f", "--filename", default="ycalc")
parser.add_option("-s", "--plot", action="store_true", default=False, dest="plot")
opts, args = parser.parse_args()

lines = ["kimra", "tempera"]

print(
    "Starting yCalc for 233.9 and 53.6 GHz oxygen lines\n"
    + f"Zenith: {opts.zenith}\n"
    + f"Azimuth: {opts.azimuth}\n"
    + f"Zeeman: {opts.zeeman}"
)
for line in lines:
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
