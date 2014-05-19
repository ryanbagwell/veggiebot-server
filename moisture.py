import RPi.GPIO as GPIO
import smtplib
import os
import time
import json
import datetime
from email.mime.text import MIMEText


GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

#
# Moisture plastic level is approx. 550
#



class Moisture(object):

    moisture_threshold = 600
	
	# change these as desired - they're the pins connected from the
    # SPI port on the ADC to the Cobbler
    mcp_clk = 18
    mcp_miso = 23
    mcp_mosi = 24
    mcp_cs = 25

    email_to = 'ryan@ryanbagwell.com'
    email_from = 'ryan@ryanbagwell.com'
    previous_value_file = '/home/rmb185/garden_script/garden-data.json'

    def __init__(self):
    	
		""" Set the pins for the mcp3008 """
		GPIO.setup(self.mcp_mosi, GPIO.OUT)
		GPIO.setup(self.mcp_miso, GPIO.IN)
		GPIO.setup(self.mcp_clk, GPIO.OUT)
		GPIO.setup(self.mcp_cs, GPIO.OUT)

    def read_mcp3008(self, channel_num=None):
        """ Read the value of the given channel number from the mcp3008 """
        
        if channel_num is None:
            raise ValueError('Please supply a channel number.')

        """ Send True to the cs pin """
        GPIO.output(self.mcp_cs, True)
 
        """ Send False to the clock pin,
            which starts the clock at low """
        GPIO.output(self.mcp_clk, False)

        """ Set the cs pin to low """
        GPIO.output(self.mcp_cs, False)

        """ Compile the command to send so we get
            back our data """
        commandout = channel_num
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here

        for i in range(5):
            if (commandout & 0x80):
                GPIO.output(self.mcp_mosi, True)
            else:
                GPIO.output(self.mcp_mosi, False)
            
            commandout <<= 1
            GPIO.output(self.mcp_clk, True)
            GPIO.output(self.mcp_clk, False)

        adcout = 0

        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(self.mcp_clk, True)
            GPIO.output(self.mcp_clk, False)
            adcout <<= 1
            if (GPIO.input(self.mcp_miso)):
                adcout |= 0x1
 
        GPIO.output(self.mcp_cs, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout


    def get_data(self):
    
        try:
            data = open(self.previous_value_file, "r").read()
            if data == '': data = '[]'
        except:
            data = '[]'
        
        return json.loads(data)

    def save_data(self, data):

        f = open(self.previous_value_file, 'w')
        f.write(json.dumps(data))
        f.close()
 
    def check_moisture(self):

        new_val = self.read_mcp3008(channel_num=0)

        print new_val

        data = self.get_data()

        data.append({
            'time': datetime.datetime.utcnow().isoformat(),
            'moistureLevel': new_val,
            })

        """ Limit our data sample to 60 """
        if len(data) > 100:
            data = data[-50:]

        self.save_data(data)

        """ Stop if our sample size is less than 10 """
        if len(data) < 10: return

        """ Check all the values to be sure they're 
            under our threshold """

        samples = [s for s in data[-10:] if s['moistureLevel'] < self.moisture_threshold]
        
        """ If any of the last 10 samples are below
            the threshold, don't do anything """

        return 
    
        if len(samples) > 0:
            os.system('insteonic irrigation off')
        else:
            os.system('insteonic irrigation on') 
        
        return
          
                
        """ Send an email notification """
        if new_val == 0:
            self.notify("You've watered the garden enough.")
        else:
            self.notify("You need to water the garden.")            

    def notify(self, body):

        msg = MIMEText(body, 'plain')
        msg['Subject'] = body
        msg['From'] = self.email_from
        msg['To'] = self.email_to

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login('ryan@ryanbagwell.com', 'Muckraker1120')
        server.sendmail(self.email_from, self.email_to, msg.as_string())


moisture = Moisture()
moisture.check_moisture()
