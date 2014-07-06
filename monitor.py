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


def get_kpa(kohms, celsius):
    """ Conversion equations taken from
        http://www.kimberly.uidaho.edu/water/swm/calibration_watermark2.pdf """

    if kohms < 1:
        kpa = -20 * (kohms * (1 + 0.018 * (celsius - 24)) - 0.55)

    elif 1 < kohms < 8:
        kpa = (-3.213 * kohms - 4.093) / (1 - 0.009733 * kohms - 0.01205 * celsius)
    else:
        kpa = -2.246 - 5.239 * kohms * (1 + 0.018 * (celsius - 24)) - (0.06756**2) * (1 + 0.018 * (celsius - 24))**2

    return kpa




def read_values():

    """ Read the moisture level """

    moisture_reading = garden.sample_mcp3008(channel_num=0)
    temperature = garden.sample_mcp3008(channel_num=1)

    moisture = moisture_reading / 1023.0 * 100.0

    celsius = (temperature * 330) / 1023.0 - 50

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0;

    moisture_volts = (moisture_reading * 3.3) / 1024
    moisture_ohms = moisture_volts / 0.0004514711929179567
    moisture_kiloohms = moisture_ohms / 1000

    kpa = get_kpa(moisture_kiloohms, celsius)

    """ Field capacity is about -30 kPa, except
        in the case of sandy soils, which is -10 kPa """
    
    available_water = -30 - -1500

    remaining_available = ((available_water - (kpa * -1)) / available_water) * 100

    return {
        'moistureLevel': remaining_available,
        'moistureReading': moisture_reading,
        'moistureVolts': moisture_volts,
        'moistureOhms': moisture_ohms,
        'moistureKOhms': moisture_kiloohms,
        'temperature': fahrenheit,
        'moistureKPa': kpa,
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

    settings.get_data()

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

print read_values()
while True:

    sleep(1)
 
    thread.start_new_thread(trigger_pump,  (settings,))

    thread.start_new_thread(save_data, (settings,))
