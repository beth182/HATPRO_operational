# -------------------------------------------------------------------
# - NAME:        BLB.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-02-06
# -------------------------------------------------------------------
# - DESCRIPTION: The BLB class can read binary HATPRO files 
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


class BLB(object):

    infile  = None # default value
    config  = None
    pathsep = '/'

    def __init__(self, object):

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
        HEADFMT = '<III'

        # - Reading header first
        bytes_header = 3*4
        raw = struct.unpack(HEADFMT,bytes_read[0:bytes_header])
        self.header = {}
        self.header['BLBCode']      = raw[0] # TPC-File Code (=780798065)
        self.header['N']            = raw[1] # Number of records
        self.header['FreqAnz']      = raw[2] # Number of frequencies 

        # - Bytes pointer to know where we are
        bytes_pointer = bytes_header # 12

        # - Now reading the frequencies (GHz) and the measured 
        #   minimum and maximum brightnes temperatures for all frequencies.
        #   Length of the record is always self.header['FreqAnz'] * 4 bytes, float,
        #   stored on value bytes_data (also used later to read the measured 
        #   values of the samples).
        DATAFMT  = '<' + 'ff'*self.header['FreqAnz']
        bytes_data = self.header['FreqAnz']*8
        # - Reading minimum/maximum value pairs for all frequencies 
        minmax_tmp = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+bytes_data])
        bytes_pointer = bytes_pointer + bytes_data
        # - Reading measured BLBMin, increasing bytes_pointer
        self.header['BLBTimeRef'] = struct.unpack('<I',bytes_read[bytes_pointer:bytes_pointer+4])[0]
        bytes_pointer = bytes_pointer + 4
        # - Reading frequencies 
        DATAFMT = '<' + 'f'*self.header['FreqAnz']
        bytes_data = self.header['FreqAnz']*4 
        frequencies_tmp = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+bytes_data])
        self.frequencies = []
        for freq in frequencies_tmp: self.frequencies.append( round(freq,3) )
        bytes_pointer = bytes_pointer + bytes_data
        # - Reading number of measured angles
        self.header['AngleAnz'] = struct.unpack('<I',bytes_read[bytes_pointer:bytes_pointer+4])[0]
        bytes_pointer = bytes_pointer + 4
        # - Reading measured angles 
        DATAFMT = '<' + 'f'*self.header['AngleAnz']
        bytes_data = self.header['AngleAnz']*4
        angles_tmp = struct.unpack(DATAFMT,bytes_read[bytes_pointer:bytes_pointer+bytes_data])
        self.angles = []
        for angle in angles_tmp: self.angles.append( round(angle,3) )
        bytes_pointer = bytes_pointer + bytes_data

        # - We stored the minmax values onto minmax_tmp. Put them into the content
        #   with a nice readable name (mainly, add correct GHz frequence)
        for i in range(len(self.frequencies)):
            self.header['BLBMin_'+str(self.frequencies[i])] = minmax_tmp[(i*2)]
            self.header['BLBMax_'+str(self.frequencies[i])] = minmax_tmp[(i*2)+1]

        # - Development. Show header. 
        #utils.print_dict(self.header)

        # - Now the different samples are following. Each sample
        #   consists of a "Time of sample", "Rainflag of sample" and
        #   (self.header['AngleAnz']+1)*self.header['FreqAnz'] values. The +1
        #   is because each sample contains the temperature a 0deg on element 0.
        #   And this for each sample.
        DATAFMT = '<' + ('Ic' + 'f'*(1+self.header['AngleAnz'])*self.header['FreqAnz'])*self.header['N']
        # - Sample length is 'Time' + 'rainflag' + (1+AngleAnz)*FreqAnz
        SAMPLELENGTH = 2+(1+self.header['AngleAnz'])*self.header['FreqAnz']
        raw = struct.unpack(DATAFMT,bytes_read[bytes_pointer:])
        fid.close()

        # - Prepare the data stuff.
        #   Prepare ndarray for the data plus an additional
        #   profilemeta holding the meta info for each of the columns
        self.data = np.zeros( (self.header['FreqAnz'],1+self.header['AngleAnz'],self.header['N']),dtype='float')
        self.datameta = []
        # index for different samples in one file (self.header['N'])
        index = 0
        for sample in range(self.header['N']):
            # raw[0]=timestamp, raw[1]=rainflag, raw[2:SAMPLELENGTH]=values
            self.data[:,:,sample] = np.reshape(raw[index+2:index+SAMPLELENGTH], (self.header['FreqAnz'],1+self.header['AngleAnz']))
            self.datameta.append( {'time':raw[index],
                                   'rainflag':ord(raw[index+1])} )
            index = index + SAMPLELENGTH 
        ### dev ### print self.config['outfile']
        ### dev ### print " "
        ### dev ### out = open(self.config['outfile'],'w')
        ### dev ### # - FreqHeaderShit
        ### dev ### out.write('sample Freq A00 ')
        ### dev ### print len(self.angles)
        ### dev ### print self.angles
        ### dev ### out.write('A%f '*len(self.angles) % tuple(self.angles) )
        ### dev ### out.write('\n')
        ### dev ### for sample in range(self.header['N']):
        ### dev ###     for i in range(self.data.shape[0]):
        ### dev ###         print self.data.shape[1]
        ### dev ###         print self.data.shape
        ### dev ###         print ' X ',len(  self.data[i,:,sample] )
        ### dev ###         print sample
        ### dev ###         print "------------------"
        ### dev ###         out.write('%d ' % sample )
        ### dev ###         out.write('%f ' % self.frequencies[i] )
        ### dev ###         out.write('%f '*self.data.shape[1] % tuple( self.data[i,:,sample] ) )
        ### dev ###         out.write('\n')
        ### dev ### out.close()
        ### dev ### sys.exit()


    # --------------------------------------------------------------- 
    def printdata(self, fid=None):

        print('now printing BLB.dat')
        if fid == None:
            sys.exit('stop no file id to write BLB data to disc')

        fid.write('# %s %s\n' % ('Input file:',self.infile) )
        for k in self.header.keys():
            fid.write('# %s %s\n' % (k,str(self.header[k])) )

        # - Data
        fmt = '%14d %4.2f %6.2f %20f\n'
        fid.write('# %s %s %s %s\n' % ('timestamp','elevation','frequence','value') )
        # 10 angles + 1 for ground temperature measured by sensor
        angles_adjusted = self.angles ; angles_adjusted.append(0.0)
        # loop over timestamps (written in profilemeta
        for m in range(len(self.datameta)):
            for a in range(len(self.angles)):
                for f in range(len(self.frequencies)):
        	    # utils timestamp converts timestamp from 1.1.2001 to unix-timestamp
                    fid.write( fmt % (utils.timestamp(self.datameta[m]['time']), \
                                 self.angles[a], \
                                 self.frequencies[f],\
        			 self.data[f,a,m]) )
