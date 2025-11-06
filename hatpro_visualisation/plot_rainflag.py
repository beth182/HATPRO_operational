from datetime import timedelta
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter

from settings import SETTINGS as settings

#at line 299 in plot.py

def create_rain_axis(plt, fig, df_rainflag_norm, pos2, locatormajor, locatorminor):
    rainax = fig.add_axes([pos2[0], pos2[1]+pos2[3]+0.01, pos2[2], 0.018])
    
    ## SABO die 2 zeilen rauskommentiert, weil die regen/empty anzeige verschoben ist
    #df_rainflag_norm.index = \
    #    df_rainflag_norm.index-timedelta(minutes=+settings['processing']['time_delta'])
    
    """
    with pd.option_context('display.max_rows', 150,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
        print(df_rainflag_norm)
    """

    # to plot empty shaded bars where nan, do some replacement
    df_rainflag_nanplot = df_rainflag_norm.copy()
    df_rainflag_nanplot[df_rainflag_nanplot < 1.1] = 0.1
    df_rainflag_nanplot[df_rainflag_nanplot.isnull()] = 1
    df_rainflag_nanplot[df_rainflag_nanplot < 0.9] = np.nan

    """
    with pd.option_context('display.max_rows', 150,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
        print(df_rainflag_nanplot)
    """

    #precipflagplot=plt.bar(df_rainflag_norm.index,df_rainflag_norm.values, width=0.0068,  color=settings['figures']['precipitation_color'])
    precipflagplot = plt.bar(df_rainflag_norm.index, df_rainflag_norm.values.reshape(len(df_rainflag_norm)), 
                             width=0.0068,  color=settings['figures']['precipitation_color']) #SABO
    
    ##ORIG
    #precipflagplot_nan=plt.bar(df_rainflag_nanplot.index,
    #                           df_rainflag_nanplot.values, 
    #                           width=0.007, 
    #                           color=settings['figures']['bgcolor'], 
    #                           edgecolor=settings['figures']['nancolor'], 
    #                           hatch='//')
    
    precipflagplot_nan = plt.bar(
                                df_rainflag_nanplot.index, 
                                #df_rainflag_nanplot.values, 
                                df_rainflag_nanplot.values.reshape(len(df_rainflag_nanplot)), 
                                width=0.007, 
                                #width=0.001, 
                                color=settings['figures']['bgcolor'], 
                                edgecolor=settings['figures']['nancolor'], 
                                hatch='//'
                            ) #SABO
    

    #precipflagplot.set_hatch('x')
    rainax.xaxis.set_major_locator( locatormajor ) # tick with label every hour
    rainax.xaxis.set_minor_locator( locatorminor ) # minor tick every half hour
    rainax.xaxis.set_major_formatter( DateFormatter('%H'))
    rainax.tick_params(axis='both', which='major', labelsize=settings['figures']['tickfontsize']) # size for x and y-axis labels

    #rainax.set_axis_bgcolor(settings['figures']['nancolor'])
    rainax.set_facecolor(settings['figures']['nancolor']) #SABO

    # for correct display, add the timedelta once again, used for xlim
    ## SABO die 2 zeilen rauskommentiert, weil die regen/empty anzeige verschoben ist
    #df_rainflag_norm.index = \
    #    df_rainflag_norm.index+timedelta(minutes=+settings['processing']['time_delta'])
    
    # add 10 minutes to be consistent with the LIDAR where the space at the recent timestamp is needed for the barbs
    rainax.set_xlim([df_rainflag_norm.index[0], df_rainflag_norm.index[-1]])

    #rainax.set_xlim([df_rainflag_norm.index[0], df_rainflag_norm.index[-1]+timedelta(minutes=settings['processing']['time_delta'])])
    
    # not to 1 but 0.825 as not every second measured, usually max(rain in 10min): 495seconds
    rainax.set_ylim([0,0.825]) 
    plt.annotate(
                'precipitation\nduration\nwithin 10min', 
                xy=(1815, 516), 
                xycoords='figure pixels',
                horizontalalignment='left',
                verticalalignment='bottom',
                color=settings['figures']['precipitation_color'], 
                fontsize=11
    )

    rainax.patch.set_visible(False)
    #rainax.axis('off')
    rainax.axes.get_xaxis().set_visible(False)
    rainax.axes.get_yaxis().set_visible(False)
    
    rainax.spines['bottom'].set_color(settings['figures']['precipitation_color'])
    rainax.spines['top'].set_color(settings['figures']['precipitation_color']) #axis upper edge
    rainax.spines['right'].set_color(settings['figures']['precipitation_color'])#axis right edge
    rainax.spines['left'].set_color(settings['figures']['precipitation_color'])#axis left edge
