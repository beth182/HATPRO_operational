# -------------------------------------------------------------------
# - NAME:        retrievalrh.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-03-06
# -------------------------------------------------------------------
# - DESCRIPTION: retrieval for relative humidity
# -------------------------------------------------------------------
# - EDITORIAL:   2014-03-06, RS: Created file.
# -------------------------------------------------------------------

import sys, os
from coefparser import coefparser
import numpy as np
import utils
from datetime import datetime as dt

class retrievalrh( object ):

    def __init__(self,config,periods,db):

        # - Getting input arguments
        self.config = config
        self.periods = periods
        self.db = db

        # - Loading coefficients
        self.__load_coefficients__()

        # - Getting averaged data from the database for
        #   what we need. We need MET and BLB for the temperature
        #   retrieval and MET and BRT for the humidity algorithm.
        self.MET = self.db.get_averaged_data(self.periods,'MET')
        #self.BLB = self.db.get_averaged_data(self.periods,'BLB')
        self.BRT = self.db.get_averaged_data(self.periods,'BRT')

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

        # - Get corrected humidity profiles:
        RESULT = self.apply_retrieval_algorithm(beta,x_matrix)

        # - Result to database
        self.db.write_RESULT_to_db(RESULT,'RESULT_rh')

    # ---------------------------------------------------------------
    # - Create "beta" matrix containing the coefficients. The matrix
    #   is of size "altitude (row) times terms in equation" which is
    #   based on "offset", "sensor coefficient", "linear/quadratic terms"
    #   and can have variouse sizes. 
    # ---------------------------------------------------------------
    def get_beta_matrix(self):

        beta = None 

        # - Just because I have less to write then ..
        content = self.coef.content

        # - If the retreival_type does not match what I knew at the
        #   moment I wrote the script, exit.
        #   For relative humidity (and we are in the retreival for rh)
        #   the retrieval_type has to be 1
        if not int(self.coef.retrieval_type()) == 1:
            utils.exit('Found fancy/wrong retrieval type for relative humidity!')

        # - Predictor information (which column should contain
        #   which predictor variable?). x_exp contains the exponent.
        #   There are quadratic terms in the equations.
        x_info = []; x_exp = []

        # -----------------------------------------------------------
        # - Decide which retrieval type it is. RT (retrieval type 0) has
        #   coefficients along the elevation angle of the scan while
        #   RT=1 (retrieval type 1) goes along frequencies
        if self.coef.retrieval_type() == 0:
            print '  Retrieval type RT=0: coefficients for different angles'
            coef_dimension = self.coef.angles()
        elif self.coef.retrieval_type() == 1:
            print '  Retrieval type RT=0: coefficients for different frequencies'
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
            for sensor in ['TS','HS','PS','IS']:
                if int(content[sensor][0]) == 1:
                    x_info.append( sensor ); x_exp.append(1)
                    sensor_counter = sensor_counter+1
            if not sensor_counter == content['SL'][0].shape[1]:
                utils.exit('Found more sensors which should be used as coefficients!')

        # -----------------------------------------------------------
        # - Adding linear coefficients 
        if 'TL' in content.keys() and len(content['TL']) > 0:
            print '  Number of linear brigthness temperature coefficient sets: %d' % len(content['TL'])
            for block in range(len(content['TL'])):
                # - Check and add data
                if not content['TL'][0].shape[0] == beta.shape[0]:
                    utils.exit('Found linear coefficients but the size does not match ' + \
                               'the size of the beta matrix!')
                beta = np.hstack( (beta,content['TL'][block]) ) 
                # - Predictor info
                if content['TL'][0].shape[1] == 1:
                    x_info.append( coef_dimension[0] )
                    x_exp.append(1)
                elif not  content['TL'][0].shape[1] == len(coef_dimension):
                    utils.exit('Columns of coefficients do not fit the setup shit!')
                else:
                    for elem in coef_dimension:
                        x_info.append( elem )
                        x_exp.append(1)

        # -----------------------------------------------------------
        # - Adding quadratic coefficients 
        if 'TQ' in content.keys() and len(content['TQ']) > 0:
            print '  Number of linear brigthness temperature coefficient sets: %d' % len(content['TQ'])
            for block in range(len(content['TQ'])):
                # - Check and add data
                if not content['TQ'][0].shape[0] == beta.shape[0]:
                    utils.exit('Found quadratic coefficients but the size does not match ' + \
                               'the size of the beta matrix!')
                beta = np.hstack( (beta,content['TL'][block]) ) 
                # - Predictor info
                if content['TQ'][block].shape[1] == 1:
                    x_info.append( coef_dimension[0] )
                    x_exp.append(2)
                elif not  content['TQ'][block].shape[1] == len(coef_dimension):
                    utils.exit('Columns of coefficients do not fit the setup shit!')
                else:
                    for elem in coef_dimension:
                        x_info.append( elem )
                        x_exp.append(2)

        # - Does the size of the beta matrix fits the number
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
            # - Nice list of all timestamps we have to search for
            timestamp = [];
            for p in range(len(self.periods)): timestamp.append( self.periods[p][1] )
            # - Resulting data list
            result = []
            # - find correct observation for a given
            #   time periode (timestamp) and variable.
            for line in self.MET:
                for time in timestamp: 
                    if line[0] == time and line[1] == info:
                        result.append( line[2]**exp )
            return result
        # -----------------------------------------------------------
        def get_BRT_values(info,exp):
            # - Nice list of all timestamps we have to search for
            timestamp = [];
            for p in range(len(self.periods)): timestamp.append( self.periods[p][1] )
            # - Resulting data list
            result = np.zeros( (len(self.periods)) ) 
            # - find correct observation for a given
            #   time periode (timestamp) and variable.
            for line in self.BRT:
                for t in range(len(self.periods)):
                    time = self.periods[t][1]
                    if line[0] == time and line[1] == info:
                        result[t]  = line[2]**exp
            return result
        # -----------------------------------------------------------


        # -----------------------------------------------------------
        # - Main part of the method: looping over x_info which contains
        #   the information about which measured value should be in
        #   which column of the x_matrix. Find value, store.

        # - Create empty matrix to store the data first
        x_matrix = np.zeros( (len(self.periods),len(x_info)), dtype='float' )

        for i in range(len(x_info)):

            info = x_info[i]

            # - Simplest case, offset.
            if info == 'offset':
                x_matrix[:,i] = 1.
                continue
            elif info in ['TS','HS','PS','IS']:
                x_matrix[:,i] = get_obs_values(info,float(x_exp[i]))
            else:
                x_matrix[:,i] = get_BRT_values(info,float(x_exp[i]))

        ####if not np.sum(x_matrix == 0.) == 0:
        ####    utils.exit('tried to build the x_matrix but I haven\'t found all values!')


        return x_matrix

    # ---------------------------------------------------------------
    # - This thing returns the result. This was the reason to
    #   do all the code.
    # ---------------------------------------------------------------
    def apply_retrieval_algorithm(self,beta,x_matrix):

        # - Nice list of all timestamps we have to search for
        timestamp = [];
        for p in range(len(self.periods)): timestamp.append( self.periods[p][1] )

        # - The final list
        RESULT = []

        # - Outer loop goes over all periods
        for t in range(len(timestamp)):
            time = timestamp[t]
            print '  Apply coefficients to %s' % dt.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
            # - Looping over altitudes
            for a in range(len(self.coef.altitudes())):
                altitude = self.coef.altitudes()[a]

                # - If there are 0.s in the x_matrix, there are
                #   missing data. Skip. 
                if np.sum( np.where( x_matrix[t,:] == 0 ) ) > 0:
                    continue 

                RES = np.sum(np.multiply(x_matrix[t,:],beta[a,:]))
                RESULT.append( (time,altitude,RES) )

        return RESULT

    # ---------------------------------------------------------------
    # - Loading coefficients
    # ---------------------------------------------------------------
    def __load_coefficients__(self):

        # - Reading coefficients
        print '\n* Reading the coefficients file for relative humidity'
        #print '  File is: %s' % self.config['coef_rh']
        self.coef = coefparser({'infile':self.config['coef_rh']})


    

















