# -------------------------------------------------------------------
# - NAME:        database.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-03-06
# -------------------------------------------------------------------
# - DESCRIPTION: Storage handling, sqlit3
# -------------------------------------------------------------------
# - EDITORIAL:   2014-03-06, RS: Created file.
# -------------------------------------------------------------------

import sys, os
import sqlite3
from hatpro.PyModules import utils
from datetime import datetime as dt

class database(object):

    def __init__(self,config):

        self.config = config
        print(self.config['dbfile'])
        self.__open_connection__()

    # ---------------------------------------------------------------
    # - Open the database connection first - try to reach the
    #   SQLITE file.
    # ---------------------------------------------------------------
    def __open_connection__(self):

        try:
            self.con = sqlite3.connect(self.config['dbfile'])
        except:
            sys.exc_info()[0]
            utils.exit('Cannot open sqlite database file called '+self.config['dbfile'])


    # ---------------------------------------------------------------
    # - Close connection to the sqlite3 database 
    # ---------------------------------------------------------------
    def close(self):
        print('  Close db connection')
        self.con.close()


    # ---------------------------------------------------------------
    # - Different data classes need different approaches to store
    #   the data into the sqlite database. 
    # ---------------------------------------------------------------
    def writedata(self,object):

        if object.objclass == 'BRT':
            self.__writedata_BRT__(object.data)
        elif object.objclass == 'BLB':
            self.__writedata_BLB__(object.data)
        elif object.objclass == 'MET':
            self.__writedata_MET__(object.data)
        else:
            utils.exit('No method database.writedata defined for '+object.objclass)

    # ---------------------------------------------------------------
    # - Check if a table exists or not. Returns True or False.
    # ---------------------------------------------------------------
    def __does_table_exist__(self,name):

        sql = 'SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\''+name+'\';'
        cur = self.con.cursor()
        cur.execute(sql)

        res = cur.fetchone()
        if res == None:
            return False
        else:
            return True


    # ---------------------------------------------------------------
    # - Write MET data to sqlite database
    # ---------------------------------------------------------------
    def __writedata_MET__(self, data, tablename='MET'):

        # - does the table exist?
        if not self.__does_table_exist__(tablename):
            # - Create table. We need:
            #   timestamp (integer) + variable_name (char)
            #   value (float)
            #   unique key is on timestamp+sensor_name
            print('  Create new table called '+tablename)
            str_list = []
            str_list.append('CREATE TABLE '+tablename+' (\n')
            str_list.append('  timestamp INTEGER NOT NULL,\n')
            str_list.append('  variable CHARACTER NOT NULL,\n')
            str_list.append('  value REAL NOT NULL,\n')
            str_list.append('  PRIMARY KEY (timestamp,variable)\n')
            str_list.append(');')
            sql = utils.EMPTYSTRING.join(str_list)
            cur = self.con.cursor()
            print("----------------------------")
            print("SQL: "+sql)
            print("----------------------------")
            cur.execute(sql);
        #print('  Write data to '+tablename)

        # - Put everything into the database
        sql = 'REPLACE INTO '+tablename+' (timestamp, variable, value) VALUES (?,?,?);'
        cur = self.con.cursor()
        cur.executemany(sql,data)
        self.con.commit()
        print('MET data written: %d lines to %s table' % (len(data),tablename))


    # ---------------------------------------------------------------
    # - Write BRT data to sqlite database
    # ---------------------------------------------------------------
    def __writedata_BRT__(self,data,tablename='BRT'):

        # - does the table exist?
        if not self.__does_table_exist__(tablename):
            # - Create table. We need:
            #   timestamp (integer) + variable_name (char)
            #   value (float)
            #   unique key is on timestamp+sensor_name
            print('  Create new table called '+tablename)
            str_list = []
            str_list.append('CREATE TABLE '+tablename+' (\n')
            str_list.append('  timestamp INTEGER NOT NULL,\n')
            str_list.append('  frequence REAL NOT NULL,\n')
            str_list.append('  value REAL NOT NULL,\n')
            str_list.append('  PRIMARY KEY (timestamp,frequence)\n')
            str_list.append(');')
            sql = utils.EMPTYSTRING.join(str_list)
            cur = self.con.cursor()
            print("----------------------------")
            print("SQL: "+sql)
            print("----------------------------")
            cur.execute(sql);
        #print('  Write data to database ' + tablename)

        # - Put everything into the database
        sql = 'REPLACE INTO '+tablename+' (timestamp, frequence, value) VALUES (?,?,?);'
        cur = self.con.cursor()
        cur.executemany(sql,data)
        self.con.commit()
        #print('  data written: %d lines to %s table' % (len(data),tablename))


    # ---------------------------------------------------------------
    # - Write BLB data to sqlite database
    # ---------------------------------------------------------------
    def __writedata_BLB__(self,data,tablename='BLB'):

        # - does the table exist?
        if not self.__does_table_exist__(tablename):
            # - Create table. We need:
            #   timestamp (integer) + variable_name (char)
            #   value (float)
            #   unique key is on timestamp+sensor_name
            print('  Create new table called '+tablename)
            str_list = []
            str_list.append('CREATE TABLE '+tablename+' (\n')
            str_list.append('  timestamp INTEGER NOT NULL,\n')
            str_list.append('  frequence REAL NOT NULL,\n')
            str_list.append('  angle REAL NOT NULL,\n')
            str_list.append('  value REAL NOT NULL,\n')
            str_list.append('  PRIMARY KEY (timestamp,frequence,angle)\n')
            str_list.append(');')
            sql = utils.EMPTYSTRING.join(str_list)
            cur = self.con.cursor()
            print("----------------------------")
            print(sql)
            print("----------------------------")
            cur.execute(sql);
        #print('  Write data to database '+tablename)

        # - Put everything into the database
        sql = 'REPLACE INTO '+tablename+' (timestamp, frequence, angle, value) VALUES (?,?,?,?);'
        cur = self.con.cursor()
        cur.executemany(sql,data)
        self.con.commit()
        #print('  BLB data written: %d lines to table %s' % (len(data),tablename))

    ## SZABO ##
    def create_avg_table(self, tablename, nrdatacolumns):
        str_list = []
        str_list.append('CREATE TABLE IF NOT EXISTS '+tablename+' (\n')
        str_list.append('  timestamp INTEGER NOT NULL,\n')
        for i in range(nrdatacolumns):
            str_list.append('  value{0} REAL,\n'.format(i))
        str_list.append('  PRIMARY KEY (timestamp)\n')
        str_list.append(');')
        sql = utils.EMPTYSTRING.join(str_list)
        cur = self.con.cursor()
        #print("----------------------------")
        #print(sql)
        #print("----------------------------")
        cur.execute(sql)
    
    ## SZABO ##
    def get_minmax_utc(self, tablename, minormax):
        sql = 'select {1}(timestamp) from {0};'.format(tablename, minormax)
        cur = self.con.cursor()
        #print(sql)
        cur.execute(sql)
        res = cur.fetchone()        
        #print(type(res[0]))
        return int(res[0])
    
    ## SZABO ##
    def get_avg_data(self, utc, tablename):
        values = []
        sql = 'select avg(value) from {2} where timestamp > {0} and timestamp <= ({1}) group by altitude;'.format(utc, utc+600, tablename)
        cur = self.con.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        values.append(utc+600)
        for val in res:
            values.append(val[0])
        return tuple(values)

    ## SZABO ##
    def insert_avg_data(self, tablename, data):
        cur = self.con.cursor()
        str_list = []
        sql = 'INSERT OR REPLACE INTO {0} VALUES ('
        for i in range(40):
            str_list.append('?')
        sql = sql + ','.join(str_list) + ')'
        sql = sql.format(tablename)
        #print(sql)
        cur.executemany(sql, data)
        self.con.commit()

    # ---------------------------------------------------------------
    # - Write the results into the database
    # ---------------------------------------------------------------
    def write_RESULT_to_db(self,data,tablename):

        # - does the table exist?
        if not self.__does_table_exist__(tablename):
            # - Create table. We need:
            #   timestamp (integer) + variable_name (char)
            #   value (float)
            #   unique key is on timestamp+sensor_name
            print('  Create new table called '+tablename)
            str_list = []
            str_list.append('CREATE TABLE '+tablename+' (\n')
            str_list.append('  timestamp INTEGER NOT NULL,\n')
            str_list.append('  altitude INTEGER NOT NULL,\n')
            str_list.append('  value REAL NOT NULL,\n')
            str_list.append('  PRIMARY KEY (timestamp,altitude)\n')
            str_list.append(');')
            sql = utils.EMPTYSTRING.join(str_list)
            cur = self.con.cursor()
            print("----------------------------")
            print(sql)
            print("----------------------------")
            cur.execute(sql);
        #print('  Write data to '+tablename)

        # - Put everything into the database
        sql = 'REPLACE INTO '+tablename+' (timestamp, altitude, value) VALUES (?,?,?);'
        cur = self.con.cursor()
        cur.executemany(sql,data)
        self.con.commit()
        #print('  data written: %d lines to %s table' % (len(data),tablename))



    # ---------------------------------------------------------------
    # - Getting minimum and maximum of overlapping time stamps.
    #   Something like this:
    #   Table:       MET    BLB    BRT
    #                 -    xxxxx    -  
    #               xxxxx  xxxxx    -  
    #               xxxxx  xxxxx  xxxxx   <- getting this as min
    #               xxxxx  xxxxx  xxxxx
    #               xxxxx  xxxxx  xxxxx
    #               xxxxx  xxxxx  xxxxx   <- getting this as max
    #               xxxxx  xxxxx    -  
    # ---------------------------------------------------------------
    def get_overlapping_timestamps(self,tables):

        # tables: ['MET', 'BLB'...]
        # look in all tables for min and max timestamp, then again look for
        #  min and max of those

        minimum = []
        maximum = []
        cur = self.con.cursor()
        for table in tables:
            sql = 'SELECT min(timestamp) as min, max(timestamp) as max ' + \
                  'FROM \''+table+'\';' 
            cur.execute(sql)
            res = cur.fetchone()
            minimum.append( res[0] ); maximum.append( res[1] )

        tfmt = '%Y-%m-%d %H:%M:%S'
        print('  Overlapping time periode:')
        print('  Minimum: '+dt.fromtimestamp(min(minimum)).strftime(tfmt))
        print('  Maximum: '+dt.fromtimestamp(max(maximum)).strftime(tfmt))

        return min(minimum), max(maximum)


    # ---------------------------------------------------------------
    # - Do the averaging for all different data in the database.
    #   Based on the periods (input) and the PRIMARY KEY of the table.
    # ---------------------------------------------------------------
    def do_averaging(self,tables):

        # - Getting "minimum of the maximum timestamp" of the three
        #   tables:
        timestamp_min,timestamp_max = self.get_overlapping_timestamps(tables)

        # Loading periods do average over
        periods = self.get_time_periods_to_average(config['averaging'],timestamp_min,timestamp_max)	

        # - basic sql command templates
        sqltemplate = {
            'MET':'SELECT MAX(timestamp), variable, AVG(value) FROM MET WHERE '+ \
                  'timestamp > %d AND timestamp <= %d GROUP BY variable',
            'BRT':'SELECT MAX(timestamp), frequence, AVG(value) FROM BRT WHERE '+ \
                  'timestamp > %d AND timestamp <= %d GROUP BY frequence',
            'BLB':'SELECT MAX(timestamp), frequence, angle, AVG(value) FROM BLB WHERE '+ \
                  'timestamp > %d AND timestamp <= %d GROUP BY frequence, angle'}

        # - Outer loop is over periods.
        for period in periods:
            # - Inner loop over tables.
            for table in tables:
                if not self.__does_table_exist__(table):
                    utils.exit('sorry, cannot average table '+table+'. Does not exist!')
                elif not table in sqltemplate:
                    utils.exit('sorry, sqltemplate for averaging missing for table '+table)

                # - Create sql command
                sql = sqltemplate[table] % period

                # - Getting data
                cur = self.con.cursor()
                cur.execute(sql)
                res = cur.fetchall()

                # - Setting timestamp (first element) to the
                #   end of the period.
        	#   Sometimes, the max(timestamp) is < higher end of period. -> replace
                data = []
                for i in range(len(res)):
                    tmp = [period[1]]
                    for elem in range(1,len(res[i])):
                        tmp.append(res[i][elem])
                    data.append( tuple(tmp) ) 
                #print(res == data)

                if table == 'MET':
                    self.__writedata_MET__(data,'MET_avg')
                elif table == 'BLB':
                    self.__writedata_BLB__(data,'BLB_avg')
                elif table == 'BRT':
                    self.__writedata_BRT__(data,'BRT_avg')
                



    # ---------------------------------------------------------------
    # - Loading averaged data for a given range of periods (always
    #   for the end of the period! Return a list. 
    # ---------------------------------------------------------------
    def get_averaged_data(self,timestamp,table):

        if not table in ['MET','BLB','BRT']:
            utils.exit('Sorry, not defined yet.')

        #timestamp_min = periods[0][0]
        #timestamp_max = periods[0][1]
        #for period in periods:
        #    timestamp_min = min(timestamp_min,period[0])
        #    timestamp_max = max(timestamp_max,period[0])
        timestamp_min = min(timestamp)
        timestamp_max = max(timestamp)

        ### - Create sql syntax
        ##sql = 'SELECT * FROM '+table+'_avg WHERE timestamp='
        ##str_list = []
        ##for p in range(len(periods)):
        ##    str_list.append( str(int(periods[p][1])) )
        ##sql += ' OR timestamp='.join(str_list)
        if timestamp_min == timestamp_max:
            sql = 'SELECT * FROM '+table+'_avg WHERE timestamp = %d' % (timestamp_min)
        else:
            sql = 'SELECT * FROM '+table+'_avg WHERE timestamp >= %d AND timestamp <= %d' % (timestamp_min,timestamp_max)
        cur = self.con.cursor()
        cur.execute(sql)

        return cur.fetchall()

    def get_brightness_temp(self,table):

        sql = 'SELECT * FROM '+table
        cur = self.con.cursor()
        cur.execute(sql)

        return cur.fetchall()

    def get_data_for_specific_timespan(self,table,t_min,t_max):

        sql = 'SELECT * FROM '+table+' WHERE timestamp >= %d AND timestamp <= %d' % (t_min,t_max)
        cur = self.con.cursor()
        cur.execute(sql)

        return cur.fetchall()

    def write_down_all_timestamps(self, tables):

        tfmt = '%Y-%m-%d %H:%M:%S'
        for table in tables:
            sql = 'SELECT timestamp FROM '+table
            cur = self.con.cursor()
            cur.execute(sql)
            res_sql = cur.fetchall()
            # timestamps_unix: 'number' and ','
            print('All timestamps in %s: ' % (table))
            print([dt.fromtimestamp(tuple_time[0]).strftime(tfmt) for tuple_time in res_sql[0:1000]])


    def get_time_periods_to_average(minutes,timestamp_min,timestamp_max):
    
        periods = []
    
        # - Time sequence (periode duration) in seconds
        time_sequence = float(minutes)*60.
    
        # - Compute start and end point for propper periods of this length
        #   math.ceil: round up to next integer
        #   math.floor: round down to last integer
        begin = math.ceil( float(timestamp_min)/time_sequence)*time_sequence
        end   = math.floor(float(timestamp_max)/time_sequence)*time_sequence
    
        # - If they are equal, we cannot do any averaging
        if begin == end:
            exit('Overlapping periode does not contain any periods ' + \
                       'of length '+str(int(minutes))+'minutes. Stop.')
    
        # - Create entries into the periods list
        #   periods: list of always to entries
        while begin < end:
            periods.append( (begin,begin+time_sequence) )
            begin = begin + time_sequence
    
        # - Visual
        print('  Found %d propper periods overspanning %d minutes' % (len(periods),minutes))
        tfmt = '%Y-%m-%d %H:%M:%S'
        for period in periods:
            print('  - From %s to %s' % ( dt.fromtimestamp(period[0]).strftime(tfmt), \
                                          dt.fromtimestamp(period[1]).strftime(tfmt) ))
    
    
        return periods

