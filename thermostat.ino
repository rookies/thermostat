#include <RCSwitch.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "Config.hh"

RCSwitch rcSwitch;
OneWire ow(sensorPin);
DallasTemperature sensors(&ow);
bool turnedOn = false;

const byte commandMaxLength = 15;
char command[commandMaxLength+1];
byte commandLength = 0;

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
  /* Check for new data on the serial bus: */
  while (Serial.available() > 0) {
    char chr = Serial.read();
    if (chr != '\n' && chr != '\r' && commandLength < commandMaxLength) {
      if (chr == 'x') {
        /* Abort command: */
        command[commandLength] = '\0';
        commandLength = 0;
        Serial.print(F("INFO: Aborted command '"));
        Serial.print(command);
        Serial.println(F("'."));
      } else {
        /* Append received char to the command: */
        command[commandLength] = chr;
        commandLength++;
      }
    } else {
      /* Command received, parse it: */
      command[commandLength] = '\0';
      commandLength = 0;
      char *comma = strchr(command, ',');
      if (comma) {
        *comma = '\0';
        lowerBound = atoi(command) / 100.;
        upperBound = atoi(comma + 1) / 100.;
        Serial.print(F("INFO: Set bounds to: "));
        Serial.print(lowerBound);
        Serial.print(F(","));
        Serial.println(upperBound);
      } else {
        /* Invalid command. */
        Serial.print(F("WARNING: Invalid command '"));
        Serial.print(command);
        Serial.println(F("'."));
      }
    }
  }
  /* Check if thermostat is enabled: */
  if (lowerBound < -270 && upperBound < -270) {
    return;
  }
  /* Get the temperature: */
  sensors.requestTemperatures();
  float temp = sensors.getTempCByIndex(0);
  /* Print time & temperature: */
  Serial.print(millis());
  Serial.print(F(","));
  Serial.print(temp);
  Serial.print(F(","));
  Serial.print(lowerBound);
  Serial.print(F(","));
  Serial.print(upperBound);
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
