#!/usr/bin/env python

from datetime import datetime, timedelta
from dateutil.parser import parse
from json import load, loads
from os.path import expanduser, isfile, join
from subprocess import run
from time import sleep
from urllib.request import urlopen
import logging


API_URL = 'https://api.darksky.net/forecast'
API_KEY = '7b74f3837ab0f63bfb389ee1a45e7295'
DATA_DIR = join(expanduser('~'), '.stay-dry')

logging.basicConfig(
    filename=join(DATA_DIR, 'logs', '%s.log' % str(datetime.today())[:10]),
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%I:%M:%S %p',
)

def read_config():
    """Read a JSON config file and return a dict."""
    cfg = join(DATA_DIR, 'config.json')
    if not isfile(cfg):
        logging.critical('No config file found: Exiting.')
        quit()

    with open(cfg) as f:
        settings = load(f)
    settings['mwf_bus'] = parse(settings['mwf_bus'])
    settings['tr_bus'] = parse(settings['tr_bus'])
    settings['mwf_bike'] = parse(settings['mwf_bike'])
    settings['tr_bike'] = parse(settings['tr_bike'])

    # Sanity checks.
    if settings['timeout'] < 0:
        settings['timeout'] = 300
    if settings['threshold'] < 0 or settings['threshold'] > 100:
        settings['threshold'] = 40

    return settings


def will_it_rain():
    """Get the forecast and return whether or not it is likely to rain."""
    url = '/'.join((API_URL, API_KEY, settings['location']))
    weather = loads(urlopen(url).read().decode('utf-8'))
    # If it's raining now, the roads are going to be shitty.
    # If it's going to rain during a commute, everything is  shitty.
    rain_now = weather['currently']['precipProbability']
    # Assuming a one-hour prep time - should be configurable.
    rain_later = weather['hourly']['data'][1]['precipProbability']
    # Assuming an eight-hour school day - should be configurable.
    rain_later_later = weather['hourly']['data'][9]['precipProbability']

    rain = (
        rain_now > settings['threshold'] / 100 or
        rain_later > settings['threshold'] / 100 or
        rain_later_later > settings['threshold'] / 100
    )
    logging.info('It\'s %sgoing to rain.\n' % ('' if rain else 'not '))
    return rain


def get_delta(rain):
    """
    Return the timedelta between now and wake up time.
    Note: this will only work if it's run after midnight,
      i.e. on the same day that the alarm will ring.
    """
    if datetime.today().weekday() % 2 == 0:  # MWF.
        if rain:
            sleep_delta = settings['mwf_bus'] - datetime.now()
        else:
            sleep_delta = settings['mwf_bike'] - datetime.now()
    else:  # TR.
        if rain:
            sleep_delta = settings['tr_bus'] - datetime.now()
        else:
            sleep_delta = settings['tr_bike'] - datetime.now()

    return sleep_delta


def ring():
    """Play the alarm."""
    tone = join(DATA_DIR, 'tones', settings['tone'])
    if not isfile(tone):
        tone = join(DATA_DIR, 'tones', 'helium.wav')
    run(
        ['mpv', tone, '--vo', 'null', '--loop-file'],
        timeout=settings['timeout']
    )


if __name__ == '__main__':
    # weekday = datetime.today().weekday()
    # if weekday > 4:
    #     logging.info('It\'s not a weekday.\n')
    #     quit()
    settings = read_config()
    # key = 'mwf_' if weekday % 2 == 0 else 'tr_'
    # early, late = sorted((settings[key + 'bus'], settings[key + 'bike']))
    # delta = early - datetime.now() - timedelta(minutes=5)
    # logging.info('Sleeping for %s...\n' % delta)
    # sleep(delta.total_seconds())
    # delta = get_delta(will_it_rain())
    # logging.info('Sleeping for %s...\n' % delta)
    # sleep(delta.total_seconds())
    logging.info('Time to wake up.\n')
    ring()
