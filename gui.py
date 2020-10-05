#!/usr/bin/env python3
import sys
import threading
import collections
import serial
from matplotlib import pyplot, widgets, gridspec

# TODO: Write logfile.
# TODO: Function to resume from logfile.


class SerialThread(threading.Thread):
    def __init__(self, serialPort, data, lock, *args, **kwargs):
        self._serial = serial.Serial(serialPort, 9600, timeout=1)
        self._data = data
        self._lock = lock

        super().__init__(*args, **kwargs)

    def __del__(self):
        self._serial.close()

    def run(self):
        while True:
            # Check for commands to send:
            with self._lock:
                try:
                    cmd = self._data['commands'].pop(0)
                except IndexError:
                    cmd = None
            if cmd is not None:
                self._serial.write(('\n\n%s\n' % cmd).encode('utf-8'))
                with self._lock:
                    self._data['messages'].append('<< %s' % cmd)

            # Check for lines to receive:
            line = self._serial.readline().decode('utf-8').strip()
            if line == '':
                pass
            elif line.startswith('STATUS:'):
                # STATUS:timestamp,current,lowerLimit,upeerLimit,status
                parts = line[7:].split(',')

                # Parse status:
                if parts[4] == 'SWITCHON' or parts[4] == 'STAYON':
                    textStatus = 'on'
                    status = 1
                elif parts[4] == 'SWITCHOFF' or parts[4] == 'STAYOFF':
                    textStatus = 'off'
                    status = 0
                elif parts[4] == 'DISABLED':
                    textStatus = 'disabled'
                    status = 0
                else:
                    textStatus = 'invalid'
                    status = None

                # Store data:
                with self._lock:
                    self._data['status'] = textStatus
                    limits = float(parts[2]), float(parts[3])
                    if (limits[0] < -270) or (limits[1] < -270):
                        limits = None, None

                    self._data['history'].append((
                        int(parts[0]),    # timestamp
                        float(parts[1]),  # currentTemp
                        limits[0],        # lowerTempLimit
                        limits[1],        # upperTempLimit
                        status,           # status
                    ))
            else:
                # different message
                with self._lock:
                    self._data['messages'].append('>> %s' % line)


class Main:
    def __init__(self, argv):
        self._serialData = {
            'status': 'unknown',
            'history': collections.deque([], 1000),
            'messages': [],
            'commands': [],
        }
        self._serialLock = threading.Lock()
        self._serialThread = SerialThread(
            argv[1], self._serialData, self._serialLock)

        self._lowerLimit = None
        self._upperLimit = None

    def run(self):
        # Start thread for serial communication:
        self._serialThread.start()

        # Initialize plot:
        fig = pyplot.figure()
        gs = gridspec.GridSpec(9, 6, figure=fig)
        ax0 = fig.add_subplot(gs[:6, :])
        ax1 = fig.add_subplot(gs[6:8, :], sharex=ax0)
        ax2 = fig.add_subplot(gs[8, :2])
        ax3 = fig.add_subplot(gs[8, 2:4])
        ax4 = fig.add_subplot(gs[8, 4])
        ax5 = fig.add_subplot(gs[8, 5])
        axs = (ax0, ax1, ax2, ax3, ax4, ax5)
        box1 = widgets.TextBox(axs[2], 'Lower Limit (°C)')
        box1.on_text_change(self._changeLower)
        box2 = widgets.TextBox(axs[3], 'Upper Limit (°C)')
        box2.on_text_change(self._changeUpper)
        submit = widgets.Button(axs[5], 'Set')
        submit.on_clicked(self._setLimits)
        pyplot.ion()
        pyplot.show()

        # Start main loop:
        while True:
            # Check for messages:
            with self._serialLock:
                while True:
                    try:
                        print(self._serialData['messages'].pop(0))
                    except IndexError:
                        break

            # Acquire data:
            with self._serialLock:
                t = [v[0] for v in self._serialData['history']]
                Tc = [v[1] for v in self._serialData['history']]
                Tl = [v[2] for v in self._serialData['history']]
                Th = [v[3] for v in self._serialData['history']]
                Hs = [v[4] for v in self._serialData['history']]

            # Convert time to seconds relative to the last status:
            if len(t) > 0:
                t = [(v - t[-1]) / 1000. for v in t]

            # Clear plots:
            axs[0].clear()
            axs[1].clear()
            axs[4].clear()
            axs[4].axis('off')

            # Plot new data:
            axs[0].plot(t, Tc, c='tab:blue')
            axs[0].plot(t, Tl, c='tab:red')
            axs[0].plot(t, Th, c='tab:red')
            axs[0].set_ylabel('temperature / °C')
            axs[1].plot(t, Hs, c='tab:blue')
            axs[1].set_xlabel('time / s')
            axs[1].set_ylabel('heater')
            axs[1].set_yticks([0, 1])
            axs[1].set_yticklabels(['off', 'on'])

            # Set status:
            with self._serialLock:
                statusText = self._serialData['status']
            if len(t) > 0:
                statusText += ', %s, %s, %s' % (
                    '%.2f' % Tc[-1] if Tc[-1] is not None else '-',
                    '%.2f' % Tl[-1] if Tl[-1] is not None else '-',
                    '%.2f' % Th[-1] if Th[-1] is not None else '-')
            axs[4].text(0, 0, statusText)

            # Draw plots:
            fig.tight_layout()
            fig.canvas.draw_idle()
            fig.canvas.start_event_loop(2)

    def _changeLower(self, text):
        try:
            self._lowerLimit = float(text)
        except ValueError:
            pass

    def _changeUpper(self, text):
        try:
            self._upperLimit = float(text)
        except ValueError:
            pass

    def _setLimits(self, event):
        with self._serialLock:
            self._serialData['commands'].append('%d,%d' % (
                self._lowerLimit * 100, self._upperLimit * 100))


if __name__ == '__main__':
    Main(sys.argv).run()
