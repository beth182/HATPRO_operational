#!/usr/bin/env python
from __future__ import division
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
#matplotlib.use('Qt5Agg')

import sys
import code
# import modules /subfunctions:
from read_sybase import create_df_from_TAWES_file, read as read_sybase
from read_hatpro import read_data as read_hatpro
from read_hatpro import read_hatpro_ws
from iwv import calculate_iwv as calculate_iwv
from pot_temperature import calculate_pottemp as calculate_pottemp
from plot import plot_screen as plot_screen
from pot_temperature_colors import pottemp_color_boundaries as pottemp_color_boundaries
from settings import SETTINGS as settings
from settings_url import SETTINGS as settings_url
#read_data("hatpro_t.csv","/media/lukas/Volume/CloudStation/hatpro/data/") # has to end wkith a backslash
rf_name=settings['processing']['rainflag_colname'] #rainflag column-name, usually "rf"
#######################################
# Predefine start and end of image, put that in a bash script later
####
# read out the arguments that were transfered with the python command "main_2.py"
try:
    start=sys.argv[1]+" "+sys.argv[2]
    end=sys.argv[3]+" "+sys.argv[4]
    archive=sys.argv[5] # boolean 0 or 1
except: # if nothing declared before (in script.sh)
    pass
    start='20231105 12:00'
    end='20231106 15:00'
    archive='1'

starttime=datetime.strptime(start, "%Y%m%d %H:%M")
endtime=datetime.strptime(end, "%Y%m%d %H:%M")

print('Starttime: '+str(starttime))
print('Endtime: '+ str(endtime))
delta=settings['processing']['time_delta'] #minutes - should be x*10 for all x= [1,2,3,...] as sybase data are available at an interval of 10 minutes

# create regular time-grid (vector) 
endtime+= timedelta(minutes=delta)
#endtime+= timedelta(minutes=delta)
#endtime+= timedelta(minutes=delta)# add once again because delta minutes are subtracted afterwards as it is a 10min average and data has to be plotted at hour-delta to get the right pixel colored
vector = np.arange(starttime, endtime, timedelta(minutes=delta)) # vector for chosen interval, as np.array is a half open interval starting at starttime but not includes the original endtime -> endtime+delta, so that endtime is the last timestep

pdvector = pd.to_datetime(vector) # convert generated vector with mean-intervals into pandas array

#print('pdvector für empty df concating:', pdvector)
                                            
#######################################
# read SYBASE and HATPRO data
####   
#if archive > '0': #if archive=1 then only day in filename
#    sybase_path = settings_url['sybase_path_archive']
#else:
#    sybase_path = settings_url['sybase_path_operational']

#try:

#sybase_df, data_flag_sybase = read_sybase(sybase_path)
#tawes_path = settings_url['tawes_path']
#print('tawes_path:', tawes_path)
#sybase_df, data_flag_sybase = create_df_from_TAWES_file(starttime, tawes_path)
#print(sybase_df)


# predefine empty dataframe that no error is produced even if data not available
df_rh = pd.DataFrame(index=pdvector) # create empty dataframe with regular index-grid
df_rh[0] = np.nan
df_t = pd.DataFrame(index=pdvector) # create empty dataframe with regular index-grid
df_t[0] = np.nan
df_ws = pd.DataFrame(index=pdvector) # create empty dataframe with regular index-grid
df_ws[0] = np.nan
df_rainflag = pd.DataFrame(index=pdvector) # create empty dataframe with regular index-grid
df_rainflag[0] = np.nan

try:
    if archive > '0': #if archive=1 then only day in filename
        levels_t, df_t = read_hatpro(settings_url['filename_hatpro_temp_archive'])
    else:
        levels_t, df_t = read_hatpro(settings_url['filename_hatpro_temp_operational'])
except Exception as e:
    print(e, sys.exc_info())
    pass

try:
    if archive > '0': #if archive=1 then only day in filename
        levels_rh, df_rh = read_hatpro(settings_url['filename_hatpro_humidity_archive'])
    else:
        levels_rh, df_rh = read_hatpro(settings_url['filename_hatpro_humidity_operational'])
except:
    print(e, sys.exc_info())
    pass

