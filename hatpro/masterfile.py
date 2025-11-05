# Author:	Stephanie Westerhuis
# Date: 	2015-01-19
# Description:	This is the masterfile for dealing with HATPRO data
#		a) read in the binary files and store the values
# 		b) run the retrieval of temperature/humidity values
#		c) plot a profile

# Python modules
import os
import sys
import datetime

# Self-written modules
from hatpro.PyModules import utils
from hatpro.PyModules import multiobject as mo
from hatpro.PyModules import database
from hatpro.PyModules import TP
from hatpro.PyModules import doretrieval
from hatpro.PyModules import BRT
from hatpro.PyModules import HPC
from hatpro.PyModules import MET
from hatpro.PyModules import BLB
from hatpro.PyModules import dateUtils

# sys.path.append('PyModules')

# Set timezone to UTC
os.environ['TZ'] = 'UTC'

# User inputs for running locally
# Example: Specify the year, month, day, and hour manually
YEAR = "2025"
MONTH = "05"
DAY = "14"
HOUR = "12"

# Paths (update these as needed)
current_filepath = os.getcwd().replace('\\', '/') + '/'
assert os.path.exists(current_filepath), f"Path to current directory not found: {current_filepath}"
PATH_TO_HATPRO = current_filepath

# PATH_TO_RAWDATA_RAW = current_filepath + 'example_day_data/' + 'D' + DAY + '/'  # example day's data
PATH_TO_RAWDATA_RAW = current_filepath + 'example_day_data/'
assert os.path.exists(PATH_TO_RAWDATA_RAW), f"Path to raw data not found: {PATH_TO_RAWDATA_RAW}"

# Construct paths based on user inputs
PATH_TO_RAWDATA = f"{PATH_TO_RAWDATA_RAW}Y{YEAR}/M{MONTH}/D{DAY}"
assert os.path.exists(PATH_TO_RAWDATA), f"Path to raw data not found: {PATH_TO_RAWDATA}"

PATH_TO_RAWDATA_WITH_HOUR = f"{PATH_TO_RAWDATA}/H{HOUR}"

# Configuration file
# BETH ADDITION
config_filepath = current_filepath + 'config.conf'
assert os.path.isfile(config_filepath), f"Configuration file not found: {config_filepath}"


config = {}
# execfile(sys.argv[2] + os.sep + 'config.conf', config)

with open(config_filepath) as f:
    exec(f.read(), config)




config['dbfile'] = current_filepath + 'hatprodata.db'

# ToDo: check these are the same as /mnt/imgi2-a/c7071039/imgi_wrapper_dev/hatpro/John/ files

config['coef_rh'] = current_filepath + 'John/HZE_ibk_0112_V90_nosubset_ng_pg_0.35_0.35.RET'
config['coef_T'] = current_filepath + 'John/TELQ_ibk_0112_V90_nosubset_ng_npg_0.20_0.20.RET'

assert os.path.isfile(config['coef_rh']), f"coefficient file not found for RH: {config['coef_rh']}"
assert os.path.isfile(config['coef_T']), f"coefficient file not found for T: {config['coef_T']}"


# ------------------------------------------------------------------------------------
# a) Read in files and store values in database
# ------------------------------------------------------------------------------------

# Find files
# TODO: find files also in subdirectories and for specific date

# Find files matching the hour pattern
hourpattern = HOUR
files = utils.get_files_from_path(PATH_TO_RAWDATA, [f"*{hourpattern}.MET", f"*{hourpattern}.BLB", f"*{hourpattern}.BRT"])

nrfilesfound = len(files)
if nrfilesfound == 0:
    sys.exit('No Files Found!!')
print(f'* Found {nrfilesfound} files in {PATH_TO_RAWDATA} directory')

# Create 'multiobjects' - an invention of Reto to deal with the data and metadata
TPres = mo.multiobject()  # initialize an empty multiobject object to store the temperature results
TPEres = mo.multiobject()  # initialize an empty multiobject object to store the theta temp results
HPCres = mo.multiobject()  # initialize an empty multiobject object to store the humidity results
BRTres = mo.multiobject()  # initialize an empty multiobject object to store the brightness temps
METres = mo.multiobject()  # initialize an empty multiobject object to store meteorological values
BLBres = mo.multiobject()  # initialize an empty multiobject object to store boundary layer brightness temp



