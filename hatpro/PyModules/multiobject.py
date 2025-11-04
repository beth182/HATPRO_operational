# -------------------------------------------------------------------
# - NAME:        multiobject.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-02-08
# -------------------------------------------------------------------
# - DESCRIPTION: This object takes the different measurements, e.g.
#                temperature profiles, to visualize them at the end.
# -------------------------------------------------------------------
# - EDITORIAL:   2014-02-08, RS: Created file.
# -------------------------------------------------------------------

import sys, os
os.environ['TZ'] = 'UTC'
import numpy as np


from hatpro.PyModules import utils

from datetime import datetime as dt
from scipy import interpolate as si

import matplotlib.pyplot as plt
import matplotlib.axes as axes
import matplotlib.dates as mdates
# from matplotlib.mlab import griddata
from scipy.interpolate import griddata

class multiobject():

    # keep in mind that in the script "main.py" this class is used with
    # .add({'obj':variable}), variable is retrieved with one of the
    # binary read-in fuctions. therefore they themselves have the classes
    # .config, .header, .maximum, .minimum, .frequencies, .infile, .pathsep
    # .readdata, .profilemeta, .infile...

    def __init__(self):
        self.obj        = None
        self.objclass   = None
        self.time       = ([]) # x-axis
        self.altitude   = ([]) # y-axis
        self.values     = ([]) # to store the profile values
        self.title      = ''   # default title
        self.continuous  = {}   # default object for continuouse obs
        self.data       = []   # used to store data in a format for the sqlite database 

        # - relhum is used for the humidity profile. If relhum
        #   is set to yes, we take relative humidity. Else,
        #   absolute humidity will be used.
        self.relhum = False # self.relhum is only set to yes if input-dict. contains 'True'

    def add(self,object):

        for o in object:
            if o == 'obj':
                self.obj = object[o]
                self.objclass = object[o].__class__.__name__
            elif o == 'relhum':
                self.relhum = object[o]

        if self.objclass == 'TP':
            self.__add_TP_data__()
        elif self.objclass == 'HPC':
            self.__add_HPC_data__()
        elif self.objclass == 'BRT':
            self.__add_BRT_data__()
        elif self.objclass == 'BLB':
            self.__add_BLB_data__()
        elif self.objclass == 'MET':
            self.__add_MET_data__()
        else:
            sys.exit('ERROR! No __add_xxx_data__ method defined!')


    # ---------------------------------------------------------------
    # - add TP data object
    #   The profiles are on self.obj.profile, each column is a
    #   sample. I just take the mean at the moment.
    #   For the plot we need the time, altitude and profile
    #   values as vectors.
    def __add_TP_data__(self):

        # - Take mean time of all samples
        timestamp = 0
        for x in self.obj.profilemeta:
            timestamp = timestamp + x['time']
        timestamp   = utils.timestamp( int(timestamp/len(self.obj.profilemeta)) )
        # - Store the data
        n = len(self.obj.altitudes)
        self.time.extend( list(np.repeat(timestamp,n)) )
        self.altitude.extend( self.obj.altitudes )
        self.values.extend( list(np.mean(self.obj.profile,1)) )


    # ---------------------------------------------------------------
    # - add HPC data object
    #   The profiles are on self.obj.profile, each column is a
    #   sample. I just take the mean at the moment.
    #   For the plot we need the time, altitude and profile
    #   values as vectors.
    def __add_HPC_data__(self):

        # - Relative or absolute humidity?
        if self.relhum:
            profilemeta = self.obj.rh_profilemeta
            profile     = self.obj.rh_profile[:,1:]
        else:
            profilemeta = self.obj.profilemeta
            profile     = self.obj.profile[:,1:]

        # - Take mean time of all samples
        timestamp = 0
        for x in profilemeta:
            timestamp = timestamp + x['time']
        # - Store the data
        timestamp   = utils.timestamp( int(timestamp/len(profilemeta)) )
        n = len(self.obj.altitudes)
        self.values.extend( list(np.mean(profile,1)) )
        self.time.extend( list(np.repeat(timestamp,n)) )
        self.altitude.extend( self.obj.altitudes )


    # ---------------------------------------------------------------
    # - add brightness temperature (BRT) data object
    def __add_BRT_data__(self):

        # - Extracting time stamps for all the measurements
        obs_times = ([])
        for i in range(0,self.obj.header['N']): # self.obj.header['N'] -> # of samples
            # B.profilemeta[x].keys() -> rainflag, elevation, time
            obs_times.extend( [utils.timestamp(self.obj.profilemeta[i]['time'])] )
        # - Append to time variable
        self.time.extend( obs_times )

        # - Create list with tuples for database
        # data: timestamp, frequency, profile
        # loop over frequencies, loop over timestamps
        for f in range(self.obj.header['FreqAnz']):
            for t in range(len(obs_times)):
                self.data.append( (obs_times[t],self.obj.frequencies[f],self.obj.profile[f,t]) )

        # loop over frequencies
        # self.continuous.keys: frequencies
        # self.continuous[key]: self.obj.profile resp B.profile
        for i in range(0,self.obj.header['FreqAnz']): 
            name = self.obj.frequencies[i] #'freq_'+str(i)

            if not name in self.continuous.keys():
                self.continuous[name] = list(self.obj.profile[i,:])
            else:
                self.continuous[name].extend( self.obj.profile[i,:] )

        # - Need them. At least once during the plot 
        self.frequencies = self.obj.frequencies


    # ---------------------------------------------------------------
    # - add brightness temperature (BLB) data object
    def __add_BLB_data__(self):

        # - Extracting time stamps for all the measurements
        obs_times = ([])
        for i in range(0,self.obj.header['N']):
            obs_times.extend( [utils.timestamp(self.obj.datameta[i]['time'])] )
        # - Append to time variable
        self.time.extend( obs_times )
        
        for s in range(self.obj.header['N']):
            for i in range(self.obj.header['FreqAnz']): 
                for a in range(len(self.obj.angles)+1):
                    if (a == len(self.obj.angles)):
                        angle = 0.
                    else:
                        angle = self.obj.angles[a]
                    self.data.append( (obs_times[s],self.obj.frequencies[i],angle,self.obj.data[i,a,s]) )
        
        #for s in range(self.obj.header['N']):
        #    for i in range(0,self.obj.header['FreqAnz']): 
        #        name = 'freq_'+str(i)+'_sample_'+str(s)

        #        if not name in self.continuous.keys():
        #            self.continuous[name] = list(self.obj.data[i,:,s])
        #        else:
        #            self.continuous[name].extend( self.obj.data[i,:,s] )

        # - Need them. At least once during the plot 
        self.frequencies = self.obj.frequencies


    # ---------------------------------------------------------------
    # - add meteorological sensors object 
    def __add_MET_data__(self):

        # - Extracting time stamps for all the measurements
        obs_times = ([])
        # M.profilemeta consists of 'rainflag' and 'time'
        for i in range(0,self.obj.header['N']):
            obs_times.extend( [utils.timestamp(self.obj.profilemeta[i]['time'])] )
        # - Append to time variable
        self.time.extend( obs_times )

        # - Create list with tuples for database
        # M.sensors -> ['PS', 'TS', 'HS', 'ff', 'dd']
        for s in range(self.obj.header['TotalSensorNumber']):
            for t in range(len(obs_times)):
                self.data.append( (obs_times[t],self.obj.sensors[s],self.obj.profile[s,t]) )
        # Also add rainflag
        for rf in self.obj.profilemeta:
            self.data.append((utils.timestamp(rf['time']), 'RF', rf['rainflag']))

        # - Same data, different format
        for i in range(0,self.obj.header['TotalSensorNumber']): 
            name = self.obj.sensors[i]

            if not name in self.continuous.keys():
                self.continuous[name] = list(self.obj.profile[i,:])
            else:
                self.continuous[name].extend( self.obj.profile[i,:] )

        # - Need them. At least once during the plot 
        self.sensors = self.obj.sensors


    # ===============================================================
    # - Main plot handling method. Calls one of the
    #   ploting routines below.
    def plot(self,ax,options):

        # - Take plot options
        for o in options:
            if o == 'title':
                self.title = options[o]

        # - Plot the shit
        if self.objclass == 'TP':
            self.__plot_TP_object__(ax)
        elif self.objclass == 'HPC':
            self.__plot_HPC_object__(ax)
        elif self.objclass == 'BRT':
            self.__plot_BRT_object__(ax)
        elif self.objclass == 'MET':
            self.__plot_MET_object__(ax)
        else:
            print('WARNING: no plotting routine for this object')
        

    def __plot_TP_object__(self,ax):

        X = self.time
        Y = self.altitude
        Z = self.values

        time_from   = int(dt.fromtimestamp(min(X)).date().strftime('%s'))
        time_to     = time_from + 86400 #86400 s = 24h
        ax_time     = np.linspace(time_from,time_to,201)
        ax_altitude = np.linspace(min(Y),max(Y),101)
        
        # Test
        colors = ("#003D67","#004268","#00466A","#004B6C","#00506E","#005570",
                  "#005A73","#005F75","#006477","#00687A","#006D7C","#00727E",
                  "#007681","#007B83","#007F84","#008386","#008788","#008B8A",
                  "#008F8B","#00938D","#00978E","#009B8F","#009F90","#00A291",
                  "#00A692","#00A993","#00AC93","#00AF94","#02B294","#1DB595",
                  "#2BB895","#36BB95","#40BE95","#48C095","#50C295","#57C595",
                  "#5EC795","#65C995","#6CCB95","#72CD94","#78CF94","#7ED194",
                  "#83D393","#89D493","#8ED693","#94D792","#99D892","#9EDA92",
                  "#A3DB91","#A8DC91","#ADDD91","#B1DE90","#B6DE90","#BADF90",
                  "#BFE090","#C3E090","#C7E190","#CBE190","#CFE290","#D3E290",
                  "#D7E291","#DBE391","#DEE392","#E2E392","#E5E393","#E9E394",
                  "#ECE395","#EFE396","#F2E297","#F5E298","#F8E29A","#FBE29B",
                  "#FEE19D","#FFE19E","#FFE0A0","#FFE0A2","#FFDFA3","#FFDFA5",
                  "#FFDEA7","#FFDEA9","#FFDDAC","#FFDCAE","#FFDCB0","#FFDBB2",
                  "#FFDAB5","#FFDAB7","#FFD9B9","#FFD8BC","#FFD8BE","#FFD7C1",
                  "#FFD6C3","#FFD6C6","#FFD5C9","#FFD5CB","#FFD4CE","#FFD3D1",
                  "#FFD3D3","#FFD2D6","#FFD2D9","#FFD1DB")
        
        values = griddata(X,Y,Z,ax_time,ax_altitude,interp='linear')
 
        
        # --------------------------- THE PLOT ------------------------------
        # contour the gridded data, plotting dots at the nonuniform data points.
        #CS =  plt.contour(ax_time,ax_altitude,values,15,linewidths=0.5,colors='k')
        CS = plt.contourf(ax_time,ax_altitude,values,len(colors)-1,colors=colors)
        # -------------------------------------------------------------------
        
        # ------------------------- THE X-AXIS ------------------------------
        # - Ticks to see where we have had measurements
        #fig.gca().set_xticks(X,())
        # - Time ticks
        time_ticks = np.arange(start=time_from,stop=time_to+1,step=3*3600)
        time_labels = []
        for x in time_ticks: time_labels.append(dt.fromtimestamp(x).strftime('%H:%M'))
        ax.get_xaxis().set_tick_params(direction='out')
        ax.set_xticks(time_ticks)
        ax.set_xticklabels(time_labels)
        #ax.set_xlabel( 'Measurements start at: '+dt.fromtimestamp(time_from).strftime('%Y-%m-%d') )
        # -------------------------------------------------------------------
        
        # ------------------------- THE Y-AXIS ------------------------------
        # - Ticks to see where we have had measurements
        # - Time ticks
        alt_ticks = np.arange(start=1000.,stop=10000.+1.,step=1000.)
        alt_labels = alt_ticks/1000.
        ax.get_yaxis().set_tick_params(direction='out')
        ax.set_yticks(alt_ticks)
        ax.set_yticklabels(alt_labels)
        ax.set_ylabel( 'Height [km] above HatPro' )
        # -------------------------------------------------------------------
        
        ax.set_title( self.title + ' ' + dt.fromtimestamp(time_from).strftime('%Y-%m-%d') )
        plt.colorbar()


    def __plot_HPC_object__(self,ax):

        X = self.time
        Y = self.altitude
        Z = self.values

        time_from   = int(dt.fromtimestamp(min(X)).date().strftime('%s'))
        time_to     = time_from + 86400
        ax_time     = np.linspace(time_from,time_to,201)
        ax_altitude = np.linspace(min(Y),max(Y),101)
        
        # Test
        colors = ("#F9F9F9","#F6F8F6","#F3F7F4","#F0F5F1","#EDF4EE","#E9F3EB",
                  "#E6F2E8","#E3F0E6","#E0EFE3","#DDEEE0","#D9ECDD","#D6EBDA",
                  "#D3EAD7","#D0E9D4","#CCE7D1","#C9E6CE","#C6E5CB","#C2E3C9",
                  "#BFE2C6","#BBE0C3","#B8DFC0","#B4DEBD","#B1DCB9","#ADDBB6",
                  "#AAD9B3","#A6D8B0","#A2D7AD","#9ED5AA","#9BD4A7","#97D2A4",
                  "#93D1A0","#8FCF9D","#8BCE9A","#87CC96","#83CB93","#7EC98F",
                  "#7AC88C","#75C688","#71C485","#6CC381","#67C17D","#62BF79",
                  "#5CBE75","#56BC71","#50BA6D","#49B869","#41B664","#38B45F",
                  "#2DB259","#19AF52")

        levels = np.linspace(0,100,len(colors))

        values = griddata(X,Y,Z,ax_time,ax_altitude,interp='linear')
        CS = plt.contourf(ax_time,ax_altitude,values,len(colors)-1,colors=colors)

        x_test = []; y_test = [];
        for i in range(len(ax_time)):
            x_test.append(ax_time[i])
            m = 0
            for x in values:
                m = max(m,x[i])
            y_test.append(m)

        # ------------------------- THE X-AXIS ------------------------------
        # - Time ticks
        time_ticks = np.arange(start=time_from,stop=time_to+1,step=3*3600)
        time_labels = []
        for x in time_ticks: time_labels.append(dt.fromtimestamp(x).strftime('%H:%M'))
        ax.get_xaxis().set_tick_params(direction='out')
        ax.set_xticks(time_ticks)
        ax.set_xticklabels(time_labels)
        #ax.set_xlabel( 'Measurements start at: '+dt.fromtimestamp(time_from).strftime('%Y-%m-%d') )
        # -------------------------------------------------------------------
        
        # ------------------------- THE Y-AXIS ------------------------------
        # - Ticks to see where we have had measurements
        # - Time ticks
        alt_ticks = np.arange(start=1000.,stop=10000.+1.,step=1000.)
        alt_labels = alt_ticks/1000.
        ax.get_yaxis().set_tick_params(direction='out')
        ax.set_yticks(alt_ticks)
        ax.set_yticklabels(alt_labels)
        ax.set_ylabel( 'Height [km] above HatPro' )
        # -------------------------------------------------------------------
        
        ax.set_title( self.title + ' ' + dt.fromtimestamp(time_from).strftime('%Y-%m-%d') )
        plt.colorbar()



    # ---------------------------------------------------------------
    # - Plotting BRT (brightness temperature) object
    # ---------------------------------------------------------------
    def __plot_BRT_object__(self,plt):

        time_from   = int(dt.fromtimestamp(min(self.time)).date().strftime('%s'))
        time_to     = time_from + 86400
        time_ticks = np.arange(start=time_from,stop=time_to+1,step=3*3600)
        time_labels = []
        for x in time_ticks: time_labels.append(dt.fromtimestamp(x).strftime('%H:%M'))

        for i in range(0,len(self.frequencies)):

            # - Next subplot
            ax = plt.subplot(7,2,i+1)

            # - To know where we are
            col = int(i)/7 + 1
            if col == 1:
                row = i+1
            else:
                row = i-7+1

            freq = self.frequencies[i]
            ax.plot(self.time,self.continuous['freq_'+str(i)])

            ax.get_xaxis().set_tick_params(direction='out')
            ax.set_xticks(time_ticks)
            if i >= 12: 
                ax.set_xticklabels(time_labels)
            else:
                ax.set_xticklabels([])

            if i == 0:
                ax.set_title( self.title )
            elif i == 1:
                ax.set_title( dt.fromtimestamp(time_from).strftime('%Y-%m-%d') )


            string = 'Freq: '+str(round(freq,2)),' GHz'
            ax.text(time_to,min(self.continuous['freq_'+str(i)]), \
                    string,horizontalalignment='right',verticalalignment='bottom')


        plt.subplots_adjust(hspace=0)


    # ---------------------------------------------------------------
    # - Plotting MET (meteorological sensors) object 
    # ---------------------------------------------------------------
    def __plot_MET_object__(self,plt):

        time_from   = int(dt.fromtimestamp(min(self.time)).date().strftime('%s'))
        time_to     = time_from + 86400
        time_ticks = np.arange(start=time_from,stop=time_to+1,step=3*3600)
        time_labels = []

        for x in time_ticks: time_labels.append(dt.fromtimestamp(x).strftime('%H:%M'))

        for i in range(0,len(self.sensors)):

            # - Next subplot
            ax = plt.subplot(3,2,i+1)

            # - To know where we are
            col = int(i)/3 + 1
            if col == 1:
                row = i+1
            else:
                row = i-7+1

            sensor = self.sensors[i]
            ax.plot(self.time,self.continuous['sensor_'+str(i)])

            ax.get_xaxis().set_tick_params(direction='out')
            ax.set_xticks(time_ticks)
            if i >= 12: 
                ax.set_xticklabels(time_labels)
            else:
                ax.set_xticklabels([])

            if i == 0:
                ax.set_title( self.title )
            elif i == 1:
                ax.set_title( dt.fromtimestamp(time_from).strftime('%Y-%m-%d') )


            string = sensor
            ax.text(time_to,min(self.continuous['sensor_'+str(i)]), \
                    string,horizontalalignment='right',verticalalignment='bottom')


        plt.subplots_adjust(hspace=0)


























