from simulation_package.retrieval import Retrieval


# run retrieval
def ret():
    kimra_zeeman = Retrieval(line="kimra", recalc=True, zeeman=True)
    kimra_zeeman.do_OEM(filename="234GHz_zeeman.hdf5")

    tempera_zeeman= Retrieval(line="tempera", recalc=True, zeeman=True)
    tempera_zeeman.do_OEM(filename="53GHz_zeeman.hdf5")
