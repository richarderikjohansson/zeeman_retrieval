import pandas as pd #pyright:ignore
from datetime import datetime, timedelta
import h5py
import numpy as np

file = "magfield/kir202401dsec.sec"
df = pd.read_csv(file, skiprows=12, sep='\s+')

dt = list()
for date, time in zip(df["DATE"], df["TIME"]):
    hms = time.split(".")[0]
    dt.append(datetime.strptime(f"{date} {hms}", "%Y-%m-%d %H:%M:%S"))

B = np.array([b for b in df["KIRF"]])

# magfield in UTC spec in CET need to get correct data
s = np.where(np.array(dt) >= datetime(year=2024,month=1,day=3,hour=23,minute=0,second=0))[0][0]
e = np.where(np.array(dt) >= datetime(year=2024,month=1,day=4,hour=23,minute=0,second=0))[0][0]

start = datetime(2024, 1, 4, 0, 0, 0)
end = datetime(2024, 1, 5, 0, 0, 0)

# Create a list to hold the date range
date_range = []

# save data between 4th and 5th January
with h5py.File("magfield.hdf5", "w") as file:
    file["B"] = B[s:e]
    file["start"] = "240104"
    file["end"] = "240105"


