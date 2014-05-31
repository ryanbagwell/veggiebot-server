from lib.garden import Garden
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

sensor1 = garden.sample_mcp3008(channel_num=0)
sensor2 = garden.sample_mcp3008(channel_num=1)

print "Sensor 1: %s" % sensor1
print "Sensor 2: %s" % sensor2

moisture = sensor1

if moisture < garden.moisture_threshold:
    print "Stopping pump ..."
    #result = os.system('insteonic irrigation off')
    #print "Result: %s" % result
    #speak("The garden is good!")
    #garden.notify("Stopped watering the garden. Moisture level: %s." % moisture)

elif moisture > 900:
    pass
    #speak("You need to water the garden")
    #garden.notify("Started watering the garden. Moisture level: %s." % moisture)
    #print os.system('insteonic irrigation on')

""" Stop here if we're not in 30-minute intervals 
    so we don't log the data """
minute = datetime.datetime.now().minute
print minute
if minute not in [0, 30]:
    sys.exit()

""" Get the existing data """
data = garden.get_data()

""" Append the new reading """
data.append({
    'time': datetime.datetime.utcnow().isoformat(),
    'moistureLevel': moisture,
    'sensor1': sensor1,
    'sensor2': sensor2,
    })

""" Limit our data sample to 100 """
if len(data) > 100:
    data = data[-100:]

""" Save the data """
garden.save_data(data)



