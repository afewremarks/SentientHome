#!/usr/local/bin/python3 -u
__author__ = 'Oliver Ratzesberger <https://github.com/fxstein>'
__copyright__ = 'Copyright (C) 2015 Oliver Ratzesberger'
__license__ = 'Apache License, Version 2.0'

# Make sure we have access to SentientHome commons
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

# Sentient Home Application
from common.shapp import shApp
from common.sheventhandler import shEventHandler

import json

# Default settings
from cement.utils.misc import init_defaults

defaults = init_defaults('usgs_quake', 'usgs_quake')
defaults['usgs_quake']['poll_interval'] = 10.0

with shApp('usgs_quake', config_defaults=defaults) as app:
    app.run()

    handler = shEventHandler(app, dedupe=True)

    # Initial poll - most likely a day if the increments are hourly data
    # We do this to catchup on events in case the feed was down for some time
    path = app.config.get('usgs_quake', 'usgs_quake_init_path')

    while True:
        # Get all earthquakes of the past hour
        r = handler.get(app.config.get('usgs_quake', 'usgs_quake_addr') +
                        path)
        data = json.loads(r.text)

        m = data['metadata']

        event = [{
            'name': 'usgs.earthquake.metadata',     # Time Series Name
            'columns': ['title', 'count', 'generated', 'api', 'status'],  # Keys
            'points': [[m['title'], m['count'], m['generated'],
                        m['api'], m['status']]]     # Data points
        }]

        app.log.debug('Event data: %s' % event)

        handler.postEvent(event, dedupe=True)

        # Need to revser the order of incoming events as news are on top but we
        # need to process in the order they happened.
        features = data['features'][::-1]

        for f in features:
            event = [{
                'name': 'usgs.earthquake.feature',      # Time Series Name
                'columns': ['id', 'long', 'lat', 'depth', 'mag', 'type',
                            'magtype', 'tz', 'felt', 'place', 'status',
                            'gap', 'dmin', 'rms', 'ids', 'title', 'types',
                            'cdi', 'net', 'nst', 'sources', 'alert', 'time',
                            'tsunami', 'code', 'sig'
                            ],                          # Keys
                'points': [[f['id'],
                            f['geometry']['coordinates'][0],
                            f['geometry']['coordinates'][1],
                            f['geometry']['coordinates'][2],
                            f['properties']['mag'],
                            f['properties']['type'],
                            f['properties']['magType'],
                            f['properties']['tz'],
                            f['properties']['felt'],
                            f['properties']['place'],
                            f['properties']['status'],
                            f['properties']['gap'],
                            f['properties']['dmin'],
                            f['properties']['rms'],
                            f['properties']['ids'],
                            f['properties']['title'],
                            f['properties']['types'],
                            f['properties']['cdi'],
                            f['properties']['net'],
                            f['properties']['nst'],
                            f['properties']['sources'],
                            f['properties']['alert'],
                            f['properties']['time'],
                            f['properties']['tsunami'],
                            f['properties']['code'],
                            f['properties']['sig']]]    # Data points
            }]
            # dedupe automatically ignores events we have processed before
            handler.postEvent(event, dedupe=True)

        # We reset the poll interval in case the configuration has changed
        handler.sleep()

        # Reset poll path before looping with latest setting
        path = app.config.get('usgs_quake', 'usgs_quake_path')
