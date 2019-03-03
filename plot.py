#!/usr/bin/python3
import re, sys, time, argparse
from matplotlib import pyplot

def parseLine(l):
    global first, times, values, heater, lowerBound, upperBound
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
    elif re.match(r'^[0-9]+,[0-9]+\.[0-9]+,[0-9]+\.[0-9]+,[0-9]+\.[0-9]+,[A-Z]+$', l) is not None:
        if first:
            first = False
            # Skip first value, it may be corrupted.
        else:
            parts = l.split(',')
            time = float(parts[0]) / 1000
            times.append(time)
            val = float(parts[1])
            values.append(val)
            low = float(parts[2])
            lowerBound.append(low)
            up = float(parts[3])
            upperBound.append(up)
            if parts[4].find('ON') != -1:
                heater.append(1)
            else:
                heater.append(0)

def plot(a0, a1):
    global times, values, heater, lowerBound, upperBound
    a0.plot(times,values)
    if len(lowerBound) > 0:
        a0.plot(times, lowerBound)
        a0.plot(times, upperBound)
    a0.grid(which='both')
    a0.set_xlabel('time (seconds)')
    a0.set_ylabel('temperature (centigrade)')

    a1.plot(times, heater)
    a1.grid(which='both')
    a1.set_xlabel('time (seconds)')
    a1.set_ylabel('heater')

parser = argparse.ArgumentParser(description='Plot thermostat data.')
parser.add_argument('file', type=str, help='the thermostat log file')
parser.add_argument('--live', action='store_true', help='update the plot when new data is written to the log file')
args = parser.parse_args()

times, values, heater, lowerBound, upperBound = [], [], [], [], []
first = True
lines = 0
with open(args.file, 'r') as f:
    for l in f:
        parseLine(l)
        lines += 1

f, (a0, a1) = pyplot.subplots(2, 1, gridspec_kw = {'height_ratios':[3,1]})
plot(a0, a1)

f.tight_layout()

if args.live:
    pyplot.draw()
    pyplot.pause(.01)
    with open(args.file, 'r') as f:
        for _ in range(lines):
            f.readline()
        while True:
            l = f.readline()
            if not l:
                time.sleep(1)
            else:
                parseLine(l)
                a0.clear()
                a1.clear()
                plot(a0, a1)
                pyplot.draw()
                pyplot.pause(.01)
else:
    pyplot.show()
