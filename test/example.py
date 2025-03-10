from simulation_package.retrieval import Retrieval
from simulation_package.hdf import read_hdf5, DottedDict
from simulation_package.make_grids import get_git_root
import matplotlib.pyplot as plt

git_root = get_git_root()

# Init retrievals for 53 GHz and 233 GHz lines and do ycalc
tempera = Retrieval(line="tempera", recalc=True)
kimra = Retrieval(line="kimra", recalc=True)

# Do OEM for 53 and 233 GHz lines
tempera.do_OEM(filename="tempera_example.hdf5")
kimra.do_OEM(filename="kimra_example.hdf5")

# Read retrieved data-sets
data = DottedDict({
    "kimra": read_hdf5(f"{get_git_root()}/data/retrieval/kimra_example.hdf5"),
    "tempera": read_hdf5(f"{get_git_root()}/data/retrieval/tempera_example.hdf5"),
})
