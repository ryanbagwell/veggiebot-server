from lib.devices import MoistureSensor
from lib.utils import get_kpa, get_volts, get_resistance
import time

sensor = MoistureSensor()

while True:

    moisture_reading = sensor.get_moisture()

    moisture_volts = get_volts(moisture_reading)

    moisture_ohms = get_resistance(moisture_volts, 0.0004514711929179567)

    moisture_kiloohms = moisture_ohms / 1000

    time.sleep(1)

    celsius = sensor.get_temperature()

    kpa = get_kpa(moisture_kiloohms, celsius)

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0

    output = [
        'Reading %s' % moisture_reading,
        'Voltage %s' % moisture_volts,
        'Ohms %s' % moisture_ohms,
        'kOhms %s' % moisture_kiloohms,
        'kPa %s' % kpa,
    ]

    print ' | '.join(output)

    time.sleep(1)
