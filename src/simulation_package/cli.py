import argparse
from simulation_package.ret import ret
from simulation_package.yc import yc
from simulation_package.meas_yc_plot import meas_plot, mag_plot, meas_sim_comparison
from simulation_package.ret_plots import spec_and_fit_plot, jac_plot

COMMANDS = {"ycalc": yc, "retrieval": ret}
PLOTTING = {""}

DESC = {
    "ycalc": "Perform ycalc of 233.95 GHz O2 line at azi = [0, 90, 180, 270] and za = 77.6",
    "retrieval": "Perform synttich retrieval of 233.95 GHz O2 line",
}


def cli():
    parser = argparse.ArgumentParser(add_help=True)
    subparsers = parser.add_subparsers(
        dest="command", required=True, description="Available commands")

    for name in COMMANDS.keys():
        desc = DESC[name]
        subparser = subparsers.add_parser(name, help=desc, description=desc)
        subparser.add_argument("--plot", action="store_true")

    args = parser.parse_args()
    script = COMMANDS[args.command]

    match args.command:
        case "ycalc":
            script()
            if args.plot:
                mag_plot()
                meas_plot()
                meas_sim_comparison()

        case "retrieval":
            script()
            if args.plot:
                spec_and_fit_plot()
                jac_plot()


if __name__ == "__main__":
    cli()
