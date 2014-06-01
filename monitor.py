from lib.garden import Garden, Pin
import datetime
import os
import sys
import random

def speak(message):

    gender = random.choice(['m','f',])
    variant = random.choice(range(1,7))

    voice = "-ven-us+%s%s" % (gender, variant)

    cmd = "espeak '%s' -s 160 %s" % (message, voice)
    print cmd
    os.system(cmd)

garden = Garden()

""" Read the moisture level """

moisture = garden.sample_mcp3008(channel_num=0)
temperature = garden.sample_mcp3008(channel_num=1)

print "Moisture: %s" % moisture
print "Temperature: %s" % temperature

if moisture < 600:
    pin = Pin(17)
    pin.on()

elif moisture > 900:
    pin = Pin(17)
    pin.off()

    #result = os.system('insteonic irrigation off')
    #print "Result: %s" % result
    #speak("The garden is good!")
    #garden.notify("Stopped watering the garden. Moisture level: %s." % moisture)


    
    #speak("You need to water the garden")
    #garden.notify("Started watering the garden. Moisture level: %s." % moisture)
    #print os.system('insteonic irrigation on')

""" Stop here if we're not in 30-minute intervals 
    so we don't log the data """
minute = datetime.datetime.now().minute

if minute not in [0, 30]:
    sys.exit()


celsius = (temperature * 330) / 1023.0 - 50

fahrenheit = (celsius * 9.0 / 5.0) + 32.0;

""" Get the existing data """
data = garden.get_data()

""" Append the new reading """
data.append({
    'time': datetime.datetime.utcnow().isoformat(),
    'moistureLevel': moisture,
    'sensor1': moisture,
    'sensor2': fahrenheit,
    'temperature': fahrenheit
    })

""" Limit our data sample to 100 """
if len(data) > 100:
    data = data[-100:]

""" Save the data """
garden.save_data(data)



