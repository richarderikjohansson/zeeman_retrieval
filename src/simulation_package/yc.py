from simulation_package.ycalc import ycalc_zeeman
from tqdm import tqdm


# run ycalc
def yc():
    azi = {"0": 0, "90": 90, "180": 180, "270": -90}
    for name, az in tqdm(azi.items()):
        ycalc_zeeman(
            zenith=77.6,
            azimuth=az,
            line="kimra",
            filename=f"YCALC_{name}.hdf5",
            zeeman=True,
        )
