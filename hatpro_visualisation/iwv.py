#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:28:11 2017

@author: lukas
"""
import pandas as pd
import numpy as np
# calculate integrated water vapour
def calculate_iwv(df_input, dates,pdvector):
    # returns a dataframe containing the iwv and the timestamp
    # unit: kg m-2
    dff=df_input.ix[:,df_input.columns.isin(dates)==True] # extracts data for chosen data, sorted by date
    iwv_index=df_input.columns[df_input.columns.isin(dates)==True] # extracts DateTime sorted by date
    a=dff.ix[1:].index.tolist() # convert df index to list without first element
    a=[int(i) for i in a]
    b=dff.ix[:-1].index.tolist() # convert df index to list without last element
    b=[int(i) for i in b]
    #height difference
    try:
        diff_z=[a[n] - b[n] for n in range(0, len(a))]
        #mean abs. humidity between two layers
        iwv=[((dff.ix[:,:].values[n] + dff.ix[:,:].values[n+1])/2)*diff_z[n] for n in range(0, len(dff.ix[:,:].values)-1) ]
        iwv_values=sum(iwv)/1000 # unit kg/m²
        iwv=pd.DataFrame(data=iwv_values, index=iwv_index)
    except IndexError:  #raised if `y` is empty.
        pass
        iwv=pd.DataFrame(0, index=pdvector,columns=[0]) # if error -> create dataframe with zeros
        #pd.DataFrame(np.nan, index=[0,1,2,3], columns=['A'])
    float_arr = np.vstack(iwv[0].values).astype(np.float) # convert array of dtype object to float array
    if np.count_nonzero(~np.isnan(float_arr))==0: # if 0, then only nan in array, this happens when file empty
        iwv=pd.DataFrame(0, index=pdvector,columns=[0]) # if error -> create dataframe with zeros
        data_rh=0 # flag for data availability 
    return(iwv)