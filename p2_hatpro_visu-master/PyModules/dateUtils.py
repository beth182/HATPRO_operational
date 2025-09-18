#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import calendar
import datetime as dt
import pytz
import time

def createDateTime(date):
    if len(date) <= 8:
        date = date + '0000'
    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    H = int(date[8:10])
    M = int(date[10:12])
    return dt.datetime(y,m,d,H,M,0,0,pytz.UTC)

def createNextRoundMin(utc, minrange=10):
    actdt =  dt.datetime.utcfromtimestamp(utc)
    minute = actdt.strftime("%M")
    rangeminute = int(minute) / minrange
    y = int(actdt.strftime("%y"))
    m = int(actdt.strftime("%m"))
    d = int(actdt.strftime("%d"))
    H = int(actdt.strftime("%H"))
    rangedt = dt.datetime(y,m,d,H,rangeminute*10,0,0,pytz.UTC)
    return int(time.mktime(rangedt.timetuple()))

