"""
Weather Data
============

A simple backend to get data from the British Met Office API.


Requirements
------------

:requires: MetOffer


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 03-Aug-2016
"""
import metoffer
import pprint
import pandas as pd


def getNearestLocationData(lat, lon, apikey):
    M = metoffer.MetOffer(apikey)
    data = M.nearest_loc_forecast(lat, lon, metoffer.THREE_HOURLY)
    data = metoffer.parse_val(data)

    return data


def SimpleExample():
    apikey = '7e2ecd8b-e840-4d06-8eba-5b48ff725cb0'
    data = getNearestLocationData(51.52054, -0.09773, apikey)

    print(data.name, data.lat, data.lon, data.elevation)
    pprint.pprint(data.data)

    for i in data.data:
        print(
            "{} - {}".format(i["timestamp"][0].strftime("%d %b, %H:%M"), metoffer.WEATHER_CODES[i["Weather Type"][0]]))

    print(metoffer.guidance_UV(data.data[0]["Max UV Index"][0]))


def mapExample():
    apikey = '7e2ecd8b-e840-4d06-8eba-5b48ff725cb0'
    M = metoffer.MetOffer(apikey)
    data = M.map_overlay_obs()

    for x in data['Layers']['Layer']:
        if x['@displayName'] == 'Lightning':
            latestLightning = x['Service']['Times']['Time'][0]
        if x['@displayName'] == 'Rainfall':
            latestRainfall = x['Service']['Times']['Time'][0]

    print(latestLightning)
    print(latestRainfall)


if __name__ == '__main__':
    #SimpleExample()

    mapExample()