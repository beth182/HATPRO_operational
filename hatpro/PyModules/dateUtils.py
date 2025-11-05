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
    # minute = actdt.strftime("%M")
    minute = int(actdt.strftime("%M"))

    rangeminute = minute // minrange

    y = int(actdt.strftime("%Y"))
    m = int(actdt.strftime("%m"))
    d = int(actdt.strftime("%d"))
    H = int(actdt.strftime("%H"))

    # Ensure the minute value is valid (0–59)
    minute_value = (rangeminute * minrange) % 60

    # Construct the datetime object
    # rangedt = dt.datetime(y,m,d,H,int(rangeminute*10),0,0,pytz.UTC)
    rangedt = dt.datetime(y, m, d, H, minute_value, 0, 0, pytz.UTC)

    return int(time.mktime(rangedt.timetuple()))


