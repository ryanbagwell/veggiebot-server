from lib.devices import Pin, MoistureSensor
from lib.utils import get_kpa
from lib.settings import Settings
import datetime
import os
import random
from time import sleep
import thread
import pytz
import logging

logging.addLevelName(25, 'VeggieBotInfo')

log_format = '%(levelname)s: %(asctime)s %(message)s'

logger = logging.getLogger('Veggiebot')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_format))

file_handler = logging.FileHandler('/var/log/veggiebot.log')
file_handler.setLevel(25)
file_handler.setFormatter(logging.Formatter(log_format))

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.log(25, "Starting monitor")

moisture_sensor = MoistureSensor()


def read_values():

    """ Read the moisture level """

    celsius = moisture_sensor.get_temperature()

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0

    moisture_ohms = moisture_sensor.get_moisture()

    moisture_kiloohms = moisture_ohms / 1000.0

    kpa = get_kpa(moisture_kiloohms, celsius)

    """ Field capacity is about -30 kPa, except
        in the case of sandy soils, which is -10 kPa """

    available_water = -30 - -1500

    remaining_available = ((available_water - (kpa * -1)) / available_water) * 100

    return {
        'moistureLevel': remaining_available,
        'moistureReading': 0,
        'moistureVolts': 0,
        'moistureOhms': moisture_ohms,
        'moistureKOhms': moisture_kiloohms,
        'temperature': fahrenheit,
        'moistureKPa': kpa,
    }


def save_data():

    payload = read_values()

    moisture_sensor.save_data(payload)


def trigger_pump(settings):

    status_change = settings.changed.get('pumpStatus', None)

    if status_change == 'on':
        pin = Pin(17)
        logger.log(25, "Turning pump on ...")
        pin.off() #On opens the circuit
        return

    if status_change == 'off':
        pin = Pin(17)
        logger.log(25, "Turning pump off ...")
        pin.on() #Off completes the circuit
        return

    if settings.pumpStatus == 'auto':

        pin = Pin(17)

        values = read_values()

        if values['moistureLevel'] < settings.autoThreshold - 50:
            pin.off()

        elif values['moistureLevel'] > settings.autoThreshold + 50:
            pin.on()


settings = Settings()

while True:

    sleep(1)

    try:
        settings.refresh()
    except Exception as e:
        logger.warning("Couldn't refresh settings. Exception: %s" % e)

    trigger_pump(settings)

    since_last_saved = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - moisture_sensor.last_saved

    minutes_since_last_saved = float(since_last_saved.seconds / 60.0)

    if minutes_since_last_saved >= settings.dataInterval:
        logger.log(25, "Saving data")
        thread.start_new_thread(save_data, ())
