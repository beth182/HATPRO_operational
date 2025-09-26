# -------------------------------------------------------------------
# - NAME:        HPC.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-02-06
# -------------------------------------------------------------------
# - DESCRIPTION: The HPC class can read binary HATPRO files 
#                humidity profile chart files (including RH).
#                Format as explained by 'Principles of Operation &
#                Software Guide', Appendix A, Radiometer Physics GmbH
# -------------------------------------------------------------------
# - EDITORIAL:   2014-02-06, RS: Created file.
# -------------------------------------------------------------------


import sys, os
os.environ['TZ'] = 'UTC'
import struct
import numpy as np
import utils


class HPC(object):

    def __init__(self,object):

        self.infile  = None # default value
        self.config  = None
        self.pathsep = '/'

        for o in object:
            if o == 'infile':
                infile = object[o]
            if o == 'config':
                self.config = object[o]

        if self.config == None:
            sys.exit('ERROR: Class ' + self.__class__.__name__ + ': ' + \
                     'Config not given')
        elif infile == None:
            sys.exit('ERROR: Class ' + self.__class__.__name__ + ': ' + \
                     'Input file not given.')

        # - Create full input file path/name 
        try:
            #self.infile = self.config['datadir'] + self.config['pathsep'] + infile
            self.infile = infile
        except:
            sys.exit('ERROR: Class ' + self.__class__.__name__ + ': ' + \
                     'Cannot create full input file path!.')
        if not os.path.isfile(self.infile):
            sys.exit('ERROR: Class ' + self.__class__.__name__ + ': ' + \
                     'File ' + self.infile + ' not found.')

        self.readdata()
        ##self.printdata()

    # -----------------------------------------------------------
    # - Reading the binary data
    def readdata(self):
    
        fid = open(self.infile,'rb')
        bytes_read = fid.read()

        # - Create binary format
        HEADFMT = '<IIffIII'

        # - Reading header first
        bytes_header = 7*4
        raw = struct.unpack(HEADFMT,bytes_read[0:bytes_header])
        self.header = {}
        self.header['TPBCode']      = raw[0] # TPC-File Code (=780798065)
        self.header['N']            = raw[1] # Number of records
        self.header['HPCMin']       = raw[2] # Minimum of recorded abs. humidity values 
        self.header['HPCMax']       = raw[3] # Maximum of recorded abs. humidity values
        self.header['TPCTimeRef']   = raw[4] # Time reference (1:UTC, 0:Local Time)
        self.header['TPCRetreival'] = raw[5] # 0: linear Reg, 1: quadratic Reg, 2: neuronal network
        self.header['AltAnz']       = raw[6] # Number of altitude levels

        # - Development. Show header. 
        ###utils.print_dict(self.header)

        # - Bytes pointer
        bytes_pointer = bytes_header # current pointer position

        # - We know now how many samples and altitude levels
        #   we have to expect. Based on those infos we can 
        #   create the altitude format string (ALTFMT) to read
        #   the altitudes and the data format string (DATAFMT)
        #   to read the profiles.
        ALTFMT  = '<' + 'I'*self.header['AltAnz']
        # - Number of bytes for the altitudes record
        bytes_altitude = self.header['AltAnz']*4
        self.altitudes = struct.unpack(ALTFMT,bytes_read[bytes_pointer:bytes_pointer+bytes_altitude])
        bytes_pointer = bytes_pointer + bytes_altitude

        # -----------------------------------------------------------
        # - First reading profiles of absolute humidity 
        #   Length of one of the profile records is equal to
        #   the number of altitudes plus 5 bytes for the time and rainflag
        bytes_data = 5+self.header['AltAnz']*4
        # - Reading data for absolute humidity 
        DATAFMT = '<'
        for sample in range(self.header['N']):
            DATAFMT = DATAFMT + 'Ic' + 'f'*self.header['AltAnz']
        raw = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+self.header['N']*bytes_data])
        bytes_pointer = bytes_pointer + self.header['N']*bytes_data

        # - Prepare profiles of absolute humidity
        #   a numpy ndarray for the profiles (sample 1 to sample N
        #   in columns) and profile meta info (containing
        #   the time of the sample and a rain flag)
        self.profile = np.ndarray( (self.header['AltAnz'],self.header['N']),dtype='float')
        self.profilemeta = []
        index = 0
        for sample in range(self.header['N']):
            self.profilemeta.append( {'time':raw[index],
                                      'rainflag':ord(raw[index+1])} )
            self.profile[:,sample] = raw[index+2:index+2+self.header['AltAnz']]
            index = index + 2+self.header['AltAnz']

        # -----------------------------------------------------------
        # - In between the profiles of absolute and relative humidity
        #   there are two further "header" infos. Read them.
        raw = struct.unpack('<ff',bytes_read[bytes_pointer:bytes_pointer+8])
        self.header['RHMin']         = raw[0] # Minimum record of rel humidity 
        self.header['RHMax']         = raw[1] # Minimum record of rel humidity 
        bytes_pointer = bytes_pointer + 8
        

        # -----------------------------------------------------------
        # - Now relative humidity profiles
        #   Length of one of the profile records is equal to
        #   the number of altitudes plus 5 bytes for the time and rainflag
        bytes_data = 5+self.header['AltAnz']*4
        # - Reading data for absolute humidity 
        DATAFMT = '<'
        for sample in range(self.header['N']):
            DATAFMT = DATAFMT + 'Ic' + 'f'*self.header['AltAnz']
        raw = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+self.header['N']*bytes_data])
        bytes_pointer = bytes_pointer + self.header['N']*bytes_data


        # - Prepare profiles of relative humidity
        #   a numpy ndarray for the profiles (sample 1 to sample N
        #   in columns) and profile meta info (containing
        #   the time of the sample and a rain flag)
        self.rh_profile = np.ndarray( (self.header['AltAnz'],self.header['N']),dtype='float')
        self.rh_profilemeta = []
        index = 0
        for sample in range(self.header['N']):
            self.rh_profilemeta.append( {'time':raw[index],
                                         'rainflag':ord(raw[index+1])} )
            self.rh_profile[:,sample] = raw[index+2:index+2+self.header['AltAnz']]
            index = index + 2+self.header['AltAnz']


        fid.close()


    # --------------------------------------------------------------- 
    def printdata(self):

        print 'printdata method of class ' + self.__class__.__name__ + ' offline'
        #print 'z T0 T1'
        #for i in range(0,self.levels):
        # print '%f %f %f' % tuple(self.data[i,])

