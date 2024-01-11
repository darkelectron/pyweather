#! /usr/bin/env python

import requests
import json
import argparse
import configparser
import os

CONFIG_FILE_LOCATION = os.path.expanduser('~/.config/pyweather/config.ini')  # issue without os.path thing


def check_config_file():
    if not os.path.isfile(CONFIG_FILE_LOCATION):
        print("[-] Config File Not Found")
        exit(1)


def get_latlong_from_ip():
    latlong = requests.get("https://ipapi.co/latlong")

    if latlong.status_code == 200:
        return latlong.text.split(',')
    else:
        print(f"[-] Returned Code: {latlong.status_code}")
        return False


check_config_file()
config = configparser.ConfigParser()
config.read(CONFIG_FILE_LOCATION)

if config.sections() is None:
    print("[-] Config File Missing Section")
    exit(1)
else:
    # check empty options
    for a in config.items('DEFAULTS'):
        if '' in a:
            print("[-] Empty Options Found in [DEFAULTS] Section")
            exit(1)

    config_defaults = config['DEFAULTS']

if config['LOCATION']['provider'] == "Manual":
    LAT = config_defaults.get('LAT')
    LON = config_defaults.get('LON')
else:
    latlong = get_latlong_from_ip()

    if latlong is not False:
        LAT = latlong[0]
        LON = latlong[1]
    else:
        exit(1)

API_KEY = config_defaults.get('API_KEY')
UNITS = config_defaults.get('UNITS')

OWM_LINK = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose')
parser.add_argument('--print-json', action='store_true', default=False, help='print json')
parser.add_argument('--version', action='store_true', help='print version [does not work]')
args = parser.parse_args()

if args.version is True:
    os.system('git describe')
    exit(0)

weather = requests.get(OWM_LINK)

if weather:
    weather_json = weather.json()
else:
    print(weather)
    print("[-] Something Went Wrong")
    exit(1)

if args.print_json is True:
    print(json.dumps(weather_json, indent=4))
    print("weather", weather_json["weather"])
    print("main", weather_json["main"])
    print(weather_json["main"].keys())
    print(weather_json["main"]["feels_like"])

for i in weather_json["weather"]:
    weather_icon = i["icon"]


rounded_feels_like = round(weather_json["main"]["feels_like"])

config_icons = config['ICONS']
ICON = config_icons.get(weather_icon)
format = f"%{{F#FF0000}}%{{T3}}{ICON} %{{T-}}%{{F-}}{rounded_feels_like}°C"

print(format)
