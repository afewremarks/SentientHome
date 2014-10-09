#!/usr/local/bin/python -u
__author__ = "Oliver Ratzesberger"

print "Starting InfluxDB JSON feed for Netatmo"

import requests
import json
import random
import time
import os
import ConfigParser
import lnetatmo

# Conversion: Celcius to Fahrenheit
def CtoF(t):
  return (t*9)/5+32

# Conversion: mili Bar to inch Hg
def mBtoiHg(p):
  return p*0.02953

# Conversion: millimeter to inch
def mmtoin(m):
  return m*0.03937

config = ConfigParser.ConfigParser()
config.read(os.path.expanduser('~/home.cfg'))

influx_addr           = config.get('influxdb', 'influx_addr')
influx_port           = config.get('influxdb', 'influx_port')
influx_db             = config.get('influxdb', 'influx_db')
influx_user           = config.get('influxdb', 'influx_user')
influx_pass           = config.get('influxdb', 'influx_pass')
netatmo_client_id     = config.get('netatmo', 'netatmo_client_id')
netatmo_client_secret = config.get('netatmo', 'netatmo_client_secret')
netatmo_user          = config.get('netatmo', 'netatmo_user')
netatmo_pass          = config.get('netatmo', 'netatmo_pass')
netatmo_poll_interval = int(config.get('netatmo', 'netatmo_poll_interval', 5))


influx_path = "http://" + influx_addr + ":" + influx_port + "/db/" + influx_db + "/series?time_precision=s&u=" + influx_user
print "Path: " + influx_path

authorization = lnetatmo.ClientAuth( clientId = netatmo_client_id,
                            clientSecret = netatmo_client_secret,
                            username = netatmo_user,
                            password = netatmo_pass )

while True:
  devList = lnetatmo.DeviceList(authorization)

  print devList.lastData().keys()

  devData = devList.lastData()

  # Optional metric to imperal conversions
  # Not all sensors have all metrics
  for key in devData.keys():
    try:
      devData[key]['TemperatureF']=CtoF(devData[key]['Temperature'])
      devData[key]['min_tempF']=CtoF(devData[key]['min_temp'])
      devData[key]['max_tempF']=CtoF(devData[key]['max_temp'])
    except Exception:
      pass

    try:
      devData[key]['PressureiHg']=mBtoiHg(devData[key]['Pressure'])
    except Exception:
      pass

    try:
      devData[key]['sum_rain_1in']=mmtoin(devData[key]['sum_rain_1'])
      devData[key]['sum_rain_24in']=mmtoin(devData[key]['sum_rain_24'])
    except Exception:
      pass

    event = [{
      'name': 'netatmo.' + key,
      'columns': devData[key].keys(),
      'points': [ devData[key].values() ]
    }]

    print event

    try:
      r = requests.post(influx_path + "&p=" + influx_pass, data=json.dumps(event))
      print r
    except Exception:
      print 'Exception posting data to ' + influx_path
      pass

  time.sleep(netatmo_poll_interval)
