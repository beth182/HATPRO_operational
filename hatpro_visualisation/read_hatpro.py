#!/usr/bin/env python
# pass over the file name
import pandas as pd
import sys
import re

LEVEL_RE = re.compile(r'^\#.*(v\d+).*Hatpro (\d+)m.*$')

def read_data(filename):
    # loop through all lines and look for vertical level indications: lines that start with "v"
    #print os.path.getsize(filepath+filename)
    print(f'...opening file {filename}')
    with open(filename, 'r') as f: # open file
        d_levels={} #create dictionary for object-pairs:
        line_num=0
        for line in f: # loop through all lines
            line_num=line_num+1
            match = LEVEL_RE.match(line.strip())
            if match: # first character of line is a 'v'?
                #print "true: "+line
                level=match.group(1)
                height=match.group(2)
                try:
                    int(height)
                except ValueError:
                    print('read_hatpro.py cant find the height information in the header of the data file, check the code')
                    raise
                    pass
                d_levels.update({level: height}) # add pair to dictionary
            elif line[0:3] == 'raw':
                start=line_num # last "rawdate" determines start of data -> overwrite first time where rawdate was found
                break
        #else:
        #print "false"
        #look whether the line starts with a "v"
    f.closed
    start=start-1
    # read HATPRO Data
    df = pd.read_csv(filename, skiprows=start, sep=";", index_col=0, encoding='utf-8')
    data_levels=df.shape[1] # subtract cell with string "rawdate"
    df.index=pd.to_datetime(df.index, format='%Y%m%d %H:%M:%S')
    
    #del df.index.name #del rawdate
    df.reset_index(drop=True) #SABO

    if data_levels != len(d_levels):
        print ("-------------------error while reading data {}: levels not the same lenght".format(filename))
        print(d_levels)
        print(len(d_levels))
    #else: 
        #print ("comparions successfully")
    ##cosmetics for dataframes
    array=[]
    for i in df.columns:
        height=d_levels.get(i)
        array.append(height)
    df.columns=array
    return(d_levels, df)

def read_hatpro_ws(filename):
    '''read hatpro weather station: relative humidity, non-reduced pressure [hPa], rain-flag: sum of rain-seconds, max 600, temperature [K], wind direction and wind speed [ms-1]'''
    # determine start of data to jump over a header that is currently not a fixed length
    with open(filename, 'r') as f: # open file
        line_num=0
        for line in f: # loop through all lines
            if line[0:3] == 'raw':
                start=line_num
                break
            line_num=line_num+1
    f.closed
    df = pd.read_csv(filename, sep=";", index_col=0,skiprows=start)
    df.index=pd.to_datetime(df.index, format='%Y%m%d %H:%M:%S')

    #del df.index.name #del rawdate
    df.reset_index(drop=True) #SABO

    return(df)