# - Read all files and store the results into the
#   multiobject classes.
#   Two methods are used here:
#   1. binary-read in (TP, HPC, BRT, MET, BLB)
#   -> functions: config, header, infile, pathsep, printdata, profile, profilemeta, readdata, 
#                 sensors
#   2. multiobject (for handling the data)
#   -> functions: add, altitude, continuous, data, obj, objclass, plot, relhum, sensors, time,
#                 title, values
print('\n* Loading binary HATPRO data now')
for infile in files:
    # print(infile)
    # options for the file so that it can be passed into the modules
    opts = {'infile': os.path.join(PATH_TO_RAWDATA, infile), 'config': config, 'theta': False, 'indegrees': True}

    # - Reading file type to decide what to do
    #   get_filecode extracts binary variable code
    filecode = utils.get_filecode(infile, PATH_TO_RAWDATA)
    # print('filecode={0}'.format(filecode))
    if filecode == 780798065 or filecode == 459769847:  # TPC or TPB
        # Theta false
        T = TP.TP(opts)  # binary read in
        TPres.add({'obj': T})
        # Theta true
        opts['theta'] = True
        TE = TP.TP(opts)
        TPEres.add({'obj': TE})

    elif filecode == 117343673:  # HPC
        H = HPC.HPC(opts)
        HPCres.add({'obj': H, 'relhum': True})

    elif filecode == 666666:  # BRT
        B = BRT.BRT(opts)
        BRTres.add({'obj': B, })

    elif filecode == 599658944:  # MET (new version)
        M = MET.MET(opts)
        METres.add({'obj': M})

    elif filecode == 567845848:  # BLB
        BL = BLB.BLB(opts)
        BLBres.add({'obj': BL})

    else:
        print('------> file code ' + str(filecode) + ' unknown')

# write HATPRO rawdata into database
print('\n* Writing binary HATPRO data now into database')
db = database.database(config)
try:
    db.writedata(METres)
except:
    print('  Cannot write METres into database. Nothing loaded (?)')

try:
    db.writedata(BRTres)
except:
    print('  Cannot write BRTres into database. Nothing loaded (?)')

try:
    db.writedata(BLBres)
except:
    print('  Cannot write BLBres into database. Nothing loaded (?)')

# -------------------------------------------------------------------------------
# b) Apply retrieval to calculate Temperature and humidity
# -------------------------------------------------------------------------------
print('\n* Applying retrieval now.')
result_rh = doretrieval.doretrieval(config, db, 'rh').result
result_t = doretrieval.doretrieval(config, db, 'T').result

# print(result_rh[0])
# print(result_rh[1])
# print(result_rh[2])
# print(result_rh[3])
# print(result_rh[4])

#up to here
print(type(result_rh))

print('\n* Writing result into database.')
db.write_RESULT_to_db(result_rh, 'RESULT_rh')
db.write_RESULT_to_db(result_t, 'RESULT_t')

# SZABO
db.create_avg_table('RESULT_rh_avg', 39)
db.create_avg_table('RESULT_t_avg', 39)

avg_data_rh = []
avg_data_t = []

min_utc_rh = db.get_minmax_utc('RESULT_rh', 'min')
min_utc_t = db.get_minmax_utc('RESULT_t', 'min')
# print(min_utc_rh)

max_utc_rh = db.get_minmax_utc('RESULT_rh', 'max')
max_utc_t = db.get_minmax_utc('RESULT_t', 'max')
# print(max_utc_rh)

round_min_utc_rh = dateUtils.createNextRoundMin(min_utc_rh)
# print(round_min_utc_rh)
round_min_utc_t = dateUtils.createNextRoundMin(min_utc_t)
# print(round_min_utc_rh)

for utc in range(round_min_utc_rh, max_utc_rh, 600):
    dataline = db.get_avg_data(utc, 'RESULT_rh')
    if len(dataline) == 40:
        avg_data_rh.append(dataline)

for utc in range(round_min_utc_t, max_utc_t, 600):
    dataline = db.get_avg_data(utc, 'RESULT_t')
    if len(dataline) == 40:
        avg_data_t.append(dataline)

db.insert_avg_data('RESULT_rh_avg', avg_data_rh)
db.insert_avg_data('RESULT_t_avg', avg_data_t)

db.close()
