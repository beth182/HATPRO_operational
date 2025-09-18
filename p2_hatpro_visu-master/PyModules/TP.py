# -------------------------------------------------------------------
# - NAME:        TP.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-02-06
# -------------------------------------------------------------------
# - DESCRIPTION: The TP class can read binary HATPRO files 
#                of form TPC (Temperature Profile Chart Full Trop.)
#                and of form TPB (Temperature Profile Chart
#                Boundary Layer). 
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


class TP(object):

# object: dictionary with 'infile', 'config', 'theta', 'indegrees'

    def __init__(self,object):

        self.infile     = None # default value
        self.config     = None
        self.indegrees  = False # Kelvin (F) or Degrees Celsius (T)?
        self.theta      = False # default, dont compute theta values
        self.tgradient  = 0.01 # temperatur gradient per metre (1K per 100m)
        self.pathsep    = '/'


        for o in object:
            if o == 'infile':
                infile = object[o]
            if o == 'config':
                self.config = object[o]
            if o == 'theta':
                self.theta = object[o]
            if o == 'indegrees':
                self.indegrees = object[o]

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
        #self.printdata()

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
        self.header['TPCMin']       = raw[2] # Minimum of recorded temperatures 
        self.header['TPCMax']       = raw[3] # Maximum of recorded temperatures
        self.header['TPCTimeRef']   = raw[4] # Time reference (1:UTC, 0:Local Time)
        self.header['TPCRetreival'] = raw[5] # 0: linear Reg, 1: quadratic Reg, 2: neuronal network
        self.header['AltAnz']       = raw[6] # Number of altitude levels

        # - Development. Show header. 
        #utils.print_dict(self.header)

        # - We know now how many samples and altitude levels
        #   we have to expect. Based on those infos we can 
        #   create the altitude format string (ALTFMT) to read
        #   the altitudes and the data format string (DATAFMT)
        #   to read the profiles.
        ALTFMT  = '<' + 'I'*self.header['AltAnz']
        bytes_altitude = self.header['AltAnz']*4 + bytes_header
        self.altitudes = struct.unpack(ALTFMT,bytes_read[bytes_header:bytes_altitude])

        # - Reading data
        DATAFMT = '<'
        for sample in range(self.header['N']):
            DATAFMT = DATAFMT + 'Ic' + 'f'*self.header['AltAnz']
        raw = struct.unpack(DATAFMT,bytes_read[bytes_altitude:])
        fid.close()

        # - Prepare the data stuff.
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

        # - Compute potential temperature if theta is set to True
        if self.theta:
            for i in range(len(self.altitudes)):
                self.profile[i,:] = self.profile[i,:] + self.altitudes[i]*self.tgradient

        # - Convert Kelvin to Degrees Celsius?
        if self.indegrees:
            self.profile = self.profile - 273.15



    # ---------------------------------------------------------------
    # - Write some output to an ascii file. Development version (?)
    def write_to_ascii(self,filename):

        if not os.path.isfile(filename):
            writehead = True
        else:
            writehead = False

        print '  Write data to '+filename

        # - Take mean values of all samples
        data = np.mean(self.profile,1)

        # - Number of elements
        elements = len(self.altitudes)

        fid = open(filename,'a+')

        if writehead:
            fid.write('-99999 ')
            for a in self.altitudes:
                fid.write('%d ' % a)
            fid.write('\n')


        time = utils.timestamp(self.profilemeta[0]['time'])
        fid.write('%d ' % time)
        for d in data:
            fid.write('%f ' % d)
        fid.write('\n')

        fid.close()


    # ---------------------------------------------------------------
    def printdata(self):

        print 'printdata method of class ' + self.__class__.__name__ + ' offline'
        #print 'z T0 T1'
        #for i in range(0,self.levels):
        # print '%f %f %f' % tuple(self.data[i,])

