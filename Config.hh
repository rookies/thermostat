#ifndef Config_hh
#define Config_hh

/* Default lower and upper temperature bound (centigrade): */
float lowerBound = -300;
float upperBound = -300;
/* NOTE: set both to -300 to disable the thermostat at startup */

/* Interval to check the temperature (ms): */
const unsigned long interval = 2000;

/* Pin configuration: */
const int senderPin = 15;
const int sensorPin = 2;

/* Transmitter configuration: */
const int protocol = 6;
const int pulseLength = 670;
const char *onCmd = "10101000000000010001";
const char *offCmd = "10101000000000000000";

#endif
