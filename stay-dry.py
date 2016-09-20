import json, urllib.request, datetime
from time import sleep

current_url = 'http://api.openweathermap.org/data/2.5/weather?q=Winnipeg&APPID='
forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?q=Winnipeg&APPID='
key = '7fbef229d61af82f1ae6a7afde748f9c'

def will_it_rain(): # is it going to rain?
    response = urllib.request.urlopen(current_url+key)
    response_str = response.read().decode('utf-8')
    data = json.loads(response_str)
    rain = '3h' in data['rain'] # is it raining right now?
    if not rain:
        response = urllib.request.urlopen(forecast_url+key)
        response_str = response.read().decode('utf-8')
        data = json.loads(response_str)
        rain = '3h' in data['list'][1]['rain'] # will it rain on the way home?
    return rain

weekday = datetime.datetime.today().weekday()
if weekday < 5: # monday - friday
    if will_it_rain():
        # set alarm for bussing
    else:
        # set alarm for cycling

# setting alarm: probably use mpv and a usb speaker? 
