from lib.garden import Garden
import time

garden = Garden()

while True:

    moisture = garden.sample_mcp3008(channel_num=0)
    
    time.sleep(1)
    
    volts = garden.sample_mcp3008(channel_num=1)

    millivolts = volts * (3300 / 1024)

    celsius = (millivolts - 500) / 10

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0;

    print "Moisture: %s; Temp: %s;" % (moisture, fahrenheit)
    
    time.sleep(1)
