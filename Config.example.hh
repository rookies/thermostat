#ifndef Config_hh
#define Config_hh

/* Lower and upper temperature bound: */
const float lowerBound = 40;
const float upperBound = 50;

/* Interval to check the temperature: */
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