# read weather station data of hatpro
rf_flag=1
try:
    if archive > '0': #if archive=1 then only day in filename
        df_ws=read_hatpro_ws(settings_url['filename_hatpro_weatherstation_archive'])
        df_rainflag = df_ws[rf_name]
        #print('df_ws', df_ws)
    else:
        df_ws=read_hatpro_ws(settings_url['filename_hatpro_weatherstation_operational'])
        df_rainflag = df_ws[rf_name]
except:
    rf_flag = 0 # no rain flag data available
    pass
#choose only rainflag:
#######################################
#fill hatpro and sybase data into the regular-time grid
####
df_empty = pd.DataFrame(index=pdvector) # create empty dataframe with regular index-grid
#print('df_empty.index[0]',df_empty.index[0])

#https://stackoverflow.com/questions/27391081/concatenating-pandas-and-join-axes
df_t = pd.concat([df_empty, df_t], axis=1).reindex(df_empty.index) # take df_empty with regular grid spacing and sort the data into that structure
df_rh = pd.concat([df_empty, df_rh], axis=1).reindex(df_empty.index)
df_rainflag = pd.concat([df_empty, df_rainflag], axis=1).reindex(df_empty.index)
df_ws = pd.concat([df_empty, df_ws], axis=1).reindex(df_empty.index)

"""
with pd.option_context('display.max_rows', 150,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
    print('df_ws', df_ws)
    print('df_rainflag',df_rainflag)
"""

if not df_ws.empty:
    data_flag_ws = 1

if data_flag_ws > 0: #if something available
    # take df_empty with regular grid spacing and sort the data into that structure
    #df_sybase = pd.concat([df_empty, sybase_df], axis=1).reindex(df_empty.index)

    # quantifying sybase availability
    # sum of periods where pressure values are not available
    availability = (1-df_ws.ps.isnull().sum()/len(df_ws))*100
    print(f'\npercentage of available data within the sybase: {availability}') #percentage of available data within the sybase

    #print('df_sybase')
    #print(df_sybase)

    if availability >= settings['processing']['sybase_availability']: 
        data_flag_ws=1
    else:
        data_flag_ws=0

# check availability of data in imported files. 
# If only nan are in the matrix, a flag is set to help in further calculations
float_arr = np.vstack(df_rh.values).astype(float) # convert array of dtype object to float array

# HUMIDITY
# if 0, then only nan in array, this happens when file empty
if np.count_nonzero(~np.isnan(float_arr)) == 0: 
    print('Datafile Relative Humidity empty')
    data_rh=0 # flag for data availability: mising
else:
    data_rh=1 # flag for data availability: at least some data is available

# TEMPERATURE
float_arr = np.vstack(df_t.values).astype(float) # convert array of dtype object to float array
if np.count_nonzero(~np.isnan(float_arr))==0: # if 0, then only nan in array, this happens when file empty
    print('Datafile Temperature empty')
    data_t=0 # flag for data availability: missing
else:
    data_t=1 # flag for data availability: at least some data is available

# set NAN where rain threshold exceeded
rf_boolean = df_rainflag > settings['processing']['rainflag_threshold'] # seconds within 600 seconds, a 10min window
df_rainflag_norm = df_rainflag/600 # normalize threhold
if rf_flag>0 and data_t>0: # if rainflag data available
    df_t[rf_boolean[rf_name]==True]=9999
    
#######################################
# calculate integrated water vapour - not used currently
####
dfd=df_rh.T #Table of RH: timestamps as column names, rows are the levels.
dates=dfd.columns # the whole dataframe
#if(data_rh>0): # only calculate potential temperature if sybase data available
    #try: # for the cases where humidity not available
        #iwv=calculate_iwv(dfd, dates, pdvector)
    #except (IndexError, ValueError):  #raised if `y` is empty.
        #pass
        ##iwv=pd.DataFrame(index=pdvector)
    
#######################################
# calculate potential temperature
####
# start by calculating pressure in the atmosphere depending on the surface pressure and temperature in Kelvin
if(data_rh>0): # only calculate potential temperature if sybase data available
    df=df_rh
else:
    df=df_t #only for determination of difference between height levels

a=df.columns[1:].tolist() # convert df index to list without first element
a=[int(i) for i in a]
#print('a',a)
b=df.columns[:-1].tolist() # convert df index to list without last element
b=[int(i) for i in b]

