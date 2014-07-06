from .mixins import ADCMixin, ParseDataMixin
import time
import datetime
import RPi.GPIO as GPIO


class SoilData(ParseDataMixin):
    """ A class to save and retrieve soil data
        to/from Parse.com """

    parse_classname = 'SoilData'


class Settings(ParseDataMixin):
    """ A class to load app settings from parse.com """

    parse_classname = 'Settings'
    pumpStatus = 'off'
    autoThreshold = 500
    changed = {}

    def __init__(self, *args, **kwargs):

        super(Settings, self).__init__(*args, **kwargs)

        try:
            self.get_data()

        except Exception as e:
            print e

    def get_data(self):

        q = '{"user":{"$inQuery":{"where":{"email":"%s"},"className":"_User"}}}' % self.parse_user_email

        params = {
            'where': q
        }

        json_data = super(Settings, self).get_data(payload=params)

        for k, v in json_data['results'][0].items():

            if getattr(self, k, None) != v:
                self.changed[k] = v
            else:
                try:
                    self.changed.pop(k, None)
                except:
                    pass

            setattr(self, k, v)

        return json_data


class Flow(SoilData):
    """ A class to send and retrive flow meter data
        to/from Parse.com """

    counter = 0
    pin = 0
    data_file = '/var/local/flow-data.json'

    def __init__(self, pin):

        self.pin = pin

        GPIO.setmode(GPIO.BCM)

        GPIO.setwarnings(False)

        GPIO.setup(pin, GPIO.IN)

        data = self.get_data()

        try:
            self.counter = data['flowCount']
        except:
            pass


    def count(self, pin):
        self.counter = self.counter + 1

        api = xively.XivelyAPIClient('Oc3SqIBJtpfJuZseir2bGfvepJKQq4RPwh7KoEmx3y1rHHcL')

        feed = api.feeds.get(342218851)

        feed.datastreams = [
            xively.Datastream(id='Outflow', current_value=self.counter, at=datetime.datetime.utcnow()),
        ]

        feed.update()


        print self.counter


    def save_data(self):

        data = {
            'flowCount': self.counter,
            'time': datetime.datetime.utcnow().isoformat(),
        }

        super(Flow, self).save_data(data=data)


    def listen(self):

        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.count, bouncetime=0)

        while True:
            self.save_data()
            time.sleep(60)


class Pin(object):
    """ A generic class to turn
        GOIP Pins on or off """

    def __init__(self, pin, mode=GPIO.BCM, warnings=False):
        self.pin = pin

        GPIO.setmode(mode)
        GPIO.setwarnings(warnings)

    def status(self):
        """ Returns the status of the pin """

        return GPIO.input(self.pin)

    def on(self):
        """ Sets a pin to high """

        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, True)

    def off(self):
        """ Sets a pin to low """

        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, False)

    def toggle(self):

        if self.status() == 1:
            self.off()
        else:
            self.on()


class MoistureSensor(ADCMixin, SoilData):
    """ This class consists of mixins that will
        read the Moisture sensor data from the mcp3008, and save it to
        parse.com """

    def __init__(self, *args, **kwargs):
        super(MoistureSensor, self).__init__(*args, **kwargs)

    """ Define the pins for our sensors """
    moisture_power_pin = 22
    temperature_power_pin = 22
    moisture_adc_channel = 0
    temperature_adc_channel = 1

    def setup(self):
        super(MoistureSensor, self).setup()

        GPIO.setup(self.moisture_power_pin, GPIO.OUT)

    def get_moisture(self):

        self.setup()

        """ Give the moisture sensor some power """
        GPIO.output(self.moisture_power_pin, True)

        """ Read the value from the chip """
        moisture = self.read(channel_num=self.moisture_adc_channel)

        """ Shut off power to the sensor """
        GPIO.output(self.moisture_power_pin, False)

        GPIO.cleanup()

        return moisture

    def get_temperature(self, fahrenheit=False):

        self.setup()

        """ Give the temperature sensor some power """
        GPIO.setup(self.temperature_power_pin, GPIO.OUT)
        GPIO.output(self.temperature_power_pin, True)

        reading = self.read(channel_num=self.temperature_adc_channel)

        """ Turn the power off """
        GPIO.output(self.temperature_power_pin, False)

        GPIO.cleanup()

        """ Convert the value to voltage, then to celsius """
        celsius = (reading * 330) / 1023.0 - 50

        """ Convert it to farenheit if needed """
        if fahrenheit:
            return (celsius * 9.0 / 5.0) + 32.0

        return celsius

    def get_results(self):
        """ Gets the results of both temperature and moisture """

        moisture = self.get_moisture()

        temp = self.get_temperature()

        return moisture, temp
