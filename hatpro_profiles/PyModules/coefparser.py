# -------------------------------------------------------------------
# - NAME:        coefparser.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-03-05
# -------------------------------------------------------------------
# - DESCRIPTION: Reading Giovannis coefficient files and put them
#                in a coefparser object to use them later for the
#                linear/quadratic regression.
# -------------------------------------------------------------------
# - EDITORIAL:   2014-03-05, RS: Created file.
# -------------------------------------------------------------------

import sys, os
import numpy as np
import re

class coefparser(object):

    # The important thing here is self.content.
    # keywords are: ['RT', 'PS', 'FR', 'RP', 'AG', 'CC', 'HS', 'IS', 'DB',
    #                 'TS', 'VN', 'AL', 'TL', 'RB', 'SL', 'TQ', 'OS']
    # RT = retrieval type
    # PS = barometric pressure sensor
    # FR = frequencies
    # RP = retrieval product
    # AG = angles
    # CC = customer ID (UIBK)
    # HS = surface humidtiy sensor
    # IS = infrared radiometer
    # DB = data base
    # TS = environmental surface temperature sensor
    # VN = version number
    # AL = altitude levels
    # TL = brightness temp. linear coefficients
    # RB = retrieval based on (brightness temp)
    # SL = sensor linear coefficients
    # TQ = brightness temp. quadratic coefficients
    # OS = offset

    # - Required variables the coefficient file has to have.
    #   If not, we have to stop.
    REQUIRED = {'RT':'Retrieval Type',
                'AL':'Definition of altitude leves',
                'FR':'Definition of frequencies',
                'AG':'Definition of measurement angles'}

    # - character indicating a comment line
    COMMENTLINE = '#'
    EMPTYSTRING = ''

    def __init__(self,object):

        self.infile = None
        # - Take inputs
        for o in object:
            if o == 'infile':
                self.infile = object[o]

        if self.infile == None:
            sys.exit('No input file given to coefparser')
        else:
            if not os.path.isfile(self.infile):
                sys.exit('Input file '+self.infile+' does not exist!')

        # - Reading data
        self.parse_the_file()

        #print(len(self.content['FR']))
        #number_of_frequencies = len(self.content['FR'])
        #number_of_altitudes   = len(self.content['AL'])
        #for block in range(len(self.content['TL'])):
        #    ncol = int(len(self.content['TL'][block])/number_of_altitudes)
        #    self.content['TL'][block] = np.reshape( self.content['TL'][block], \
        #            (number_of_altitudes,ncol) ).shape
        #    print(self.content['TL'][block].shape)

        #print('ich werfe hier beim reshapen alle anderen infos irgendwie weg')
        #print(self.content['TL'])
        #print(len(self.content['TL']))
        #print(len(self.content['TL'][0]))

    def parse_the_file(self):

        print('* Parsing coefficient file '+self.infile)

        # - Dict to store the results
        self.content = {}

        # - Try to open the file and read the content
        try:
            fid = open(self.infile,'r')
        except:
            sys.exit('Cannot open the file '+self.infile)

        # -----------------------------------------------------------
        # - Looping over the file
        head = True # we are in the header section
        # fid: file we're looking at
        for line in fid:
            # - Remove line breaks and shit
            # .replace(old, new)
            # every line has \n\r at the end -> remove this
            line = line.replace('\n','').replace('\r','')
            # re.sub: search for substring(0) and replace by (1) in (2)
                # TODO: probably leave out? didn't find occurrence
            line = re.sub(' +',' ',line)

            if 'ID-Code' in line: continue # Skip this line
            # - Found the (comment line) which indicates the beginning
            #   of the coefficient section
            #   looks like this: #--------Retrieval Coefficients------	
            elif line.strip().startswith(self.COMMENTLINE) and \
                 'Retrieval Coefficients' in line:

                # - We finished reading the header line. Note that
                #   there are some variables which are required 
                #   for the rest of the algorythm. Checking them.
                #   If one is missing, stop.
        	#   The keys we check for: RT, AL, FR, AG
                self.__check_content_head__(self.content)
                head = False # No more in the header section
                insection = False # starts 'not being in a coefficient section'
                section_data = [] # Initialize new list object

            # -------------------------------------------------------
            # - If we are in the header section, try to read
            #   all the header stuff.
            if head:
                if line.strip().startswith(self.COMMENTLINE):
                    continue
                else:
                    # try to evaluate this shit
        	    # SW: originally: line.split('#')[0].split('=')
                    data = line.split('=')
                    if not len(data) == 2:
                        sys.exit('Misconfiguration in head of file '+self.infile)
        	    # data[0] describes variable -> TS, HS, PS...
                    self.content[data[0]] = [] 
        	    # data[1] contains numbers following after =
                    for elem in data[1].split(' '): 
        	    # splitting these looks like: ['', '', '', '', '', '51.260', ''...
                        if len(elem) > 0:
                            try:
                                self.content[data[0]].append( float(elem) )
                            except:
                                self.content[data[0]].append( elem )
            # -------------------------------------------------------
            # - Allready in the data section. Here we have to
            #   decide if we are actually reading a coefficient
            #   section or not. A section always starts with a lilne
            #   without leading self.COMMENTLINE and a '=' in it.
            #   If we have found such a section we have to read until
            #   we find the next comment line which indicates the end
            #   of such a section.
            else:

                # - If we are not in a section and there is no = in 
                #   the line, skip.
        	# @ insection = FALSE; no '='
                if not insection and not '=' in line:
                    continue
                # - End of section?
        	# @ insection = TRUE; starts with '#'
                elif insection and line.strip().startswith(self.COMMENTLINE):
                    # - Else append
                    self.__reshape_section_data__(section_data,section_name,self.content)
                    # - Clear tmp list
                    section_data = []
                    insection = False
                # - Oh, found a new section!
        	# @ insection = FALSE; '=' found in the line
                elif not insection and '=' in line:
                    # - Extracting 'variable' name
                    section_name = line.split('=')[0].strip() 
                    if not section_name in self.content.keys():
                        print('  Adding section '+section_name)
                        self.content[section_name] = []
                    for elem in line.split('#')[0][3:].split(' '):
                        if len(elem) > 0:
                            try:
                                section_data.append( float(elem) )
                            except:
                                sys.exit('No floating point number!!')
                    insection = True # Now we are in a section
                # - If we are in a section
                elif insection:
                    # - Getting data from the line
                    for elem in line.split('#')[0].split(' '):
                        if len(elem) > 1:
                            try:
                                section_data.append( float(elem) )
                            except:
                                sys.exit('No floating point number!!')
            # -------------------------------------------------------
            
        # - We are at the end of the file, but the last section
        #   hasn't been checked and added to the content.
        #   Do that now, else you are missing the last block.
        self.__reshape_section_data__(section_data,section_name,self.content)



    # ---------------------------------------------------------------
    # - Checking the head of coefficient file (in content). There
    #   are several required variables we need to have. If they 
    #   are missing, stop immediatly.
    # ---------------------------------------------------------------
    def __check_content_head__(self,content):

        # - Checking REQUIRED variables
        for key in self.REQUIRED.keys():
            if key in content.keys():
                print(('  - {}:   {} '.format( self.REQUIRED[key], (content[key]) )))
            else:
                print('  ! Hanv\'t found %s in the header of the coefficient file!' % \
                      ( self.REQUIRED[key] ))

    # ---------------------------------------------------------------
    # - Reshaping the coefficient blocks. We are reading them
    #   as a list object. For some checks and better handling for
    #   the algorithm we have to reshape the data and put them
    #   into a numpy array.
    # ---------------------------------------------------------------
    def __reshape_section_data__(self,section_data,section_name,content):

        # - The coefficient blocks can have two different forms.
        #   Form a) is a simple vector (only measured at zenit angle 90. deg)
        #           with length of the altitude levels.
        #   Form b) is a matrix of where the number of rows correspond
        #           to the altitudes and the columns either to the 
        #           number of frequencies OR the number of angles.
        #           This depends on the RT (Retrieval Type)
        #   Form c) the whole thing is empty. This can be the case
        #           for example for the sensor coefficients which are
        #           not always in use.
        #   Each of the blocks corresponds to a special frequency.
        #   They have to be in the correct order (blocks in the same
        #   order as self.frequencies()

        # - Number of columns, depend on retrieval type
        if self.retrieval_type() == 0:
            colnumber = len(self.angles())
        elif self.retrieval_type() == 1:
            colnumber = len(self.frequencies())
        else:
            sys.exit('Unknown Type')
        
        # - Case a: only a vector of length self.altitudes
        if len(section_data) == len(self.altitudes()):
            #print("  - Reshape %-2s:   %d x %d" % (section_name, len(self.altitudes()), 1))

            # - 2d array with one column
            data = np.reshape( section_data, (len(self.altitudes()),1) )
            # - Append data to the content
            self.content[section_name].append( data )

        # - Case b: matrix of size length self.altitudes vs. second dimension
        #   based on self.retrieval_type.
        elif len(section_data) == len(self.altitudes())*colnumber: 
            #print("  - Reshape %-2s:   %d x %d" % (section_name, len(self.altitudes()), colnumber))

            # - 2d array with one column
            data = np.reshape( section_data, (len(self.altitudes()),colnumber) )
            # - Append data to the content
            self.content[section_name].append( data )

        # - Case c: totally empty, skip.
        elif len(section_data) == 0:
            print("  - Cannot reshape %s, is empty. Unused. Skip." % (section_name))
        else:
            print("   huch ", len(section_data))
            sys.exit('EXIT: does not fit case a, b, or c in __reshape_section_data__')





    # ---------------------------------------------------------------
    # - Some return methods for simpler access
    # ---------------------------------------------------------------
    def altitudes(self):
        return self.content['AL']
    def angles(self):
        return self.content['AG']
    def frequencies(self):
        return self.content['FR']
    def retrieval_type(self):
        return int(self.content['RT'][0])








