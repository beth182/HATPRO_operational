######################################
HATPRO Visualisation Script
by Lukas Lehner, Student at ACInn
lehner.lukas(at)hotmail.com
#####################################

script requires the following data (add code to script.sh and script_archive.sh):

1) temp and humidity data as CSV from database (Szabo, retrieval of Steffi - Wrapper)

2) Sybase data (.txt) - mainly pressure measurements from the university station. This can be replaced by HATPRO measurements if they would be available.
eg. ssh acinn_sybase@meteo-data 'cd ~acinn_sybase/Sybase2; ../virtualenv/bin/python getobs.py -t tawes -s 11320 --YYYYmmdd -b 20170101 -e 20170102'

3) Precipitation flag would be important to drop data measured during precipitation - currently (March 2017) not available

set all urls to data-files and export images in "settings_url.py"
additionally set all local paths and path to python in script.sh and script_archive.sh - the bash scripts that start the process.

the following subfunctions/definitions are available:

- read_sybase.py	Read .txt file from sybase of university weather station

- read_hatpro.py	Read hatpro data from database, already processed and in 10 min (currently) interval

- pot_temperature.py	Calculate potential temperature from hatpro temperature and sybase pressure measurements

- pot_temperature_colors.py	The colorbar of the filled potential temperature field is changing depending on the "day of year" as a fixed color is not very applicable. Climatologies of potential temperature in Innsbruck, on Patscherkofel and Zugspitze were analyzed to cover different heights. The file "theta_boundaries.csv" contains an matrix of 366 (including leap year) rows with the lower and upper threshold of the colorbar.

- iwv.py		This function calculates the integrated water vapour per square meter. It is not used in the visualisation. Some single verifications with radiosondes showed good aggreement (no further statistics)

- plot.py		Plot the screen image

- main.py		Main script

- settings.py and settings_url.py	Setting files for processing and plotting of the data

Cronjobs could be set up every 10 minutes. 
