# SIMULATION CODE AND MEASUREMENT DATA

In this README will descriptions on how to use the simulation code "zeeman_ycalc_azi.py" and also how the data is 
packaged in the .hdf5 files

## SIMULATION CODE

The simulation code found in "zeeman_ycalc_azi.py" and runs fully in python. To install the necessary dependencies 
I suggest to use miniforge3 and mamba see: https://github.com/conda-forge/miniforge and follow the installation guide.

Using LINUX/MacOS you can then easily install all the dependencies using mamba or conda with the environment file 
"environment.yml". This is done through the following command in your terminal:

mamba env create --name simulation --file environment.yml

All dependencies will then be installed in the environment "simulation". To activate this environment simply 
type the following command in your terminal:

mamba activate simulation

Now you can run the simulation from the terminal with:

python zeeman_ycalc_azi.py

The simulation will be done with four different lines of sight where the azimuth angle will vary between the 0°, 90°,
180° and 270°. The zenith angle will remain fixed at 77.6° mimicking our measurement lines of sight. When the script 
have finished you will the results of the simulation be saved under "hdf5/simulation"

## FILE AND VARIABLE DESCRIPTIONS

### SIMULATIONS

The simulations are saved as hdf files in hdf5/simulations. The filenames indicate what azimuthal angles used for example, 
"ycalc_O2_0.hdf5" contains the data for the simulation where the azimuth angle was 0° and so on. The files are hdf files 
and I suggest the python library h5py to read them, see: https://docs.h5py.org/en/3.12.1/ for the documentation. The keys 
in these fields are the following:

I   : intesity of the radiation
Q   : Stoke component for the linear polarized radiation (vertical and horizontal)
U   : Stoke component for the linear polarized radiation (45°)
V   : Stoke component for the circular polarized radiation (right and left hand)
f   : Frequency vector
azi : Azimuth angle

### MEASUREMENTS

As for the simulations are the measurements also saved in hdf format and can also be read with the h5py library. The files
are associated according the following:

Data_2024-01-04_03-35-09_RPGFFTS.hdf5 : Measurement at 0° azimuth angle (North)
Data_2024-01-04_05-36-27_RPGFFTS.hdf5 : Measurement at 180° azimuth angle (South)
Data_2024-01-04_15-06-38_RPGFFTS.hdf5 : Measurement at 90° azimuth angle (East)
Data_2024-01-04_16-07-17_RPGFFTS.hdf5 : Measurement at 270° azimuth angle (West)

The data is saved under the key "kimra_data" and holds the following keys:

azimuth          : Azimuth angle for the line of sight
date             : The start date of the measurement
f                : Frequency vector associated with the measurement
integration      : Number of integrations for the measurement
gas              : Gas tag tied to the measurement
integration-time : Time spent for the integration, in ms
p_grid           : pressure grid collected from ECMWF
record-number    : integer associated with the raw data file
source           : file path to the raw data file on the server
spectrometer     : The spectrometer used
t_field          : Temperature grid collected from ECMWF
time             : Start time for the measurement
y                : Spectra in brightness temperature
z_field          : altitude grid calculated from the pressure grid
za               : Zenith angle for the line of sight
