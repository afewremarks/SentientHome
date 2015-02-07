#!/usr/local/bin/python3 -u
__author__    = 'Oliver Ratzesberger <https://github.com/fxstein>'
__copyright__ = 'Copyright (C) 2015 Oliver Ratzesberger'
__license__   = 'Apache License, Version 2.0'

# Make sure we have access to SentientHome commons
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))  + '/..')

# Sentient Home configuration
from common.shconfig import shConfig
from common.sheventhandler import shEventHandler

import logging as log
log.info('Starting SentientHome Tracer')

import time

# Simple tracer that 'fires' events on a predefined interval

config = shConfig('~/.config/home/home.cfg')
handler = shEventHandler(config, config.getfloat('sentienthome', 'tracer_interval', 10))

count = 0

while True:
    count += 1

    tm = time.time()
    st = time.localtime()
    eventtype = 'localtime'
    event = [{
        'name': 'tracer', # Time Series Name
        'columns': ['time', 'count', 'eventtype',
                    'year', 'month', 'yday', 'mday', 'wday',
                    'hour24', 'hour12', 'min', 'sec',
                    'isdst', 'tzone', 'gmtoff'
                    ], # Keys
        'points': [[tm, count, eventtype,
                    st.tm_year, st.tm_mon, st.tm_yday, st.tm_mday, st.tm_wday,
                    st.tm_hour, st.tm_hour % 12, st.tm_min, st.tm_sec,
                    st.tm_isdst, st.tm_zone, st.tm_gmtoff
                    ], ] # Data points
    }]

    log.debug('Event data: %s', event)

    handler.postEvent(event)

    # We reset the poll interval in case the configuration has changed
    handler.sleep(config.getfloat('sentienthome', 'tracer_interval', 10))