#height difference

diff_z=[a[n] - b[n] for n in range(0, len(a))]
#print('diff_z', diff_z)
offset=settings['processing']['heightbias'] # offset of meters between the sea level of the hatpro and sea level of university weatherstation pressure sensor
if not not diff_z: # if not not empty, if contains sth.
    diff_z[0]+=offset # as the pressure for all levels is caluclated iteratively starting at the bottom, it is good enough to add the offset to the lowest height increment
#code.interact(local=locals())
if(data_flag_ws>0): # only calculate potential temperature if sybase data available
    temp_data=df_t.iloc[:,:]
    # pressure: local pressure (QFE) and not reduced one, temperature in Kelvin

    ## --------------------------------------
    ## ORIG BEGINN
    #pp=df_sybase.P.values
    #p0=[ [pp[n]] for n in range(len(pp))]
    #T = df_sybase.TL.values+273.15
    ## ORIG END
    ## --------------------------------------

    ## --------------------------------------
    ## Using Weatherstation of hatpro becaus Tawes make jumps
    ## 2023.12.04 Gohm try
    #print(df_ws)
    pp = df_ws.ps.values
    ## pp = np.concatenate([[np.NAN],pp,[np.NAN]])
    #print('len(pp)',len(pp), type(pp))
    p0 = [ [pp[n]] for n in range(len(pp))]
    T = df_ws.ts.values
    ## T = np.concatenate([[np.NAN],T,[np.NAN]]) 
    #print('len(T)', len(T))
    ## --------------------------------------
    #print('T',T)
    #print('temp_data', temp_data)
    
    #every 2 hours: df_t.iloc[::12,:] ; # pzz is a pandas dataframe, should replace p one day
    theta, p, pzz =calculate_pottemp(df_t, diff_z, p0, T, temp_data) 
    theta.columns=[float(i)/1000 for i in theta.columns]
    #print(p)

#######################################
# calculate relative humidity
####
t=df_t
rh=np.NaN*t
if data_t>0:
    # with saturation vapour pressure over water not ice!
    rh=df_rh/((611.2 * np.exp((17.62*(t-273.16))/(243.12+(t-273.16))))/(461.52*t)*1000)*100

# convert m to km
rh.columns=[float(i)/1000 for i in rh.columns]
df_t.columns=[float(i)/1000 for i in df_t.columns]
if rf_flag>0 and data_rh>0: # if rainflag data available
    rh[rf_boolean[rf_name]==True]=9999
if rf_flag>0 and data_flag_ws>0 and data_t>0: # if rainflag data available
    theta[rf_boolean[rf_name]==True]=9999

# Pcolormesh has to get one time-index extra at the end of the vector/dataframe. Therefore add to 
# humidity and temperature dataframes one timestep with delta of delta minutes (default: 10)
# added row is copied from the last row, NaN would be possible as well.
#temporary=rh.ix[-1] #deprecated
temporary = rh.iloc[-1:] # SABO [-1:] um einen dataframe wieder zu bekommen
temporary.index = temporary.index + timedelta(minutes=delta)
#rh_neu=rh.append(temporary) #deprecated
rh_neu = pd.concat([rh, temporary])

if(data_flag_ws > 0): # only calculate potential temperature if sybase data available
    #temporary=theta.ix[-1] #deprecated
    temporary=theta.iloc[-1:]
    temporary.index = temporary.index + timedelta(minutes=delta)
    
    #theta_neu=theta.append(temporary) #depricated
    theta_neu=pd.concat([theta, temporary]) #SABO

    theta_neu.index
else:
    theta=np.NaN
    theta_neu=np.NaN

# read in the theta-colorbar limits that were calculated on basis of the climate in tyrol
boundaries = pottemp_color_boundaries(rh)

#print(boundaries) # access by typing: boundaries.lower or boundaries.upper
#######################################
# PLOT SCREEN
####

#print('type(data_t)', type(data_t), 'data_t', data_t)
#print('type(data_rh)', type(data_rh), 'data_rh', data_rh)

#print('theta_neu', theta_neu)
#print('rh_neu', rh_neu)

plot_screen(data_flag_ws, data_t, data_rh, theta, df_t, theta_neu, boundaries, rh, rh_neu, archive, df_rainflag_norm, availability)

