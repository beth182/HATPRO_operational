#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:01:35 2017

@author: lukas
"""

## Config file
SETTINGS={
    "processing":{
            "sybase_availability": 90, # percentage of sybase data that has to be available to set the availability flag to 1
            "time_delta": 10, # minutes between two timesteps of the visualisation. Default is 10, sybase data has 10min interval, hatpro usually as well.
            "moving_average_window":5, #3: 30min moving average, 5: 50min moving average if changing this parameter, refresh the footer annotation in plot.py
            "heightbias":0, # absolute bias in meters between HATPRO sea level hight and used (university) weather station. As pressure is measured at the level of HATPRO (rooftop 9th floor), it is currently set to 0
            "rainflag_colname": "rf", # rain flag column name in weatherstation data
            "rainflag_threshold": 100 # seconds within a 10min, 600 seconds window. events with more than x seconds of rain will be removed
            },
    "figures":{
        "bgcolor": "#000014", # dark gray, nearly black, original 000014
        "precipitation_color":"#B2DFEE",
        "figsize":[19.2, 10.8],
        "dpi": 100,
        "fontcolor":"#d9d9d9", # nearly white
        "edgecolor":"#d9d9d9", # nearly white
        "axisfontsize": 14,
        "tickfontsize": 15,
        "labelfontsize":16,
        "ylim":[0, 1.5],
        "nancolor":"#CCCCCC",
        "ylim_upper":4, # upper height level in kilometers
        'relhumlower':10, # color limit lower
        'relhumupper':100, # color limit upper
        'instrument_height_msl':612,
        "pottemp_colors": ["#0086E1","#008AE1","#008EE0","#1B92E0","#3996E0","#4B9BE0","#5A9FE0","#67A3E0","#73A8E0","#7EACE1","#88B1E1","#92B5E1","#9CBAE1","#A5BEE1","#AEC3E1","#B7C8E1","#C0CDE1","#C9D2E0","#D1D7E0","#DBDDE0","#E0DBDC","#E2D3D4","#E3CCCD","#E4C4C6","#E5BDBF","#E5B6B9","#E5AFB2","#E5A7AC","#E5A0A5","#E4999F","#E49298","#E38B92","#E2848C","#E17D85","#DF767F","#DE6F79","#DC6772","#DA606C","#D85965","#D6515F"],
        "rh_colors" : ["#FFFDE6","#FFF9E0","#FFF1D4","#FEE7C3", "#F6DBB0", "#ECCE99", "#E1BE7E","#DAAC6D","#CDAB63","#C0AA5B","#B2A855","#A4A651","#95A34F","#85A04E","#749C4F","#629850","#4C9352","#2D8A50"], # orig "#E7AD78","#DAAC6D","#CDAB63","#C0AA5B","#B2A855","#A4A651","#95A34F","#85A04E","#749C4F","#629850","#4C9352","#2D8A50"
        }
}
