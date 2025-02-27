from datetime import datetime
from utils.hdf import grab_mag


# --- driver code ---
start = "231202"
end = "231203"
start_gmt = datetime(year=2023, month=12, day=1, hour=23, minute=0, second=0)
end_gmt = datetime(year=2023, month=12, day=2, hour=23, minute=0, second=0)

try:
    grab_mag(
        filename="data/magfield/231202/kir202312dsec.sec",
        start_gmt=start_gmt,
        end_gmt=end_gmt,
        start=start,
        end=end,
        save_name="data/magfield/231202/magfield",
    )
except FileNotFoundError:
    print("FileNotFoundError: Unpack 'data/magfield/231202/kir202312dsec.tar.gz'")

start = "240104"
end = "240105"
start_gmt = datetime(year=2024, month=1, day=3, hour=23, minute=0, second=0)
end_gmt = datetime(year=2024, month=1, day=4, hour=23, minute=0, second=0)

try:
    grab_mag(
        filename="data/magfield/240104/kir202401dsec.sec",
        start_gmt=start_gmt,
        end_gmt=end_gmt,
        start=start,
        end=end,
        save_name="data/magfield/240104/magfield",
    )
except FileNotFoundError:
    print("FileNotFoundError: Unpack 'data/magfield/231202/kir202401dsec.tar.gz'")

