#!/bin/python

import json, urllib.request, datetime, subprocess, os.path, time

url = 'https://api.darksky.net/forecast' # api url
key = '7b74f3837ab0f63bfb389ee1a45e7295' # api key

def read_config():
    settings = {}
    if os.path.isfile(os.path.join(os.path.expanduser('~'), '.config', 'stay-dry', 'config')):
        file_path = os.path.join(os.path.expanduser('~'), '.config', 'stay-dry', 'config')
    else:
        file_path = os.path.join(os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'stay-dry', 'config'))
    with open(logfile, 'a') as log:
        log.write('Reading config file from %s\n' % file_path)
    with open(file_path) as config:
        lines = config.read().splitlines()
        for line in lines:
            try:
                settings[line.split(' = ')[0]] = int(line.split(' = ')[1])
            except ValueError as e:
                settings[line.split(' = ')[0]] = line.split(' = ')[1]
    # do some conversions
    settings['mwf_start'] = (int(settings['mwf_start'].split(':')[0]) + int(settings['mwf_start'].split(':')[1]) / 60) * 60
    settings['tr_start'] = (int(settings['tr_start'].split(':')[0]) + int(settings['tr_start'].split(':')[1]) / 60) * 60
    settings['run_time'] = (int(settings['run_time'].split(':')[0]) + int(settings['run_time'].split(':')[1]) / 60) * 60
    return settings

def will_it_rain():
    # get forecast from dark sky api
    response = urllib.request.urlopen('/'.join((url, key, settings['location'])))
    response_str = response.read().decode('utf-8')
    weather = json.loads(response_str)
    # check if it's raining now or if it will rain on the way home
    rain_now = weather['currently']['precipProbability']
    rain_later = weather['hourly']['data'][9]['precipProbability']
    with open(logfile, 'a') as log:
        log.write('Change of rain right now: %d\nChance of rain forecasted: %d\n' % (rain_now, rain_later))
    return rain_now or rain_later

def get_sleep_time(mwf, rain):
    if mwf:
        if rain:
            sleep_time = settings['mwf_start'] - settings['run_time'] - settings['prep_time'] - settings['bus_time'] - settings['cushion']
        else:
            sleep_time = settings['mwf_start'] - settings['run_time'] - settings['prep_time'] - settings['bike_time'] - settings['cushion']
    else:
        if rain:
            sleep_time = settings['tr_start'] - settings['run_time'] - settings['prep_time'] - settings['bus_time'] - settings['cushion']
        else:
            sleep_time = settings['tr_start'] - settings['run_time'] - settings['prep_time'] - settings['bike_time'] - settings['cushion']
    with open(logfile, 'a') as log:
        log.write('Sleeping for %d minutes\n' % sleep_time)
    return sleep_time * 60 # convert to seconds for time.sleep

def ring(): # wake me up (inside)
    tone_path = os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'stay-dry', 'tones', settings['tone'] + '.wav')
    with open(logfile, 'a') as log:
        if settings['player'] == 'mpv':
            try:
                subprocess.run(['mpv', tone_path, '--vo', 'null', '--loop-file'], timeout=settings['alarm_timeout'])
                log.write('Successfully played alarm with mpv.\n')
            except FileNotFoundError as e:
                log.write('Error: mpv not found.\n')
        elif settings['player'] == 'mplayer':
            try:
                subprocess.run(['mplayer', tone_path, '-vo', 'null', '-loop', '0'], timeout=settings['alarm_timeout'])
                log.write('Successfully played alarm with mplayer.\n')
            except FileNotFoundError as e:
                log.write('Error: mpv not found.\n')


if __name__ == '__main__':
    logfile = os.path.join(os.path.expanduser('~'), '.local', 'share', 'stay-dry', 'logs', time.strftime("%m-%d-%Y"))
    with open(logfile, 'a+') as log:
        log.write(time.strftime('%A, %B %d, %Y') + '\n')
    settings = read_config()
    weekday = datetime.datetime.today().weekday()
    if weekday < 5: # monday - friday
        time.sleep(get_sleep_time(weekday % 2 == 0, will_it_rain()))
        ring()
        
