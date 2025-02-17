import h5py
import os

def read_hdf5(filename):
    """
    Function to read hdf5 files

    Parameters:
    filename (str) : path to the file

    Returns:
    dictionary (dict): A dictionary with the data
    """

    with h5py.File(filename, "r") as file:
        if "kimra_data" in file.keys():
            dataset = file["kimra_data"]

        else:
            dataset = file

        dictionary = dict()
        for key in dataset.keys():
            try:
                dictionary[key] = dataset[key][:]
            except ValueError:
                dictionary[key] = dataset[key][()]

        return dictionary


def save_ret(ROOT, filename, *argv):
    """
    Function to save retrieval data in hdf5 file in data/retrieval in current working directory

    Parameters:
    filename (str): name of the file
    argv (pyarts.arts.Workspace.variable): workspace variables we want to save
    """

    savepath = f"{ROOT}/data/retrieval"
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    with h5py.File(f"{savepath}/{filename}", "w") as file:
        for data in argv:
            file[data.name] = data.value
