from lib.devices import Pin, Settings, MoistureSensor
from lib.utils import get_kpa, get_volts
import datetime
import os
import random
from time import sleep
import thread


def speak(message):

    gender = random.choice(['m','f',])
    variant = random.choice(range(1,7))

    voice = "-ven-us+%s%s" % (gender, variant)

    cmd = "espeak '%s' -s 160 %s" % (message, voice)
    os.system(cmd)


moisture_sensor = MoistureSensor()


def read_values():

    """ Read the moisture level """

    moisture_reading = moisture_sensor.get_moisture()

    celsius = moisture_sensor.get_temperature()

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0

    moisture_volts = get_volts(moisture_reading)

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

        moisture_sensor.save_data(payload)


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
