#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:53:52 2017

@author: lukas
"""
import sys
from matplotlib.dates import DateFormatter, MinuteLocator
import matplotlib.colors as mcl
import numpy as np
from numpy import arange
import numpy.ma as ma
import matplotlib as mpl
import matplotlib.pyplot as plt
from plot_rainflag import create_rain_axis
from settings import SETTINGS as settings
from settings_url import SETTINGS as settings_url
from matplotlib.cbook import get_sample_data
from datetime import timedelta
from matplotlib import lines

def plot_screen(data_sybase, data_t, data_rh, theta, df_t, theta_neu, boundaries, rh, rh_neu, archive, df_rainflag_norm, weather_station_availability):

    window_=settings['processing']['moving_average_window']

    #if data from sybase(pressure) and temp available: plot theta
    if (data_sybase > 0 and data_t > 0): 
        theta_allnan=theta.copy() # only nan for not available data and with rain flag. else: problems with high numbers of 9999
        theta_allnan[theta_allnan==9999]=np.NAN
        maxx=np.max(theta_allnan.max())
        minn=np.min(theta_allnan.min())
        diff=maxx-minn
        interval=2
        numoflines_theta=round(diff/interval, 0)+1
    if(data_rh>0): #if data from sybase(pressure) and temp available: plot theta
        rh_allnan=rh.copy() # only nan for not available data and with rain flag. else: problems with high numbers of 9999
        rh_allnan[rh_allnan==9999]=np.NAN
        
    if(data_t>0): #if data from sybase(pressure) and temp available: plot theta
        df_t_allnan=df_t.copy() # only nan for not available data and with rain flag. else: problems with high numbers of 9999
        df_t_allnan[df_t_allnan==9999]=np.NAN
    # Scale y axis from m to km -> in all dataframes, divide columns by 1000
    fig, (ax1, ax2) = plt.subplots(2, figsize=settings['figures']['figsize'], dpi=settings['figures']['dpi'])
    fig.patch.set_facecolor(settings['figures']['bgcolor'])
    # define colour for contour-area plot, add color for NaN values and mask the NaN values
    #cmap1=plt.cm.viridis_r
    #cmap1=plt.cm.coolwarm
    colors = settings['figures']['pottemp_colors']
    cmm = mcl.ListedColormap(colors) # produce custom colormap for wind speed scale (HCL)
    #cmm.set_bad(settings['figures']['nancolor']) # set the color for all NaN values (former noise, detected through signal to noise ratio), alpha = 0.0 would set the bad region transparent

    if(data_sybase>0 and data_t>0): #if data from sybase(pressure) and temp available: plot theta
        mpl.rcParams['contour.negative_linestyle'] = 'solid' #do not plot negative contour lines dashed
        #cmap1.set_bad(settings['figures']['nancolor']) # set the color for all NaN values (former noise, detected through signal to noise ratio), alpha = 0.0 would set the bad region transparent
        masked_array_av = ma.array (theta_allnan.rolling(window=window_, center=True, min_periods=1).mean().T, mask=np.logical_or(np.isnan(theta_allnan.T),theta_allnan.T==9999))
        masked_array = ma.array (theta.T, mask=np.logical_or(np.isnan(theta.T),theta.T==9999)) #np.logical_or(np.isnan(theta.T),theta.T==9999)
        masked_array_rainflag = ma.array (theta.T, mask=(theta.T==9999)) # invert mask to mark good where nan, or later 9999

        # only for pcolormesh as it needs index+1 to show all data 
        theta_neu.index=theta_neu.index- timedelta(minutes=settings['processing']['time_delta']) 
        
        #old:newindex= theta.index + timedelta(minutes=delta) # pcolormesh requires X and Y to be bigger by one to show last data row/column
        y=theta.columns.tolist() # use the index but transform it to a list to do further calculations in the next line
        y[1:]=y[1:]-(np.diff(y)/2) # y axis shifted by delta/2 to lower y values
        colors = (settings['figures']['nancolor'])
        cmap_rain = mcl.ListedColormap(colors)
        cmap_rain.set_bad(color=settings['figures']['precipitation_color'])


        #print('theta.index',theta.index)
        # add layer where only rain data are plotted blue and all other data gray
        #plot11=ax1.pcolormesh(theta_neu.index, y, masked_array_rainflag, cmap=cmap_rain) #ORIG
        plot11=ax1.pcolormesh(theta.index, y, masked_array_rainflag, cmap=cmap_rain, shading='nearest') #SABO
        
        # add data with transparent gaps where it rained or no data available
        #plot1=ax1.pcolormesh(theta_neu.index, y, masked_array, cmap=cmm, vmin=boundaries.lower, vmax=boundaries.upper) #ORIG
        plot1=ax1.pcolormesh(theta.index, y, masked_array, cmap=cmm, vmin=boundaries.lower, vmax=boundaries.upper, shading='nearest') #SABO

        theta_neu.index=theta_neu.index+ timedelta(minutes=(settings['processing']['time_delta']/2))

        theta.index=theta.index- timedelta(minutes=(settings['processing']['time_delta']/2))
        
        # set rain to nan as moving averages excludes only nan
        plot4=ax1.contour(theta.index, theta.columns, masked_array_av, int(numoflines_theta),colors='w')

        theta_neu.index=theta_neu.index+ timedelta(minutes=(settings['processing']['time_delta']/2)) #minutes=+5
        plt.clabel(plot4, inline=1, fontsize=10, fmt='%1.0f K', colors='w')

    #levelss=np.arange(-100, 100, 2)
    if(data_t>0): # if temp available
        masked_array = ma.array (df_t_allnan.rolling(window=window_, center=True, min_periods=1).mean().T, mask=np.logical_or(np.isnan(df_t.T),df_t.T>1000))
        df_t.index=df_t.index- timedelta(minutes=+settings['processing']['time_delta']/2)
        # plot all contour lines except 0-degree line
        plot3=ax1.contour(df_t.index, df_t.columns, masked_array-273.15, levels=np.append(np.arange(-60, -1, 2), np.arange(2, 60, 2)),colors='#333333',origin='upper')
        # plot zero-degree line
        plot_Null=ax1.contour(df_t.index, df_t.columns,masked_array-273.15,levels = [0],colors=('k',),linestyles=('-',),linewidths=(2,))
        plt.clabel(plot_Null, inline=True, fontsize=13, fmt=u"%1.0f °C")
    
        df_t.index=df_t.index+ timedelta(minutes=+settings['processing']['time_delta']/2)
        plt.clabel(plot3, inline=1, fontsize=11, fmt=u"%1.0f °C")
    ax1.set_ylim([0, settings['figures']['ylim_upper']])
    
    locatormajor = MinuteLocator(arange(0,61,60))
    locatorminor = MinuteLocator(arange(0,61,10))
    locatormajor.MAXTICKS = 4000
    locatorminor.MAXTICKS = 4000
    #plt.setp(ax1.get_xticklabels(), visible=True) 
    ax1.xaxis.set_major_locator( locatormajor ) # tick with label every hour
    ax1.xaxis.set_minor_locator( locatorminor ) # minor tick every half hour
    ax1.xaxis.set_major_formatter( DateFormatter('%H'))
    ax1.tick_params(axis='both', which='major', labelsize=settings['figures']['tickfontsize']) # size for x and y-axis labels

    #ax1.set_axis_bgcolor(settings['figures']['nancolor']) #depricated
    ax1.set_facecolor(settings['figures']['nancolor']) #SABO

    cmap2= mcl.ListedColormap(settings['figures']['rh_colors']) # produce custom colormap for wind speed scale (HCL)
    if(data_rh>0 and data_t>0):
        # define colour for contour-area plot, add color for NaN values and mask the NaN values
        # define the bins and normalize
        #bounds = np.linspace(settings['figures']['relhumlower'], settings['figures']['relhumupper'], 
        #                     (((settings['figures']['relhumupper']-settings['figures']['relhumlower'])/5)+1))
        bounds = np.linspace(settings['figures']['relhumlower'], settings['figures']['relhumupper'], 
                             int((((settings['figures']['relhumupper']-settings['figures']['relhumlower'])/5)+1))) #SABO

        norm = mcl.BoundaryNorm(bounds, cmap2.N)
        #cmap2.set_bad(settings['figures']['nancolor']) # set the color for all NaN values (former noise, 
        # detected through signal to noise ratio), alpha = 0.0 would set the bad region transparent
        masked_array_av = ma.array (rh_allnan.rolling(window=window_, center=True, min_periods=1).mean().T, 
                                    mask=np.logical_or(np.isnan(rh_allnan.T),rh_allnan.T==9999))
        
        masked_array = ma.array (rh.T, mask=np.logical_or(np.isnan(rh.T),rh.T==9999))

        masked_array_rainflag = ma.array (rh.T, mask=(rh.T==9999)) # invert mask to mark good where nan, or later 9999
        
        colors = settings['figures']['nancolor']
        cmap_rain = mcl.ListedColormap(colors)
        cmap_rain.set_bad(color=settings['figures']['precipitation_color'])

        rh_neu.index = rh_neu.index - timedelta(minutes=settings['processing']['time_delta']) # rh_neu and rh are different, why both have to get shifted

        # add layer where only rain data are plotted blue and all other data gray
        y=rh.columns.tolist() # use the index but transform it to a list to do further calculations in the next line
        y[1:] = y[1:] - (np.diff(y)/2) # y axis shifted by delta/2 to lower y values
        
        #print(y)
        #print(rh_neu)

        #ax2.pcolormesh(rh_neu.index, y, masked_array_rainflag, cmap=cmap_rain) #ORIG
        ## pcolormesh([X, Y,] C, **kwargs)
        ## TypeError: Dimensions of C (39, 163) should be one smaller than X(164) and Y(39) while using shading='flat' see help(pcolormesh)
        ## SABO changed from rh_neu to rh as [X,Y]
        ax2.pcolormesh(rh.index, y, masked_array_rainflag, cmap=cmap_rain, shading='nearest') #SABO
        
        #cbaxes1 = fig.add_axes([0.92, 0.52, 0.01, 0.4]) 
        #color_bar1=plt.colorbar(plot1, format='%1i', cax = cbaxes1, ticks=np.arange(0, 20, 2), extend='max')
        ## subtracht 1 interval (10min) to get correct location of color with colormesh
        rh.index=rh.index- timedelta(minutes=settings['processing']['time_delta'])

        #old:newindex= rh.index + timedelta(minutes=delta) # pcolormesh requires X and Y to be bigger by one to show last data row/column


        #ax2.pcolormesh(rh_neu.index, y, masked_array, cmap=cmap2, vmin=settings['figures']['relhumlower'], vmax=settings['figures']['relhumupper']) #ORIG
        ## pcolormesh([X, Y,] C, **kwargs)
        ## TypeError: Dimensions of C (39, 163) should be one smaller than X(164) and Y(39) while using shading='flat' see help(pcolormesh)
        ## SABO changed from rh_neu to rh_neu[1:]
        ax2.pcolormesh(rh_neu.index[1:], y, masked_array, cmap=cmap2, vmin=settings['figures']['relhumlower'], 
                       vmax=settings['figures']['relhumupper'], shading='nearest') #SABO

        rh_neu.index=rh_neu.index+ timedelta(minutes=settings['processing']['time_delta']/2)
        rh.index=rh.index+ timedelta(minutes=settings['processing']['time_delta']/2)

        plot_100=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [100],colors=('k',),linestyles=('-',),linewidths=(2,))
        plot_90=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [90],colors=('k',),linestyles=('-',),linewidths=(2,))
        plot_80=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [80],colors=('k',),linestyles=('-',),linewidths=(1,))
        plot_70=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [70],colors=('k',),linestyles=('-',),linewidths=(1,))
        plot_60=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [60],colors=('k',),linestyles=('--',),linewidths=(1,))
        plot_50=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [50],colors=('k',),linestyles=('--',),linewidths=(1,))
        plot_40=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [40],colors=('k',),linestyles=('--',),linewidths=(1,))
        plot_30=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [30],colors=('k',),linestyles=('--',),linewidths=(1,))
        plot_20=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [20],colors=('k',),linestyles=('--',),linewidths=(1,))
        plot_10=ax2.contour(rh.index, rh.columns,masked_array_av,levels = [10],colors=('k',),linestyles=('--',),linewidths=(1,))
    
        plt.clabel(plot_100, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_90, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_80, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_70, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_60, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_50, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_40, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_30, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_20, inline=1, fontsize=11, fmt='%1.0f %%')
        plt.clabel(plot_10, inline=1, fontsize=11, fmt='%1.0f %%')

        rh_neu.index=rh_neu.index+ timedelta(minutes=settings['processing']['time_delta']/2)
        rh.index=rh.index+ timedelta(minutes=settings['processing']['time_delta']/2)
    #if archive > '0':
    ax2.set_xlim([rh.index[0], rh.index[-1]]) # add 10 minutes to be consistent with the LIDAR where the space at the recent timestamp is needed for the barbs
    ax1.set_xlim([df_t.index[0], df_t.index[-1]])
    #else:    
    #    ax2.set_xlim([rh.index[0], rh.index[-1]+timedelta(minutes=10)]) # add 10 minutes to be consistent with the LIDAR where the space at the recent timestamp is needed for the barbs
    #    ax1.set_xlim([df_t.index[0], df_t.index[-1]+timedelta(minutes=10)])

    ax2.set_ylim([0, settings['figures']['ylim_upper']])
    
    ax1.set_ylabel('Altitude (km AGL)',fontsize=settings['figures']['labelfontsize'], color=settings['figures']['fontcolor'])
    ax2.set_xlabel('Time (UTC)',fontsize=16, color=settings['figures']['fontcolor'])
    ax2.xaxis.set_label_coords(0.5,-0.065) # set the position manually
    ax2.set_ylabel('Altitude (km AGL)',fontsize=settings['figures']['labelfontsize'], color=settings['figures']['fontcolor'])
    if archive > '0':
        ax1.set_title("HATPRO at ACINN, University of Innsbruck (" + str(settings['figures']['instrument_height_msl']) + " m MSL): " +  "{:%d-%b-%Y}".format(df_t.index[0]), color=settings['figures']['fontcolor'],fontsize=19)
    else:
        ax1.set_title("HATPRO at ACINN, University of Innsbruck (612 m MSL): " + "{:%H}".format(df_t.index[0]) + " UTC " + "{:%d-%b-%Y}".format(df_t.index[0]) + " to " + "{:%H}".format(df_t.index[-1]) + " UTC " + "{:%d-%b-%Y}".format(df_t.index[-1]), color=settings['figures']['fontcolor'],fontsize=19)
    
    # create legend axis
    cbaxes1 = fig.add_axes([0.945, 0.54, 0.01, 0.4]) 
    cbaxes1.annotate(r'Potential Temperature (K)', xy=(4.2, 0.45), horizontalalignment='center', verticalalignment='center', xycoords='axes fraction',rotation=90, fontsize=16, color=settings['figures']['fontcolor'])  
    cbaxes2 = fig.add_axes([0.945, 0.07, 0.01, 0.395])
    cbaxes2.annotate(r'Relative Humidity (%)', xy=(4.2, 0.45), horizontalalignment='center', verticalalignment='center', xycoords='axes fraction',rotation=90, fontsize=16, color=settings['figures']['fontcolor'])  
    #color_bar1=plt.colorbar(plot1, cax=cbaxes1, extend='both', ticks=np.arange(260, 312, 5)) # position: http://stackoverflow.com/questions/13310594/positioning-the-colorbar #, ticks=v
    #color_bar1.set_clim(270, 300) # thresholds where colorbar starts and ends
    
    # Plot Colorbar(s) without corresponding plot/mappable:
    norm = mpl.colors.Normalize(vmin=boundaries.lower, vmax=boundaries.upper)

    #SABO
    # https://stackoverflow.com/questions/43805821/matplotlib-add-colorbar-to-non-mappable-object
    mscmp = plt.cm.ScalarMappable(cmap=cmm, norm=norm)
    mscmp.set_clim(boundaries.lower, boundaries.upper)

    # ticks determins where the ticks are set and can exceed the color limits set by clim.
    #color_bar1 = mpl.colorbar.ColorbarBase(cbaxes1, cmap=cmm, norm=norm, extend='both', ticks=np.arange(250, 330, 5))
    color_bar1 = mpl.colorbar.ColorbarBase(cbaxes1, mscmp, extend='both', ticks=np.arange(250, 330, 5)) #SABO
    
    # @cbook.deprecated("3.1", alternative="ScalarMappable.set_clim")
    #color_bar1.set_clim(boundaries.lower, boundaries.upper) #deprecated
    
    #bounds = np.linspace(settings['figures']['relhumlower'], settings['figures']['relhumupper'], (((settings['figures']['relhumupper']-settings['figures']['relhumlower'])/5)+1))
    bounds = np.linspace(settings['figures']['relhumlower'], settings['figures']['relhumupper'], \
                         int((((settings['figures']['relhumupper']-settings['figures']['relhumlower'])/5)+1))) #SABO casted to int
    
    norm = mcl.BoundaryNorm(bounds, cmap2.N)

    #SABO
    # https://stackoverflow.com/questions/43805821/matplotlib-add-colorbar-to-non-mappable-object
    mscmp2 = plt.cm.ScalarMappable(cmap=cmap2, norm=norm)
    mscmp2.set_clim(settings['figures']['relhumlower'], settings['figures']['relhumupper'])

    

    #color_bar2 = mpl.colorbar.ColorbarBase(cbaxes2, cmap=cmap2,norm=norm,extend='min',ticks=np.arange(0, 101, 10)) #deprecated
    color_bar2 = mpl.colorbar.ColorbarBase(cbaxes2, mscmp2, extend='min',ticks=np.arange(0, 101, 10))
    #color_bar2.set_clim(settings['figures']['relhumlower'], settings['figures']['relhumupper']) #deprecated
    
    #[label.set_visible(True) for label in ax1.get_xticklabels()]
    #plt.setp(ax1.get_xticklabels(), visible=True)
    #plt.setp(ax2.get_xticklabels(), visible=True)
    
    
    
    ax2.xaxis.set_major_locator( locatormajor ) # tick with label every hour
    ax2.xaxis.set_minor_locator( locatorminor ) # minor tick every half hour
    ax2.xaxis.set_major_formatter( DateFormatter('%H'))
    ax2.tick_params(axis='both', which='major', labelsize=settings['figures']['tickfontsize']) # size for x and y-axis labels

    #ax2.set_axis_bgcolor(settings['figures']['nancolor']) #deprecated
    ax1.set_facecolor(settings['figures']['nancolor']) #SABO
    
    # define colors for ticks on x and y in both subplots:
    cbytick_obj = plt.getp(ax1, 'xticklabels')
    plt.setp(cbytick_obj, color=settings['figures']['fontcolor'])
    cbytick_obj = plt.getp(ax1, 'yticklabels')
    plt.setp(cbytick_obj, color=settings['figures']['fontcolor'])
    cbytick_obj = plt.getp(ax2, 'xticklabels')
    plt.setp(cbytick_obj, color=settings['figures']['fontcolor'])
    cbytick_obj = plt.getp(ax2, 'yticklabels')
    plt.setp(cbytick_obj, color=settings['figures']['fontcolor'])
    
    #colorbarproperties
    cbytick_obj = plt.getp(color_bar1.ax.axes, 'yticklabels')
    plt.setp(cbytick_obj, color=settings['figures']['fontcolor'])
    cbytick_obj = plt.getp(color_bar2.ax.axes, 'yticklabels')
    plt.setp(cbytick_obj, color=settings['figures']['fontcolor'])
    
    color_bar1.outline.set_edgecolor(settings['figures']['edgecolor'])
    color_bar1.outline.set_linewidth(1)
    color_bar1.ax.tick_params(labelsize=settings['figures']['axisfontsize']) 
    color_bar2.outline.set_edgecolor(settings['figures']['edgecolor'])
    color_bar2.outline.set_linewidth(1)
    color_bar2.ax.tick_params(labelsize=settings['figures']['axisfontsize']) 
    

    fig.subplots_adjust(hspace=0)
    #plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
    height_factor=0.02
    pos1 = ax1.get_position() # get the original position
    pos2 = [pos1.x0 - 0.08, pos1.y0+0.04,  pos1.width*1.15, pos1.height+height_factor] 
    ax1.set_position(pos2) # set a new position
    pos1 = ax2.get_position() # get the original position
    pos2 = [pos1.x0 - 0.08, pos1.y0-height_factor-0.018,  pos1.width*1.15, pos1.height+height_factor] 
    ax2.set_position(pos2) # set a new position
    
    ## Add rain axis
    #SABO
    create_rain_axis(plt, fig, df_rainflag_norm, pos2, locatormajor, locatorminor)
    
    plt.annotate('HATPRO (passive microwave radiometer) vertical profiles: Color surfaces for 10-min averages and contour lines for 50-min moving averages. Top panel: temperature and potential temperature as black and white contour lines, respectively.', xy=(950, 3), style='italic', xycoords='figure pixels',horizontalalignment='center',verticalalignment='bottom',color='gray', fontsize=11)
    #if(data_rh>0 and data_t>0):
    datevecc=rh.index[-1]
    zeroline=datevecc.floor(freq='1440min')
    ax2.axvline(zeroline, color='#dddddd', linewidth=3, zorder=1) # vertical line in second subplot: start of the current day
    ax2.axvline(zeroline, color='#000014', linewidth=1.5, zorder=1) # vertical line in second subplot: start of the current day
    ax2.axhline(1.75, color='#444444', zorder=1) # horizontal line in second subplot
    #if(data_t>0):
    datevecc=df_t.index[-1]
    zeroline=datevecc.floor(freq='1440min')
    ax1.axvline(zeroline, color='#dddddd', linewidth=3, zorder=1) # vertical line in second subplot: start of the current day
    ax1.axvline(zeroline, color='#000014', linewidth=1.5, zorder=1) # vertical line in second subplot: start of the current day
    ax1.axhline(1.75, color='#444444', zorder=1) # horizontal line in first subplot. If moving line by 0.1 km, change y-offset of image and axis by 0.01


    if(data_rh==0):
        plt.annotate('humidity data missing', xy=(1450, 20), style='italic', xycoords='figure pixels',horizontalalignment='right',verticalalignment='bottom',color='#F6CECE', fontsize=13)
    if(data_t==0):
        plt.annotate('temperature data missing', xy=(1695, 20), style='italic', xycoords='figure pixels',horizontalalignment='right',verticalalignment='bottom',color='#F8E0E0', fontsize=13)
    
    ws_threshold = settings['processing']['sybase_availability']
    if weather_station_availability <= ws_threshold:
        plt.annotate(f'weatherstation threshold: {ws_threshold}% higher then availability: {round(weather_station_availability,2)}%', 
                     xy=(1890, 20), 
                     style='italic', 
                     xycoords='figure pixels',
                     horizontalalignment='right',
                     verticalalignment='bottom',
                     color='#F8E0E0', 
                     fontsize=13)
    elif(data_sybase==0):
        plt.annotate('own weatherstation data missing', xy=(1890, 20), style='italic', xycoords='figure pixels',horizontalalignment='right',verticalalignment='bottom',color='#F8E0E0', fontsize=13)
    
    # if run again without loading rh new, add 5 to land where we started

    #insert crest height image
    im = plt.imread(get_sample_data(settings_url['crestheight_icon_location']))
    newax = fig.add_axes([0.0260, 0.6977, 0.016, 0.015]) # for crest height=1.85km: [0.0260, 0.7077, 0.016, 0.015])
    newax.imshow(im)
    #insert crest height line
    newax.axis('off')
    newaxis1 = fig.add_axes([0.0275, 0.7127, 0.013, 0.02]) 
    newaxis1.patch.set_visible(False)
    newaxis1.axis('off')
    newaxis1.axes.get_xaxis().set_visible(False)
    newaxis1.axes.get_yaxis().set_visible(False)
    newaxis1.axhline(0, color="#d9d9d9", linewidth=1.5) # horizontal line in second subplot

    #insert crest height image
    im = plt.imread(get_sample_data(settings_url['crestheight_icon_location']))
    newax = fig.add_axes([0.0260, 0.229, 0.016, 0.015])
    newax.imshow(im)
    #insert crest height line
    newax.axis('off')
    newaxis1 = fig.add_axes([0.0275, 0.244, 0.013, 0.02]) 
    newaxis1.patch.set_visible(False)
    newaxis1.axis('off')
    newaxis1.axes.get_xaxis().set_visible(False)
    newaxis1.axes.get_yaxis().set_visible(False)
    newaxis1.axhline(0, color="#d9d9d9", linewidth=1.5) # horizontal line in second subplot

    ax1.grid(True)
    ax2.grid(True)
    if archive > '0': #if archive=1 then only day in filename
        plt.savefig(settings_url['export_png_url'] +'/hatpro_' + '{:%Y%m%d}'.format(df_t.index[0]) +'.png', facecolor=fig.get_facecolor()) # specific filename for archive
    else:
        plt.savefig(settings_url['export_png_url'] +'/' +settings_url['current_figure_name'], facecolor=fig.get_facecolor()) # save current image with general filename
  #  plt.show()
