#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime as dt, timedelta
import dateutil
import pytz
import pandas as pd

"""
Created on Tue Mar  7 19:33:56 2017

@author: lukas
"""
def read(pathtofile):
    import pandas as pd
    sybase=pd.read_csv(pathtofile, comment="#", delim_whitespace=True)
    sybase=sybase.set_index(sybase.datumsec.astype('datetime64[s]')) # convert date in seconds since epoch (since Jan 1, 1970) to python datetime
    height=578 # height of weather station 11320 (University), not used currently
    data_sybase = 1
    return (sybase, data_sybase)

"""
@author: Sabo 2023.11.20
"""
def dt_list_with_duration(start_dt):
    #print('start_dt in dt_list_with_duration', start_dt)
    mdtl = []
    nr_rest_days = 2
    
    for i in range(nr_rest_days):
        mdtl.append((start_dt-timedelta(days=i)).strftime('%Y%m%d'))

    mdtl.reverse()
    return mdtl

def create_df_from_TAWES_file(psdt, file_with_path_raw):
    frames = []
    for mdtstr in dt_list_with_duration(psdt):
        with open(file_with_path_raw.replace('YYYYMMDD', mdtstr)) as f:
            #print(f)
            #we want datetime naive df
            frames.append(pd.read_csv(f, index_col='time', parse_dates=True))

    df = pd.concat(frames)
    df.index = df.index.tz_localize(None)
    #print('df.index[0]', df.index[0])

    ## right meint nimm zB 13:01 bis inklusive 13:10
    ## label sagt das man 13:10 dann als zeitstempel nimmt, also den rechts
    means = df.resample('10T', closed='right', label='right').mean()

    ##write df to file for debug
    #means.to_csv(f"gohm_testdatend/tawes_data_{psdt.strftime('%Y%m%d')}.csv")

    ## for debugging TL spikes
    #print(df)
    #print('df.TL.max()', df.TL.max())
    #import matplotlib.pyplot as plt
    #df.TL.plot(label='1 min')
    #means.TL.plot(label='10 min', marker='.')
    #plt.show()   

    return (means, 1)