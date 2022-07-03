# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting the weather of a city. """

from json import loads
from datetime import datetime, timedelta

import requests
from pytz import country_names as c_n
from pytz import country_timezones as c_tz
from pytz import timezone as tz
from os import environ
from userbot import CMD_HELP
from userbot import OPEN_WEATHER_MAP_APPID as OWM_API
from userbot import is_mongo_alive, is_redis_alive
from userbot.events import register
from userbot.modules.dbhelper import get_weather, set_weather

# ===== CONSTANT =====
INV_PARAM = "`Invalid parameters. Try again!`"
NO_API_KEY = "`Get an API key from` https://openweathermap.org/ `first.`"
DB_FAILED = "`Database connections failed!`"

# ====================
city_given = ""

async def get_tz(con):
    """
    Get time zone of the given country.
    Credits: @aragon12 and @zakaryan2004.
    """
    for c_code in c_n:
        if con == c_n[c_code]:
            return tz(c_tz[c_code][0])
    try:
        if c_n[con]:
            return tz(c_tz[con][0])
    except KeyError:
        return


@register(outgoing=True, pattern="^.weather(?: |$)(.*)")
async def fetch_weather(weather):
    if environ.get("isSuspended") == "True":
        return
    """ For .weather command, gets the current weather of a city. """
    if OWM_API is None:
        await weather.edit(NO_API_KEY)
        return

    OpenWeatherAPI = OWM_API
    saved_props = await get_weather() if is_mongo_alive() else None

    if not weather.pattern_match.group(1):
        if 'weather_city' in saved_props:
            city = saved_props['weather_city']
        else:
            await weather.edit("`Please specify a city or set one as default.`"
                               )
            return
    else:
        city = weather.pattern_match.group(1)

    timezone_countries = {
        timezone: country
        for country, timezones in c_tz.items() for timezone in timezones
    }

    if "," in city:
        newcity = city.split(",")
        if len(newcity[1]) == 2:
            city = newcity[0].strip() + "," + newcity[1].strip()
        else:
            country = await get_tz((newcity[1].strip()).title())
            try:
                countrycode = timezone_countries[f'{country}']
            except KeyError:
                await weather.edit(INV_PARAM)
                return
            city = newcity[0].strip() + "," + countrycode.strip()
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={OpenWeatherAPI}'
    request = requests.get(url)
    result = loads(request.text)
    if request.status_code != 200:
        await weather.edit("Invalid parameters in geocoding url.")
        return
    lat = result[0]['lat']
    lon = result[0]['lon']
    cityName = result[0]['name']
    country = result[0]['country']
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={OpenWeatherAPI}'
    request = requests.get(url)
    result = loads(request.text)
    if request.status_code != 200:
        await weather.edit(INV_PARAM)
        return

    cityname = cityName
    curtemp = result["current"]['temp']
    humidity = result["current"]['humidity']
    #desc = result['weather'][0]
    #desc = desc['main']
    sunrise = result["current"]["sunrise"]
    sunset = result["current"]["sunset"]
    wind = result["current"]["wind_speed"]
    winddir = result["current"]["wind_deg"]
    feels = result["current"]["feels_like"]
    pressure = result["current"]["pressure"]
    summary = result["current"]["weather"][0]["main"]
    desc = result["current"]["weather"][0]["description"]
    uvi = result["current"]["uvi"]
    ctimezone = tz(c_tz[country][0])
    time = datetime.now().strftime("%A, %I:%M %p")
    fullc_n = c_n[f"{country}"]
    # dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    #        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    div = (360 / len(dirs))
    funmath = int((winddir + (div / 2)) / div)
    findir = dirs[funmath % len(dirs)]
    kmph = str(wind * 3.6).split(".")
    mph = str(wind * 2.237).split(".")

    def fahrenheit(fahr):
        temp = str(((fahr - 273.15) * 9 / 5 + 32)).split(".")
        return temp[0]

    def celsius(celc):
        temp = str((celc - 273.15)).split(".")
        return temp[0]

    def sun(unix):
        suntime = datetime.fromtimestamp(unix,
                                         tz=ctimezone).strftime("%I:%M %p")
        return suntime

    await weather.edit(
        f"**Temperature:** `{celsius(curtemp)}°C | {fahrenheit(curtemp)}°F`\n" +
        f"**Feels like:** `{celsius(feels)}°C | {fahrenheit(feels)}°F`\n" +
        f"**UV Index:** `{uvi}`\n" +
        f"**Pressure:** `{pressure} hPa`\n"
        f"**Humidity:** `{humidity}%`\n" +
        f"**Wind:** `{kmph[0]} kmh | {mph[0]} mph, {findir}`\n" +
        f"**Sunrise:** `{sun(sunrise)}`\n" +
        f"**Sunset:** `{sun(sunset)}`\n\n\n" +
        f"`{summary}, {desc}\n`"
        f"`{cityname}, {fullc_n}`\n" + f"`{time}`")

