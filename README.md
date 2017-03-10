# Stay Dry

Stay Dry is a weather-based morning alarm for active commuters that wakes you up at the right time, no matter how you're commuting. It checks the day's forecast to determine whether or not it will rain during your commutes, decides whether you should cycle or take the bus, and sets your morning alarm accordingly.

### Dependencies

- `mpv`

### Installation

`git clone https://christopher-dg/stay-dry`
`cd stay-dry`
`mkdir ~/.stay-dry`
`cp -r tones config.json stay_dry.py ~/.stay-dry`

Some stuff about crontabs here

### Options

Options are found in `~/.stay-dry/config.json`
- `tone`: alarm tone (choose from the `tones` folder, include the extension)
- `timeout`: how long to run the alarm for (seconds)
- `threshold`: maximum chance of rain in which to cycle (0-100)
- `location`: coordinates of your location
- `mwf_bus`: time to wake up when bussing on MWF (hh:mm)
- `tr_bus`: time to wake up when bussing  on TR (hh:mm)
- `mwf_bike`: time to wake up when cycling on MWF (hh:mm)
- `tr_bike`: time to wake up when cycling  on TR (hh:mm)
