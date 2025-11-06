#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:35:49 2017

@author: lukas
"""
from __future__ import division
import sys
from matplotlib import pyplot as plt

import pandas as pd
import math


## aufruf ind er main: calculate_pottemp(df_t, diff_z, p0, T, temp_data)
def calculate_pottemp(df, diff_z, p0, T0, T):
    #this function has to be filled with temperature profiles of hatpro and the same amount of 
    # p0 (non-reduced pressure) and T0 measured by TAWES
    pz=p0 #list with i rows    
    pzz = pd.DataFrame([])
    for i in range(0, len(T0)): # loop through all datasets / timesteps
        # loop through all height levels and calculate pressure in the next level
        for n in range(1,len(df.columns)): # loop through all height levels
            pz[i].append(pz[i][n-1]*math.exp((-9.81*diff_z[n-1])/(287*T0[i])))

        pz_tmp = pd.DataFrame(pz[i], columns=[T.index[i]], index=T.columns)        
        pz_tmp = pz_tmp.T

        #pzz = pzz.append(pz_tmp) #deprecated
        pzz = pd.concat([pzz, pz_tmp])
        #pzz.to_csv(f"gohm_testdatend/pot_druck_20230708.csv")

        #pz_tmp = pd.DataFrame(pz, columns=[T.index[i]], index=df_t.columns)
        #pzz=pzz.append(pz_tmp)

    # predefine dataframe where multiple theta profiles are stored in. rows are time series, columns are levels    
    theta = pd.DataFrame() 
    for i in range(0, len(T)): ##ORIG
        ## 200_archiv.csv ->
        ## read_hatpro(settings_url['filename_hatpro_temp_archive']) ->
        ## pd.concat([df_empty, df_t], axis=1).reindex(df_empty.index) -> 
        ## df_t.iloc[:,:] -> 
        ## temp_data ->
        ## T

        ## read_hatpro_ws(settings_url['filename_hatpro_weatherstation_archive']) ->
        ## df_ws = pd.concat([df_empty, df_ws], axis=1).reindex(df_empty.index) ->
        ## df_ws.ps.values ->
        ## pp = np.concatenate([[np.NAN],pp,[np.NAN]]) ->
        ## [ [pp[n]] for n in range(len(pp))] ->
        ## p0 ->
        ## pz

        #print(i)
        temp_list = [] #SABO

        """
        Traceback (most recent call last):
        File "/home/c7071039/sabo_projects/P3_hatpro_visualisation/main.py", line 238, in <module>
            theta, p, pzz =calculate_pottemp(df_t, diff_z, p0, T, temp_data) 
        File "/home/c7071039/sabo_projects/P3_hatpro_visualisation/pot_temperature.py", line 40, in calculate_pottemp
            for n in range(0, len(pz[i])): #SABO
        IndexError: list index out of range
        """

        for n in range(0, len(pz[i])): #SABO
            temp_list.append(T.iloc[i].iloc[n]*(1000/pz[i][n])**(287/1005)) #SABO

        #theta_tmp=pd.DataFrame([ T.iloc[i][n]*(1000/pz[i][n])**(287/1005) 
        #            for n in range(0,len(pz[i])) ], columns=[T.index[i]], index=T.columns) #ORIG
        theta_tmp = pd.DataFrame(temp_list, columns=[T.index[i]], index=T.columns) #SABO

        theta_tmp=theta_tmp.T
        #theta_tmp.set_index([i])
        #theta=theta.append(theta_tmp) #deprecated
        theta = pd.concat([theta, theta_tmp])
        #theta.to_csv(f"gohm_testdatend/pot_temp_20230708.csv")

    #theta = [ round(j, 2) for j in theta ] # round to two decimals
    return(theta, pz, pzz) # pzz is a pandas dataframe, should replace pz one day