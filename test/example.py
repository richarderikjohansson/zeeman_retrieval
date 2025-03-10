from simulation_package.retrieval import Retrieval
tempera = Retrieval(line="tempera", recalc=True)
kimra = Retrieval(line="kimra", recalc=True)

tempera.do_OEM(filename="example")
kimra.do_OEM(filename="example")
