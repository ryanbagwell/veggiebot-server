from lib.devices import MoistureSensor
import time

moisture_sensor = MoistureSensor()

while True:

    moisture = moisture_sensor.get_moisture()

    time.sleep(1)
   
    temp = moisture_sensor.get_temperature(fahrenheit=False)

    print "Moisture: %s; Temp: %s;" % (moisture, temp)
    
    time.sleep(1)
