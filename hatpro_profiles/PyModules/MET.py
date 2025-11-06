# -------------------------------------------------------------------
# - NAME:        MET.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-02-06
# -------------------------------------------------------------------
# - DESCRIPTION: The MET class can read binary HATPRO files 
#                containing meteorological parameters. To be specific:
#                pressure, temperature and relative humidity.
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


class MET(object):

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
        ###self.printdata()

    # -----------------------------------------------------------
    # - Reading the binary data
    def readdata(self):
    
        fid = open(self.infile,'rb')
        bytes_read = fid.read()

        # - Create binary format
        #   Note: Head changes if there are additional sensors! 
        HEADFMT = '<IIc'+'ff'*3

        # - Reading header first
        bytes_header = 9 + 8*3
        raw = struct.unpack(HEADFMT,bytes_read[0:bytes_header])
        self.header = {}
        self.header['METCode']      = raw[0] # MET-Filecode (==599658943) 
        self.header['N']            = raw[1] # Number of records 
        self.header['AddSensorFlag'] = ord(raw[2]) # Indicator for additional sensors
        self.header['METMinP']      = raw[3] # Minimum of recorded pressure value 
        self.header['METMaxP']      = raw[4] # Maximum of recorded pressure value
        self.header['METMinT']      = raw[5] # Minimum of environmental temperature value
        self.header['METMaxT']      = raw[6] # Maximum of environmental temperature value
        self.header['METMinH']      = raw[7] # Minimum of recorded relative humidity 
        self.header['METMaxH']      = raw[8] # Maximum of recorded relative humidity
        self.sensors = ['PS','TS','HS']

        bytes_pointer = bytes_header

        ADD = self.header['AddSensorFlag']
        NUMBER_ADD_SENSORS = 0
        # - If bit 0 is 1, there is additional wind speed only
        if ADD == 1:
            NUMBER_ADD_SENSORS = 1
            raw = struct.unpack('<ff',bytes_read[bytes_pointer:bytes_pointer+NUMBER_ADD_SENSORS*8])
            self.header['METMinff']      = raw[0] # Minimum of recorded wind speed 
            self.header['METMaxff']      = raw[1] # Maximum of recorded wind speed 
            bytes_pointer = bytes_pointer + NUMBER_ADD_SENSORS*8
            self.sensors.append('ff')

        # - If bit 1 is 1, there is additional wind direction only
        elif ADD == 2:
            NUMBER_ADD_SENSORS = 1
            raw = struct.unpack('<ff',bytes_read[bytes_pointer:bytes_pointer+NUMBER_ADD_SENSORS*8])
            self.header['METMindd']      = raw[0] # Minimum of recorded wind direction 
            self.header['METMaxdd']      = raw[1] # Maximum of recorded wind direction
            bytes_pointer = bytes_pointer + NUMBER_ADD_SENSORS*8
            self.sensors.append('dd')

        # - If both, bit 0 and bit 1 are equal to 1, both are available
        elif ADD == 3:
            NUMBER_ADD_SENSORS = 2
            raw = struct.unpack('<ffff',bytes_read[bytes_pointer:bytes_pointer+NUMBER_ADD_SENSORS*8])
            self.header['METMinff']      = raw[0] # Minimum of recorded wind speed 
            self.header['METMaxff']      = raw[1] # Maximum of recorded wind speed 
            self.header['METMindd']      = raw[2] # Minimum of recorded wind direction 
            self.header['METMaxdd']      = raw[3] # Maximum of recorded wind direction
            bytes_pointer = bytes_pointer + NUMBER_ADD_SENSORS*8
            self.sensors.append('ff')
            self.sensors.append('dd')

        # - The total number of instruments is then
        #   the three default (temperature, pressure and humidity) plus
        #   the additional instruments if there were some.
        NSENSORS = 3 + NUMBER_ADD_SENSORS
        self.header['TotalSensorNumber'] = NSENSORS

        # - Now - before we can read the data - we have to read the time METTimeReference
        raw = struct.unpack('<I',bytes_read[bytes_pointer:bytes_pointer+4])
        self.header['METTimeRef']      = raw[0] # Time reference shit 
        bytes_pointer = bytes_pointer + 4

        # - Development. Show header. 
        #utils.print_dict(self.header)

        # - Now the different samples are following. Each sample
        #   consists of a "Time of sample", "Rainflag of sample", followed by
        #   measured "Pressure", "Temperature" and "Relative Humidity"
        DATAFMT = '<'
        for sample in range(self.header['N']):
            DATAFMT = DATAFMT + 'Ic'+'f'*NSENSORS
        raw = struct.unpack(DATAFMT,bytes_read[bytes_pointer:])
        fid.close()

        # - Prepare the data stuff.
        #   a numpy ndarray for the data plus an additional metainfo
        #   for each of the columns.
        self.profile = np.ndarray( (NSENSORS,self.header['N']),dtype='float')
        self.profilemeta = []
        index = 0
        for sample in range(self.header['N']):
            self.profile[:,sample] = raw[index+2:index+2+NSENSORS]
            self.profilemeta.append( {'time':raw[index],
                                      'rainflag':ord(raw[index+1])} )
            index = index + 2 + NSENSORS


    # --------------------------------------------------------------- 
    def printdata(self,fid=None):

        if fid == None:
            sys.exit('stop no file id to write BRT data to disc')

        fid.write('# %s %s\n' % ('Input file:',self.infile) )
        for k in self.header.keys():
            fid.write('# %s %s\n' % (k,str(self.header[k])) )

        # - Data
        fmt = '%14d %3s %20f\n'
        fid.write('# %s %s %s\n' % ('timestamp','sensor','value') )
        for m in range(len(self.profilemeta)):
            for s in range(len(self.sensors)):
                fid.write( fmt % (utils.timestamp(self.profilemeta[m]['time']), \
                             self.sensors[s], self.profile[s,m]) )


