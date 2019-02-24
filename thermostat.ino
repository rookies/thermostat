#include <RCSwitch.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "Config.hh"

RCSwitch rcSwitch;
OneWire ow(sensorPin);
DallasTemperature sensors(&ow);
bool turnedOn = false;

void on() {
  rcSwitch.send(onCmd);
}

void off() {
  rcSwitch.send(offCmd);
}

void setup() {
  /* Init the serial port: */
  Serial.begin(86400);
  /* Init the transmitter: */
  rcSwitch.enableTransmit(senderPin);
  rcSwitch.setProtocol(protocol);
  rcSwitch.setPulseLength(pulseLength);
  /* Init the sensor: */
  sensors.begin();
  /* Turn the heater off: */
  off();
}

void loop() {
  /* Remember when we started to calculate the duration: */
  unsigned long start = millis();
  /* Get the temperature: */
  sensors.requestTemperatures();
  float temp = sensors.getTempCByIndex(0);
  /* Print time & temperature: */
  Serial.print(millis());
  Serial.print(F(","));
  Serial.print(temp);
  Serial.print(F(","));
  /* Check what we need to do: */
  if (temp < lowerBound && !turnedOn) {
    /* Switch the heater on. */
    Serial.println(F("SWITCHON"));
    on();
    turnedOn = true;
  } else if (temp > upperBound && turnedOn) {
    /* Switch the heater off. */
    Serial.println(F("SWITCHOFF"));
    off();
    turnedOn = false;
  } else if (turnedOn) {
    /* Keep the heater turned on. */
    Serial.println(F("STAYON"));
    on();
  } else {
    /* Keep the heater turned off. */
    Serial.println(F("STAYOFF"));
    off();
  }
  /* Calculate duration and check if we met our interval: */
  unsigned long duration = millis() - start;
  if (duration < interval) {
    /* We did, sleep for the remaining time: */
    delay(interval - duration);
  } else if (duration > interval) {
    /* We didn't, print a warning: */
    Serial.print(F("WARNING: Interval not met! (interval="));
    Serial.print(interval);
    Serial.print(F("ms, duration="));
    Serial.print(duration);
    Serial.println(F("ms)"));
  }
}
