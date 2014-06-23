from lib.garden import Garden, Pin, Settings
import datetime
import os
import sys
import random
import xively
import requests
import json
from time import sleep
import thread

def speak(message):

    gender = random.choice(['m','f',])
    variant = random.choice(range(1,7))

    voice = "-ven-us+%s%s" % (gender, variant)

    cmd = "espeak '%s' -s 160 %s" % (message, voice)
    os.system(cmd)





garden = Garden()




def read_values():

    """ Read the moisture level """

    moisture_reading = garden.sample_mcp3008(channel_num=0)
    temperature = garden.sample_mcp3008(channel_num=1)

    moisture = moisture_reading / 1023.0 * 100.0

    celsius = (temperature * 330) / 1023.0 - 50

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0;

    moisture_volts = (moisture_reading * 3.3) / 1024
    moisture_ohms = ((1/moisture_volts)*3300)-1000
    moisture_kiloohms = moisture_ohms / 1000

    return {
        'moistureLevel': moisture,
        'moistureReading': moisture_reading,
        'moistureVolts': moisture_volts,
        'moistureOhms': moisture_ohms,
        'moistureKOhms': moisture_kiloohms,
        'temperature': fahrenheit,
    }


def save_data(settings):

    """ Only log our data every 30 minutes """
    if datetime.datetime.now().minute in [0, 30] and datetime.datetime.now().second is 0:

        print "Saving data"

        payload = read_values()

        print payload
   
        garden.save_data(payload)


def trigger_pump(settings):

    pin = Pin(17)

    if settings.changed.get('pumpStatus', None):
        
        if settings.pumpStatus == 'on':
            print "Turning pump on ..."
            pin.off() #Off completes the circuit
            return

        elif settings.pumpStatus == 'off':
            print "Turning pump off ..."
            pin.on() #On opens the cirtuit
            return

    else: 

        values = read_values()

        if settings.pumpStatus == 'auto':
        
            if values['moistureReading'] < settings.autoThreshold - 50:
                pin.off()

            elif values['moistureReading'] > settings.autoThreshold + 50:
                pin.on()

settings = Settings()


while True:

    sleep(1)
    
    thread.start_new_thread(trigger_pump,  (settings,))

    thread.start_new_thread(save_data, (settings,))