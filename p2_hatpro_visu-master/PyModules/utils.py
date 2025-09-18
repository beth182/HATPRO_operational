# -------------------------------------------------------------------
# - NAME:        utils.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-02-?? 
# -------------------------------------------------------------------
# - DESCRIPTION: Different useful functions used in several
#        	 other scripts
# -------------------------------------------------------------------
# - EDITORIAL:   2014-02-??, RS: Created file.
#        	 2014-12-01, SW: added header information
# -------------------------------------------------------------------

import sys, os
os.environ['TZ'] = 'UTC'
import struct
import math
from datetime import datetime as dt

EMPTYSTRING = ''

# -------------------------------------------------------------------
# - Customized exit.
# -------------------------------------------------------------------
def exit(msg):
    print '\n[!] ERROR: %s\n' % msg
    sys.exit(-9)


def print_dict( x ):

    if not type(x) == type(dict()):
        sys.exit('ERROR: Input to print_dict was no dict object!')

    keys = x.keys(); keys.sort()
    for k in keys:
        print '   %-20s %s' % (k,x[k])


def get_filecode(infile, pathtorawfiles):

    infile = pathtorawfiles + os.sep + infile
    if not os.path.isfile(infile):
        sys.exit('ERROR: file '+ infile +' not found')

    # - Else, extracting file code
    fid = open(infile,'rb')
    filecode = struct.unpack('<I',fid.read()[:4])[0]
    fid.close()

    return filecode


#def get_files(config, pattern='*'): # pattern="*" as default
#
#    import glob
#
#    # - Change directory to datadir defined in the config
#    #   file, then search for suitable files (pattern)
#    current_directory = os.getcwd()
#    os.chdir(config['datadir'])
#    #print pattern
#    #print type(pattern)
#    # if pattern is a string
#    if type(pattern) == type(''):
#        files = glob.glob(pattern)
#    # if pattern is a list of different patterns(endings)
#    elif type(pattern) == type([]):
#        files = []
#        for p in pattern:
#            tmp = glob.glob(p)
#            for t in tmp: 
#                files.append(t)
#    else:
#        sys.exit('ERROR: Wrong input on <pattern> to method get_files [type was: ' + \
#                 str(type(pattern)) + ']')
#    os.chdir(current_directory)
#    files.sort()
#    return files

def get_files_from_path(pathtorawfiles, pattern='*'): # pattern="*" as default
    import glob
    current_directory = os.getcwd()
    os.chdir(pathtorawfiles)
    if type(pattern) == type(''):
        files = glob.glob(pattern)
    elif type(pattern) == type([]):
        files = []
        for p in pattern:
            tmp = glob.glob(p)
            for t in tmp: 
                files.append(t)
    else:
        sys.exit('ERROR: Wrong input on <pattern> to method get_files [type was: ' + \
                 str(type(pattern)) + ']')
    os.chdir(current_directory)
    files.sort()
    return files

# - Hatpro origin for time stamp is 2001-01-01.
#   The function here adds as much seconds as necessary
#   to have a nice unix timestamp base on 1970-01-01
def timestamp(x):

    return x+978307200

# -------------------------------------------------------------------    
# - Getting "time periods" where we have to average over to get
#   the mean values used for the linear regression afterwards.
#   config['averaging'] (minutes input) controls the periode in minutes,
#   timestamp_min and timestamp_max defines the overlapping periode
#   of data in all tables.
# -------------------------------------------------------------------    

