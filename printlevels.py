from lib.garden import Garden
import time

garden = Garden()

while True:

    moisture = garden.sample_mcp3008(channel_num=0)
    
    time.sleep(1)
    
    reading = garden.sample_mcp3008(channel_num=1)

    celsius = (reading * 330) / 1023.0 - 50

    #volts = reading * 3.3 / 1023.0

    #mv = volts * 1000

    #celsius = 

    fahrenheit = (celsius * 9.0 / 5.0) + 32.0;

    print "Moisture: %s; Temp: %s;" % (moisture, fahrenheit)
    
    time.sleep(1)
