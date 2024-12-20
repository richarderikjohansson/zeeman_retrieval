import pandas as pd #pyright:ignore
from datetime import datetime, timedelta
import h5py
import numpy as np

def grab_mag(filename, start_gmt, end_gmt, start, end, save_name):
    """
    Function to parse magnetic field data and save data in .hdf5 format

    Parameters:
    filename (str) : path to the file
    start_gmt (datetime) : start of data in CET
    start_gmt (datetime) : end of data in CET
    start (str) : start date for data
    end (str) : end date for data
    save_name (str) : path where the .hdf5 file should be saved

    """

    df = pd.read_csv(filename, skiprows=12, sep='\s+')

    dt = list()
    for date, time in zip(df["DATE"], df["TIME"]):
        hms = time.split(".")[0]
        dt.append(datetime.strptime(f"{date} {hms}", "%Y-%m-%d %H:%M:%S"))

    B = np.array([b for b in df["KIRF"]])

    # magfield in UTC spec in CET need to get correct data
    s = np.where(np.array(dt) >= start_gmt)[0][0]
    e = np.where(np.array(dt) >= end_gmt)[0][0]

    # save data between as .hdf5 
    with h5py.File(f"{save_name}.hdf5", "w") as file:
        file["B"] = B[s:e]
        file["start"] = start 
        file["end"] = end 


# --- driver code ---
start = "231202"
end = "231203"
start_gmt = datetime(year=2023,month=12,day=1,hour=23,minute=0,second=0)
end_gmt = datetime(year=2023,month=12,day=2,hour=23,minute=0,second=0)

grab_mag(filename="data/magfield/231202/kir202312dsec.sec",
         start_gmt=start_gmt,
         end_gmt=end_gmt,
         start=start,
         end=end,
         save_name="data/magfield/231202/magfield")

start = "240104"
end = "240105"
start_gmt = datetime(year=2024,month=1,day=3,hour=23,minute=0,second=0)
end_gmt = datetime(year=2024,month=1,day=4,hour=23,minute=0,second=0)

grab_mag(filename="data/magfield/240104/kir202401dsec.sec",
         start_gmt=start_gmt,
         end_gmt=end_gmt,
         start=start,
         end=end,
         save_name="data/magfield/240104/magfield")
