#!/usr/bin/python3
import re, sys
from matplotlib import pyplot

times, values, heater = [], [], []
first = True
with open(sys.argv[1], 'r') as f:
    for l in f:
        if re.match(r'^[0-9]+,[0-9]+\.[0-9]+,[A-Z]+$', l) is not None:
            if first:
                first = False
                # Skip first value, it may be corrupted.
            else:
                parts = l.split(',')
                time = float(parts[0]) / 1000
                times.append(time)
                val = float(parts[1])
                values.append(val)
                if parts[2].find('ON') != -1:
                    heater.append(1)
                else:
                    heater.append(0)

f, (a0, a1) = pyplot.subplots(2, 1, gridspec_kw = {'height_ratios':[3,1]})
a0.plot(times, values)
a0.grid(which='both')
a0.set_xlabel('time (seconds)')
a0.set_ylabel('temperature (centigrade)')

a1.plot(times, heater)
a1.grid(which='both')
a1.set_xlabel('time (seconds)')
a1.set_ylabel('heater')

f.tight_layout()
pyplot.show()
