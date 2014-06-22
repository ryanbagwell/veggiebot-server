from lib.garden import Garden, Pin, Settings
import datetime
import os
import sys
import random
import xively
import requests
import json

def speak(message):

    gender = random.choice(['m','f',])
    variant = random.choice(range(1,7))

    voice = "-ven-us+%s%s" % (gender, variant)

    cmd = "espeak '%s' -s 160 %s" % (message, voice)
    os.system(cmd)

garden = Garden()

""" Read the moisture level """

moisture_reading = garden.sample_mcp3008(channel_num=0)
temperature = garden.sample_mcp3008(channel_num=1)

moisture = moisture_reading / 1023.0 * 100.0

celsius = (temperature * 330) / 1023.0 - 50

fahrenheit = (celsius * 9.0 / 5.0) + 32.0;

print "Moisture: %s" % moisture
print "Temperature: %s" % fahrenheit

settings = Settings()

pin = Pin(17)

if settings.pumpStatus == 'on':
    pin.off() #Off completes the circuit

if settings.pumpStatus == 'off':
    pin.on() #On opens the cirtuit

if settings.pumpStatus == 'auto':
    
    if moisture_reading < settings.autoThreshold - 50:
        pin.off()

    elif moisture_reading > settings.autoThreshold + 50:
        pin.on()


moisture_volts = (moisture_reading * 3.3) / 1024
moisture_ohms = ((1/moisture_volts)*3300)-1000
moisture_kiloohms = moisture_ohms / 1000

print "Volts: %s" % moisture_volts
print "Ohms: %s" % moisture_ohms
print "Kiloohms: %s " % moisture_kiloohms 

""" Stop here if we're not in 30-minute intervals 
    so we don't log the data """
minute = datetime.datetime.now().minute

if minute not in [0, 30]:
    sys.exit()

""" Send it to parse.com """

parse_headers = {
    "X-Parse-Application-Id": "9NGEXKBz0x7p5SVPPXMbvMqDymXN5qCf387GpOE2",
    "X-Parse-REST-API-Key": "SDWvYNwDCPB6ImJ6eo1L28Nr5fzrA4fQysIdjz4Y",
    "Content-Type": "application/json",
}

payload = {
    'moistureLevel': moisture,
    'moistureReading': moisture_reading,
    'moistureVolts': moisture_volts,
    'moistureOhms': moisture_ohms,
    'moistureKOhms': moisture_kiloohms,
    'temperature': fahrenheit,
}

garden.save_data(payload)





