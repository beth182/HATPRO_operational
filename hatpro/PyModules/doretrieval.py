# -------------------------------------------------------------------
# - NAME:        doretrieval.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-03-06
# -------------------------------------------------------------------
# - DESCRIPTION: Applying regression coefficients to (averaged) data
#           	 The Calculations are made by multiplying the beta 
#        	 matrix (containing all the different coefficients for
#        	 different levels) with the x_matrix (HATPRO rawdata
#        	 for different timesteps).
# -------------------------------------------------------------------
# - EDITORIAL:   2014-03-06, RS: Created file.
#        	 2015-01-20, SW: retrieval without averaging
# -------------------------------------------------------------------

import sys, os
from coefparser import coefparser
import numpy as np
import utils
from datetime import datetime as dt
#import ipdb

class doretrieval( object ):

    def __init__(self,config,db,what):

        # - Getting input arguments
        self.config = config
        self.db = db
        self.what = what

        # - Create "self.timestep" which is nothing else than a list    
        #   just containing each second element of the tuples of 
        #   the periods. Or in other words: the timestamps of the
        #   end of all periods in self.periods. We need them later
        #   on when searching the correct observations.
        #for period in periods: self.timestamp.append( period[1] )

        if not what in ['rh','T']:
            utils.exit('wrong input \'what\' to retrieval method. Please use \'rh\' or \'T\'')

        # - Loading coefficients
        print('\n* Reading the coefficients file for {}: {}'.format(self.what, self.config['coef_'+self.what]))
        self.coef = coefparser({'infile':self.config['coef_'+self.what]})

        # - Getting averaged data from the database for
        #   what we need. We need MET and BLB for the temperature
        #   retrieval and MET and BRT for the humidity algorithm.
        #self.MET = self.db.get_averaged_data(self.timestamp,'MET')

        self.timestamp = []

        # - Load BLB data here
        if self.what == 'T':
            self.BLB = self.db.get_brightness_temp('BLB')
            #self.BLB = self.db.get_averaged_data(self.timestamp,'BLB')
            all_timestamps = [self.BLB[i][0] for i in range(0,len(self.BLB))]
            # BETH NOTE
            # commenting out because of indentation issue?
            # for stamp in all_timestamps:
        	# if stamp not in self.timestamp: self.timestamp.append(stamp)
        # - Load BRT data here
        if self.what == 'rh':
            self.BRT = self.db.get_brightness_temp('BRT')
            #self.BRT = self.db.get_averaged_data(self.timestamp,'BRT')
            all_timestamps = [self.BRT[i][0] for i in range(0,len(self.BRT))]
            for stamp in all_timestamps:
                if stamp not in self.timestamp: self.timestamp.append(stamp)
        # - Load MET data here
        self.t_min = min(self.timestamp)
        self.t_max = max(self.timestamp)
        self.MET = self.db.get_data_for_specific_timespan('MET',self.t_min,self.t_max)

        # - Getting beta matrix (containing all coefficients for
        #   all altitudes) and the predictor information on x_info.
        #   x_info will be used to generate the matrix X (or vector,
        #   if there is only one periode)
        #   x_exp is the exponent for each of those values.
        x_info, x_exp, beta = self.get_beta_matrix()

        # - Now create regressor matrix x based on x_info.
        #   Afterwards you just have to multiply those two
        #   matrizes (beta and x_matrix) to get the corrected values.
        x_matrix = self.get_predictor_matrix(x_info,x_exp)
        #ipdb.set_trace()
        # - Get corrected humidity profiles:
        self.result = self.apply_retrieval_algorithm(beta,x_matrix)

        # - Result to database
        #self.db.write_RESULT_to_db(RESULT,'RESULT_'+self.what)

    # ---------------------------------------------------------------
    # - Create "beta" matrix containing the coefficients. The matrix
    #   is of size "altitude (row) times terms in equation" which is
    #   based on "offset", "sensor coefficient", "linear/quadratic terms"
    #   and can have variouse sizes. 
    # ---------------------------------------------------------------
    def get_beta_matrix(self):

        beta = None 

        # - Just because I have less to write then ..
        #   content is a dictionary containing all the regression coeff.
        content = self.coef.content

        # - Predictor information (which column should contain
        #   which predictor variable?). x_exp contains the exponent.
        #   There are quadratic terms in the equations.
        x_info = []; x_exp = []

        # -----------------------------------------------------------
        # - Decide which retrieval type it is. RT (retrieval type 0) has
        #   coefficients along the elevation angle of the scan while
        #   RT=1 (retrieval type 1) goes along frequencies
        if self.coef.retrieval_type() == 0:
            print('  Retrieval type RT=0: coefficients for different angles')
            coef_dimension = self.coef.angles()
        elif self.coef.retrieval_type() == 1:
            print('  Retrieval type RT=1: coefficients for different frequencies')
            coef_dimension = self.coef.frequencies()
        else:
            utils.exit('Cannot handle retrieval_type '+str(self.coef.retrieval_type())+'!! Stop!')

        # -----------------------------------------------------------
        # - Is there an offset?
        if not 'OS' in content.keys():
            utils.exit('There is no offset in the coefficient file. Stop.')
        else:
            beta = content['OS'][0]
            x_info.append('offset')
            x_exp.append(1)

        # -----------------------------------------------------------
        # - Any sensor coefficients?
        if 'SL' in content.keys() and len(content['SL']) > 0:
            if not content['SL'][0].shape[0] == beta.shape[0]:
                utils.exit('Found coefficients for sensors but the size does not match ' + \
                           'the size of the offset values!')
            beta = np.hstack( (beta,content['SL'][0]) ) 
            # - Which sensor was it? Search for it and add
            #   the corresponding 'short name' to the x_info.
            sensor_counter = 0
            # - every sensor (TS, HS, PS, IS) is either set to 0 or 1
            for sensor in ['TS','HS','PS','IS']:
                if int(content[sensor][0]) == 1:
                    x_info.append( sensor );
                    # BETH NOTE
                    # This used to be one tab back - but put to here because if indentation error
                    x_exp.append(1)
                    sensor_counter = sensor_counter+1
            if not sensor_counter == content['SL'][0].shape[1]:
                utils.exit('Found more sensors which should be used as coefficients!')

        # -----------------------------------------------------------
        # - Adding linear coefficients 
        if 'TL' in content.keys() and len(content['TL']) > 0:
            print('  Number of linear brigthness temperature coefficient sets: %d' % len(content['TL']))
            for block in range(len(content['TL'])):


                # -Check and add data
        	#  (TS, HS, PS, IS are either set to 0 or 1
                if not content['TL'][0].shape[0] == beta.shape[0]:
                    utils.exit('Found linear coefficients but the size does not match ' + \
                               'the size of the beta matrix!')

                beta = np.hstack( (beta,content['TL'][block]) ) 

                # - Predictor info
        	#   This seam a bit complicated to me, I hope this is the right explanation:
        	#   Temperature: TL looks like this
        	#	X (X means 39 values in one column)
        	#	X
        	#	X
        	#	XXXXXXXXXX (10 X's since we have 10 different angles in scanning mode)
        	#	XXXXXXXXXX
        	#	XXXXXXXXXX
        	#	XXXXXXXXXX
        	#   Humidity: TL looks like this
        	#	XXXXXXX (7 columns since we have 7 frequencies)

        	# so this would be one of the first 3 X's for Temperature
                if content['TL'][block].shape[1] == 1:
                    #   we have to store ANGLE and FREQUENCE in x_info
                    if self.coef.retrieval_type() == 0:
                        x_info.append( [coef_dimension[0],self.coef.frequencies()[block]] )
                    else: #TODO: is this here needed at some time?
                        # BETH NOTE
                        # Moved indentation to what I assume is correct here
                        # print('there is something wrong here, check L184 in doretrieval.')
                        x_exp.append(1)
        	# - if the first 3 X's are done, check if the next line actually has
        	#   the right amount of X's (10 for Temp, 7 for Humidity)
                elif not  content['TL'][block].shape[1] == len(coef_dimension):
                    utils.exit('Columns of coefficients do not fit the setup shit!')
                else:
                    for elem in coef_dimension:
                        # - If we are in retrieval_type 0 (temperature)
                        #   we have to store ANGLE and FREQUENCE in x_info
                        if self.coef.retrieval_type() == 0:
                            x_info.append( [elem,self.coef.frequencies()[block]] )
                        else:
                            x_info.append( elem )
                        x_exp.append(1)

        # -----------------------------------------------------------
        # - Adding quadratic coefficients 
        #   (basically goes the same as adding linear coefficients)
        if 'TQ' in content.keys() and len(content['TQ']) > 0:
            print('  Number of quadratic brigthness temperature coefficient sets: %d' % len(content['TQ']))
            for block in range(len(content['TQ'])):
                # - Check and add data
                if not content['TQ'][0].shape[0] == beta.shape[0]:
                    utils.exit('Found quadratic coefficients but the size does not match ' + \
                               'the size of the beta matrix!')
                beta = np.hstack( (beta,content['TQ'][block]) ) 
                # - Predictor info
                if content['TQ'][block].shape[1] == 1:
                    # - If we are in retrieval_type 0 (temperature)
                    #   we have to store ANGLE and FREQUENCE in x_info
                    if self.coef.retrieval_type() == 0:
                        x_info.append( [coef_dimension[0],self.coef.frequencies()[block]] )
                    else:
                        x_info.append( coef_dimension[0] )
                    x_exp.append(2)
                elif not  content['TQ'][block].shape[1] == len(coef_dimension):
                    utils.exit('Columns of coefficients do not fit the setup shit!')
                else:
                    for elem in coef_dimension:
                        # - If we are in retrieval_type 0 (temperature)
                        #   we have to store ANGLE and FREQUENCE in x_info
                        if self.coef.retrieval_type() == 0:
                            x_info.append( [elem,self.coef.frequencies()[block]] )
                        else:
                            x_info.append( elem )
                        x_exp.append(2)

        # - Does the size of the beta matrix fit the number
        #   of altitudes of the coefficient file?
        if not len(self.coef.altitudes()) == beta.shape[0]:
            utils.exit('shit, matrix \'beta\' has more rows than we have ' + \
                       'altitude levels from the coefficient file! Stop.')

        return x_info, x_exp, beta


    # ---------------------------------------------------------------
    # - Create predictor matrix. 
    # ---------------------------------------------------------------
    def get_predictor_matrix(self,x_info,x_exp):

        # - A few functions only needed inside this method
        # - get_obs_values returns the observation for a given
        #   time period (averaged values) and a given sensor
        def get_obs_values(info,exp):
            # - Resulting data list
            result = []
            # - find correct observation for a given
            #   time (timestamp) and variable.
            #for line in self.MET:
            #    for time in self.timestamp: 
            #        if line[0] == time and line[1] == info:
            #            result.append( line[2]**exp )
            #            #print('%10d %10d %s %s %f'  % (line[0],time,line[2],info,exp))
            # create a list of all the MET entries with the info wee interested in
            met_eq_info = [entry for entry in self.MET if entry[1] == info]
            # - the unity may have to be changed
            #   for pressure (PS): hPa -> Pa
            factor_unity_conversion = 1
            if info == 'PS': factor_unity_conversion = 100
            for time in self.timestamp:
                # BETH NOTE
                #moving indentation to what I assume is correct here
                # search for closest MET
                nearest_MET_line = met_eq_info[min(range(len(met_eq_info)), key=lambda x:abs(met_eq_info[x][0]-time))]
                # append MET data to result, but only if time difference is not too large
                if abs(time-nearest_MET_line[0]) < self.config['MET_time_difference']:
                    result.append(factor_unity_conversion*(nearest_MET_line[2])**exp)
                else:
                    result.append(0.0)
                # for pressure, we need Pa instead of hPa -> multiply by 100
            return result
        # -----------------------------------------------------------
        def get_BRT_values(info,exp):
            # - Resulting data list
            result = []
            # - find correct observation for a given
            #   time periode (timestamp) and variable.
            #for line in self.BRT:
            #    for t in range(len(self.periods)):
            #        time = self.periods[t][1]
            #        if line[0] == time and line[1] == info:
            #            result[t]  = line[2]**exp
            #return result
            # first collect all self.BRT entries with matching info (frequence)
            brt_eq_info = [entry for entry in self.BRT if entry[1]==info]
            # second loop over the timestamps to fill in the 'column' for the x_matrix
            for time in self.timestamp:
                # find index where timestamps correspond
                ind_matching_time = [i[0] for i in brt_eq_info].index(time)
                # append correct value
                result.append((brt_eq_info[ind_matching_time][2])**exp)
            return result

        # -----------------------------------------------------------
        def get_BLB_values(info,exp):
            # - Nice list of all timestamps we have to search for
            # - Resulting data list
            result = []
            # - find correct observation for a given
            #   time periode (timestamp) and variable.
            #for line in self.BLB:
            #    for t in range(len(self.periods)):
            #        time = self.periods[t][1]
            #        #      timestamp           frequence               angle
            #        if line[0] == time and line[1] == info[1] and line[2] == info[0]:
            #            result[t]  = line[3]**exp
            #
            # first collect the self.BLB entries with matching info (frequence and angle)
            # self.BLB = timestamp, frequence, angle, value
            # info = angle, frequence
            #						  frequence		angle
            blb_eq_info = [entry for entry in self.BLB if entry[1]==info[1] and entry [2]==info[0]]
            # second loop over the timestamps to fill in the 'column' for the x_matrix
            for time in self.timestamp:
                # BETH NOTE
                # changing indentation here to what I assume is correct
                # find index where timestamps correspond
                ind_matching_time = [i[0] for i in blb_eq_info].index(time)
                # append correct value
                # result.append((blb_eq_info[ind_matching_time][3])**exp)
            return result
        # -----------------------------------------------------------


        # -----------------------------------------------------------
        # - Main part of the method: looping over x_info which contains
        #   the information about which measured value should be in
        #   which column of the x_matrix. Find value, store.

        # - Create empty matrix to store the data first
        x_matrix = np.zeros((len(self.timestamp),len(x_info)), dtype='float' )

        # - We have to search either in BRT or in BLB
        if self.what == 'rh':
            get_values = get_BRT_values
        else:
            get_values = get_BLB_values

        # - Fill x_matrix column by column.
        #   Depending on the info given by x_info we look for
        #   offset, MET-data or BLB/BRT-data
        for i in range(len(x_info)):

            info = x_info[i]

            # - Simplest case, offset.
            if info == 'offset':
                x_matrix[:,i] = 1.
                continue
            # - Sensors at HATPRO (MET-data)
            elif info in ['TS','HS','PS','IS']:
                x_matrix[:,i] = get_obs_values(info,float(x_exp[i]))
            # - Brightness Temperatures (BLB/BRT-data)
            else:
                x_matrix[:,i] = get_values(info,float(x_exp[i]))

        return x_matrix

    # ---------------------------------------------------------------
    # - This thing returns the result. This was the reason to
    #   do all the code.
    # ---------------------------------------------------------------
    def apply_retrieval_algorithm(self,beta,x_matrix):

        # - The final list
        RESULT = []

        # - Outer loop goes over all periods
        for t in range(len(self.timestamp)):
            time = self.timestamp[t]
            # - Looping over altitudes
            for a in range(len(self.coef.altitudes())):
                altitude = self.coef.altitudes()[a]

                # - If there are 0.s in the x_matrix, there are
                #   missing data. Skip. 
                if np.sum( np.where( x_matrix[t,:] == 0 ) ) > 0:
                    print(' --skip-- timestamp: {}, altitude: {} '.format(t,a))
                    continue 

        	# RES = sum(1 offset, 43 linear, 43 quadratic, sensors)
                RES = np.sum(np.multiply(x_matrix[t,:],beta[a,:]))
                RESULT.append( (time,altitude,RES) )

        	#print('height: ',altitude)
        	#print('Calc: {} *\n {}'.format(x_matrix[t,:],beta[a,:]))
        	#ipdb.set_trace()
 
        return RESULT

