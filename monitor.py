from lib.garden import Garden, Pin
import datetime
import os
import sys
import random
import xively
import requests
import json

def speak(message):

    gender = random.choice(['m','f',])
    variant = random.choice(range(1,7))

    voice = "-ven-us+%s%s" % (gender, variant)

    cmd = "espeak '%s' -s 160 %s" % (message, voice)
    os.system(cmd)

garden = Garden()

""" Read the moisture level """

moisture_reading = garden.sample_mcp3008(channel_num=0)
temperature = garden.sample_mcp3008(channel_num=1)

moisture = moisture_reading / 1023.0 * 100.0

celsius = (temperature * 330) / 1023.0 - 50

fahrenheit = (celsius * 9.0 / 5.0) + 32.0;

print "Moisture: %s" % moisture
print "Temperature: %s" % fahrenheit

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


moistureVolts = (moisture_reading * 3.3) / 1024
moistureOhms = ((1/moistureVolts)*3300)-1000
kiloOhms = moistureOhms / 1000

print "Volts: %s" % moistureVolts
print "Ohms: %s" % moistureOhms
print "Kiloohms: %s " % kiloOhms 

""" Formula taken from
    http://jast.modares.ac.ir/pdf_4632_70c1ddfea84e18c2b4fa0cb50bc61af6.html """
normalizedMoisture = 36.1*(kiloOhms/(0.0009*kiloOhms-0.049*celsius+1.68))**-0.156

print "Normalized moisture: %s" % normalizedMoisture

""" Stop here if we're not in 30-minute intervals 
    so we don't log the data """
minute = datetime.datetime.now().minute

if minute not in [0, 30]:
    sys.exit()

""" Send it to parse.com """

parse_headers = {
    "X-Parse-Application-Id": "9NGEXKBz0x7p5SVPPXMbvMqDymXN5qCf387GpOE2",
    "X-Parse-REST-API-Key": "SDWvYNwDCPB6ImJ6eo1L28Nr5fzrA4fQysIdjz4Y",
    "Content-Type": "application/json",
}

payload = {
    'moistureLevel': moisture,
    'normalizedMoisture': normalizedMoisture,
    'temperature': fahrenheit,
}

r = requests.post('https://api.parse.com/1/classes/SoilData', data=json.dumps(payload), headers=parse_headers)


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



