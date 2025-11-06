#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 21:45:07 2017

@author: lukas
"""
import pandas as pd
from settings_url import SETTINGS as settings_url

def pottemp_color_boundaries(rh):
    # read in the theta-colorbar limits that were calculated on basis of the climate in tyrol
    theta_boundaries=pd.read_csv(settings_url['theta_colors'], index_col=0)
    datevecc=rh.index[-1]
    dayofyear=datevecc.dayofyear
    #print(dayofyear)
    boundaries=theta_boundaries.loc[dayofyear-1] # -1 as indexing in python starts at 0
    return(boundaries)