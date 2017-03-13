from datetime import datetime, timedelta
from dateutil.parser import parse
from json import load, loads
from os.path import expanduser, isfile, join
from subprocess import run
from time import sleep
from urllib.request import urlopen


API_URL = 'https://api.darksky.net/forecast'
API_KEY = '7b74f3837ab0f63bfb389ee1a45e7295'
DATA_DIR = join(expanduser('~'), '.stay-dry')


def read_config():
    """Read a JSON config file and return a dict."""
    cfg = join(DATA_DIR, 'config.json')
    if not isfile(cfg):
        with open('error.log', 'w') as f:
            write(f, 'No config file found: Exiting.')
        quit()

    with open(cfg) as f:
        settings = load(f)

    # Sanity checks.
    if settings['timeout'] < 0:
        settings['timeout'] = 120
    if settings['threshold'] < 0 or settings['threshold'] > 100:
        settings['threshold'] = 40

    return settings


def get_delta(bike, bus):
    """
    Check the weather, decide on a transporation method,
    and calculate the timedelta between now and wake up time.
    Should be run within a few minutes of the earliest alarm.
    Note: this will only work if it's run after midnight,
      i.e. on the same day that the alarm will ring.

    Arguments:
    bike, bus: alarm datetimes for cycling and bussing respectively.

    Returns: timedelta between now and wake up time.
    """
    url = '/'.join((API_URL, API_KEY, settings['location']))

    try:
        weather = loads(urlopen(url).read().decode('utf-8'))
    except:
        write(
            log,
            'Fetching data from API failed.\nFalling back to earliest alarm.'
        )
        key = 'mwf_' if datetime.now().weekday % 2 == 0 else 'tr_'
        # Make the alarm ring at the earlier time.
        rain = settings[key + 'bus'] < settings[key + 'bike']
    else:
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
        write(log, 'It\'s %sgoing to rain.' % ('' if rain else 'not '))

    if rain:
        sleep_delta = bus - datetime.now()
    else:
        sleep_delta = bike - datetime.now()

    return sleep_delta


def ring():
    """Play the alarm."""
    tone = join(DATA_DIR, 'tones', settings['tone'])
    if not isfile(tone):
        tone = join(DATA_DIR, 'tones', 'helium.wav')
    run(['mpv', tone, '--loop-file'], timeout=settings['timeout'])


def write(f, msg):
    """
    Write a log message to a file.

    Arguments:
    f: File handle.
    msg: Log message.
    """
    f.write('%s: %s\n' % (datetime.now().strftime('%I:%M %p'), msg))


# --------------- Actual script starts here --------------- #

settings = read_config()
# Sleep until 03:00 for the first run.
start = datetime.now().replace(hour=3, minute=0, microsecond=0)
if datetime.now().hour >= 3:
    start += timedelta(days=1)
delta = start - datetime.now()
with open('start.log', 'w') as f:
    write(f, 'Sleeping for %s.' % delta)
sleep(delta.total_seconds())

# Ideally this would run once per day rather than continuously,
# but cron is not cooperating.
while True:
    # This line should be reached at 03:00 every day.
    log = open(
        join(
            DATA_DIR, 'logs', '%s.log' %
            datetime.now().strftime('%m-%d-%Y')
        ),
        'w'
    )

    weekday = datetime.now().weekday()
    if weekday > 4:
        # On weekends, sleep until the next day.
        write(log, 'It\'s not a weekday.')
        log.close()
        sleep(timedelta(days=1).total_seconds())
        continue

    # Refresh these every day so that the date is updated.
    mwf = (
        parse(settings['mwf_bike']),
        parse(settings['mwf_bus'])
    )
    tr = (
        parse(settings['tr_bike']),
        parse(settings['tr_bus'])
    )

    day = mwf if weekday % 2 == 0 else tr
    early = min(day)

    # Wait until 5 minutes before the earliest alarm to check the weather.
    delta = early - datetime.now() - timedelta(minutes=5)
    write(log, 'Sleeping for %s before making prediction.' % delta)
    sleep(delta.total_seconds())

    delta = get_delta(*day)
    write(log, 'Sleeping for %s.' % delta)
    sleep(delta.total_seconds())

    write(log, 'Time to wake up.')
    ring()

    delta = (datetime.now() + timedelta(days=1)).replace(
        hour=3, minute=0, microsecond=0
    ) - datetime.now()
    write(log, 'Sleeping for %s.' % delta)
    sleep(delta.total_seconds())

    log.close()
