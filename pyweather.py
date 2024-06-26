#! /usr/bin/env python

import requests
import json
import argparse
import configparser
import os
import ephem
import datetime

CONFIG_FILE_LOCATION = os.path.expanduser('~/.config/pyweather/config.ini')  # issue without os.path thing


def check_config_file():
    if not os.path.isfile(CONFIG_FILE_LOCATION):
        print("[-] Config File Not Found")
        exit(1)


def get_latlong_from_ip():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.10 Safari/537.3'
    }
    # Use a session to maintain cookies
    session = requests.Session()
    # Make a request with the custom headers and session
    latlong = session.get('https://ipapi.co/latlong', headers=headers)

    if latlong.status_code == 200:
        return latlong.text.split(',')
    else:
        print(f"[-] Returned Code: {latlong.status_code}")
        return False


def get_format():
    return config['DEFAULTS']['FORMAT']


def get_moon_phase():
    date = datetime.date.today()
    observer = ephem.Observer()
    observer.date = date

    moon = ephem.Moon(observer)
    phase = moon.moon_phase

    if phase < 0.25:
        # print(f"Moon phase for {today}: New Moon")
        return "nm"
    elif phase < 0.5:
        # print(f"Moon phase for {today}: First Quarter")
        return "fq"
    elif phase < 0.75:
        # print(f"Moon phase for {today}: Full Moon")
        return "fm"
    else:
        # print(f"Moon phase for {today}: Last Quarter")
        return "lq"

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

if weather_icon == "01n":
    config_icons = config['MOON']
    ICON = config_icons.get(get_moon_phase())
else:
    config_icons = config['ICONS']
    ICON = config_icons.get(weather_icon)

format_from_text = get_format()
format = format_from_text.replace("ICON", ICON).replace("TEMP_FEELS_LIKE", str(rounded_feels_like))
print(format)
