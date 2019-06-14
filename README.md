
# Python library for controlling TestEquity TE series Temperature Chambers <!-- omit in toc -->

This is a library that (partially) implements the SCPI based interface of the Watlow controllers used by the TestEquity TE series of Environmental chamber. 

## Table of Contents  <!-- omit in toc -->
- [Requirements:](#requirements)
- [Usage:](#usage)
- [Example Usage:](#example-usage)
- [TODO:](#todo)

## Requirements:

- Python 3+
  
This library only uses built-in python libraries.

## Usage: 
1. Install [Python](https://www.python.org/downloads/)
2. Install [Git](https://git-scm.com/downloads)
   - Ensure to add git to your `PATH` if it is not already.
3. Clone this repository:
   - `git clone https://github.com/an-oreo/te107_control`
4. Ensure to include the file `f4t_control.py` in your project to use. 
5. In the file you intend ot use this, ensure to `import f4t_control` 

## Example Usage:
```python
from time import sleep
from f4t_control import (F4TController, RampScale, TempUnits)

# setup a temperature sweep
temp_units = TempUnits['C']
start = -40
stop = 125
step = 5
ramp_time_min = 3.0
soak_time_min = 7.0
temps = range(start,stop+step,step)

# instanciate the unit
x = F4TController(host='169.254.250.143',timeout=1)

# configure unit for sweeping temperature
x.set_ramp_time(ramp_time_min)
x.set_ramp_scale(RampScale.MINUTES)
# ensure chamber is enabled:
 x.set_output(1,'ON')
# ensure units 
x.set_units(temp_units)

for temp in temps:
    print('ramping to temperature {}'.format(temp))
    x.set_temperature(temp)
    # wait for ramp time to finish
    sleep(ramp_time_min*60)
    while abs(x.get_temperature() - temp) > 0.2:
        sleep(1.0)
    # begin soak
    print('beginning soak at temp {}'.format(x.get_temperature()))
    sleep(soak_time_min*60)
```

## TODO:
- [ ] More Complete Documentation
- [ ] Examples
- [ ] Quick Diagnostics
- [ ] Tests
- [ ] Package?
- [ ] Contributing?