@register(outgoing=True, pattern="^.forecast(?: |$)(.*)")
async def fetch_forecast(weath):
    if environ.get("isSuspended") == "True":
        return
    """ For .weather command, gets the current weather of a city. """
    
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    head = {'user-agent': USER_AGENT}
    weather_writed = False #whether wheather is writed to variable (maked for not writing weather for next day in this hour
    max_hours = 12
    iterator = 0 #for forecast loop
    global city_given
    saved_props = await get_weather() if is_mongo_alive() else None
    if not weath.pattern_match.group(1):
        if 'weather_city' in saved_props:
            city_given = saved_props['weather_city']
        else:
            await weath.edit("`Please specify a city or set one as default.`")
            return
    else:
        city_given = weath.pattern_match.group(1)
    url_city = f'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=pjson&outFields=Addr_type&maxLocations=1&forStorage=false&SingleLine={city_given}'
    request_city = requests.get(url_city, headers=head)
    result_city = loads(request_city.content)
    city = result_city['candidates'][0]['address']
    forecast = f"Forecast for **{city}**:\n"
    lat = result_city['candidates'][0]['location']['y']
    lng = result_city['candidates'][0]['location']['x']
    url_weather = f'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lng}'
    request_city = requests.get(url_weather, headers=head)
    result_weather = loads(request_city.content)
    timeser = result_weather['properties']['timeseries']
    time_now = datetime.now().strftime("%H")
    for weather in timeser:
        all_date = datetime.strptime(weather['time'], "%Y-%m-%dT%H:%M:%SZ")
        hour = all_date.strftime("%H")
        weather_temp = weather['data']['instant']['details']['air_temperature']
        try:
            desc = weather['data']['next_1_hours']['summary']['symbol_code']
        except KeyError:
            pass #meaning desc is trying to get details which is unavaible. Also, we need only 6, which is avaible..
        if (hour == time_now) and (weather_writed == False):
            weather_writed = True
        if weather_writed and iterator != max_hours: #means we can write forecast now
            forecast += '`' + str(hour) + ":00`: `" + str(weather_temp) + '`°C, **' + desc + "**\n" 
            iterator += 1
    await weath.edit(forecast)
    
@register(outgoing=True, pattern="^.setcity(?: |$)(.*)")
async def set_default_city(scity):
    """ For .setcity command, change the default
        city for weather command. """
    if environ.get("isSuspended") == "True":
        return
    global city_given
    if not is_mongo_alive() or not is_redis_alive():
        await scity.edit(DB_FAILED)
        return

    if OWM_API is None:
        await scity.edit(NO_API_KEY)
        return

    OpenWeatherAPI = OWM_API

    if not scity.pattern_match.group(1):
        await scity.edit("`Please specify a city to set one as default.`")
        return
    else:
        city = scity.pattern_match.group(1)
        city_given = scity.pattern_match.group(1)

    timezone_countries = {
        timezone: country
        for country, timezones in c_tz.items() for timezone in timezones
    }

    if "," in city:
        newcity = city.split(",")
        if len(newcity[1]) == 2:
            city = newcity[0].strip() + "," + newcity[1].strip()
        else:
            country = await get_tz((newcity[1].strip()).title())
            try:
                countrycode = timezone_countries[f'{country}']
            except KeyError:
                await scity.edit(INV_PARAM)
                return
            city = newcity[0].strip() + "," + countrycode.strip()

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OpenWeatherAPI}'
    request = requests.get(url)
    result = loads(request.text)

    if request.status_code != 200:
        await scity.edit(INV_PARAM)
        return

    await set_weather(city)
    cityname = result['name']
    country = result['sys']['country']

    fullc_n = c_n[f"{country}"]

    await scity.edit(f"`Set default city as {cityname}, {fullc_n}.`")


CMD_HELP.update({"weather": ["Weather",
    " - `.weather <city> or .weather <city>, <country name/code>`: "
    "Gets the weather of a city.\n"
    " - `.forecst <city> or .forecast <city>, <country name/code>`: "
    "Gets the weather of a city by every 12 hours.\n" 
    " - `.setcity <city> or .setcity <city>, <country name/code>`: "
    "Set the default city for the .weather command.\n"]
})
