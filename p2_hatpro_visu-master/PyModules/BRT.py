# -------------------------------------------------------------------
# - NAME:        BRT.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-02-06
# -------------------------------------------------------------------
# - DESCRIPTION: The BRT class can read binary HATPRO files 
#                containing the measured brightness temperatures.
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


class BRT(object):

    infile  = None # default value
    config  = None
    pathsep = '/'

    def __init__(self,object):

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
        #####self.printdata()     

    # -----------------------------------------------------------
    # - Reading the binary data
    def readdata(self):
    
        fid = open(self.infile,'rb')
        bytes_read = fid.read()

        # - Create binary format
        HEADFMT = '<IIII'

        # - Reading header first
        bytes_header = 4*4
        raw = struct.unpack(HEADFMT,bytes_read[0:bytes_header])
        self.header = {}
        self.header['BRTCode']      = raw[0] # TPC-File Code (=780798065)
        self.header['N']            = raw[1] # Number of records
        self.header['TPCTimeRef']   = raw[2] # Time reference (1:UTC, 0:Local Time)
        self.header['FreqAnz']      = raw[3] # Number of recorded frequencies

        # - Development. Show header. 
        #utils.print_dict(self.header)

        # - Now reading the frequencies (GHz) and the measured 
        #   minimum and maximum brightnes temperatures for all frequencies.
        #   Length of the record is always self.header['FreqAnz'] * 4 bytes, float,
        #   stored on value bytes_data (also used later to read the measured 
        #   values of the samples).
        DATAFMT  = '<' + 'f'*self.header['FreqAnz']
        bytes_data = self.header['FreqAnz']*4
        # - The bytes-pointer
        bytes_pointer = bytes_header
        # - Reading frequencies, increasing bytes_pointer
        frequencies_tmp = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+bytes_data])
        self.frequencies = []
        for freq in frequencies_tmp: self.frequencies.append( round(float(freq),3) )
        bytes_pointer = bytes_pointer + bytes_data
        # - Reading measured BRTMin, increasing bytes_pointer
        self.minimum = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+bytes_data])
        bytes_pointer = bytes_pointer + bytes_data
        # - Reading measured BRTMax, increasing bytes_pointer
        self.maximum = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+bytes_data])
        bytes_pointer = bytes_pointer + bytes_data

        # - Now the different samples are following. Each sample
        #   consists of a "Time of sample", "Rainflag of sample" and self.header['FreqAnz']
        #   measured brightness temperatures and last but not least a 
        #   "Elevation/Azimuth angle of sample (DEG)" 
        DATAFMT = '<'
        for sample in range(self.header['N']):
            DATAFMT = DATAFMT + 'Ic' + 'f'*self.header['FreqAnz'] + 'f'
        raw = struct.unpack(DATAFMT,bytes_read[bytes_pointer:])
        fid.close()

        # - Prepare the data stuff.
        #   Prepare ndarray for the data plus an additional
        #   profilemeta holding the meta info for each of the columns
        self.profile = np.ndarray( (self.header['FreqAnz'],self.header['N']),dtype='float')
        self.profilemeta = []
        index = 0
        for sample in range(self.header['N']):
            self.profile[:,sample] = raw[index+2:index+2+self.header['FreqAnz']]
            self.profilemeta.append( {'time':raw[index],
                                      'rainflag':ord(raw[index+1]),
                                      'elevation':raw[index+2+self.header['FreqAnz']]} )
            index = index + 2+self.header['FreqAnz'] + 1


    # --------------------------------------------------------------- 
    def printdata(self,fid=None):
        
        print('now printing BRT.dat')
        if fid == None: 
            sys.exit('stop no file id to write BRT data to disc')

        fid.write('# %s %s\n' % ('Input file:',self.infile) )
        for k in self.header.keys():
            fid.write('# %s %s\n' % (k,str(self.header[k])) )

        # - Data
        # timestamp, elevation angle, frequence, measured value
        fmt = '%14d %4.2f %6.2f %20f\n'
        fid.write('# %s %s %s %s\n' % ('timestamp','elevation','frequence','value') )
        for m in range(len(self.profilemeta)):
            for f in range(len(self.frequencies)):
                fid.write( fmt % (utils.timestamp(self.profilemeta[m]['time']), \
                             self.profilemeta[m]['elevation'], \
                             self.frequencies[f], self.profile[f,m]) )





















