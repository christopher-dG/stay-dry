# Stay Dry
A weather-based morning alarm to avoid cycling in the rain  

Stay Dry checks the day's forecast with the Dark Sky API to determine whether or not it will rain during my commutes.

# Options
- player: media player used for the alarm (mpv or mplayer)
- tone: alarm tone (choose from the tones folder, don't include extension)
- alarm_timeout: how long to run the alarm for (seconds)
- location: coordinates for the API (get these from darksky.net)
- threshold: maximum chance of rain to ignore (0-100)
- prep_time: time to get ready to leave in the morning (minutes)
- bike_time: time to bike to school, shower, etc. (minutes)
- bus_time: time to bus to school (minutes)
- run_time: time to run the script (a:bc)
- mwf_start: class start time on mwf (a:bc)
- tr_start: class start time on tr (a:bc)
- cushion: time to spare before class starts after arriving (minutes)

# Dependencies
Stay Dry needs either mpv or mplayer to play the alarm.

# Installation
Just run `install.sh` to install, files are kept in `~/.local/share/stay-dry` and `~/.config/stay-dry`.
Run `uninstall.sh` to uninstall, or simply delete the aforementioned folders.

# Usage
Scheduling a cron job to run `stay_dry.py` every morning is recommended, make sure that the time in your crontab and `run_time` in your config match.

# Custom tones
You can add anything you want to the tones directory either before installing, or later in `~/.local/share/stay-dry/tones`, make sure they end with `.wav`, or edit the code to deal with this.
