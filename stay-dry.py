#!/bin/python

import json, urllib.request, datetime, subprocess, os.path, time

url = 'https://api.darksky.net/forecast' # api url
key = '7b74f3837ab0f63bfb389ee1a45e7295' # api key

# returns dict of settings + their values
def read_config():
    settings = {}
    if os.path.isfile(os.path.join(os.path.expanduser('~'), '.config', 'stay-dry', 'config')):
        file_path = os.path.join(os.path.expanduser('~'), '.config', 'stay-dry', 'config')
    else:
        file_path = os.path.join(os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'stay-dry', 'config'))
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

# returns boolean: whether or not it is going to rain
def will_it_rain():
    # get forecast from dark sky api
    address = '/'.join((url, key, settings['location']))
    log.write('Getting weather data from %s.\n' % address)
    try:
        response = urllib.request.urlopen(address)
        response_str = response.read().decode('utf-8')
        weather = json.loads(response_str)
        # check if it's raining now, if it will rain on the way to school, or if it will rain on the way home
        rain_now = weather['currently']['precipProbability']
        rain_later = weather['hourly']['data'][1]['precipProbability']
        rain_later_later = weather['hourly']['data'][9]['precipProbability']
        log.write('Chance of rain right now: %.1f%%\nIn an hour: %.1f%%\nForecasted: %.1f%%\n' %
                  (rain_now * 100, rain_later * 100, rain_later_later * 100))
        return rain_now > settings['threshold'] / 100 or rain_later > settings['threshold'] / 100 or rain_later_later > settings['threshold'] / 100
    except urllib.error.URLError as e:
        log.write('%s: %s' % ( e, address))
        return True # be conservative upon connection failure


# returns int: minutes to sleep before alarm rings
# mwf: whether or not is a monday, wednesday, or friday
# rain: whether or not it is going to rain
def get_sleep_time(mwf, rain):
    sleep_time = - settings['run_time'] - settings['prep_time'] - settings['cushion']
    if mwf:
        sleep_time += settings['mwf_start']
    else:
        sleep_time += settings['tr_start']
    if rain:
        sleep_time -= settings['bus_time']
    else:
        sleep_time -= settings['bike_time']
    log.write('Sleeping for %d minutes\n' % sleep_time)
    return sleep_time * 60 # convert to seconds for time.sleep

# plays the alarm tone
def ring():
    tone_path = os.path.join(os.path.abspath(os.sep), 'usr', 'share', 'stay-dry', 'tones', settings['tone'] + '.wav')
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
    else:
        log.write('Error: no compatible player found in config file.\n')

            
if __name__ == '__main__':
    logfile = os.path.join(os.path.expanduser('~'), '.local', 'share', 'stay-dry', 'logs', time.strftime("%m-%d-%Y"))
    log = open(logfile, 'w')
    log.write(time.strftime('%A, %B %d, %Y') + '\n')
    settings = read_config()
    weekday = datetime.datetime.today().weekday()
    if weekday < 5: # monday - friday
        time.sleep(get_sleep_time(weekday % 2 == 0, will_it_rain()))
        ring()
    log.close()
