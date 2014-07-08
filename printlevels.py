from lib.devices import MoistureSensor
from lib.utils import get_kpa, get_volts
import time

sensor = MoistureSensor()

while True:

    moisture_reading = sensor.get_moisture()

    moisture_volts = get_volts(moisture_reading)

    moisture_ohms = moisture_volts / 0.0004514711929179567

    moisture_kiloohms = moisture_ohms / 1000

    time.sleep(1)

    celsius = sensor.get_temperature()

    kpa = get_kpa(moisture_kiloohms, celsius)

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0

    print "Moisture: %s kPa; Temp: %s &degF;" % (kpa, fahrenheit)

    time.sleep(1)
