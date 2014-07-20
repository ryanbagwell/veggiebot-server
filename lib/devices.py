from .mixins import ParseDataMixin
from .gpio_mixins import ADCMixin, ResistanceFromCapacitorMixin
import time
import datetime
import dateutil.parser
import RPi.GPIO as GPIO
import pytz


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class SoilData(ParseDataMixin):
    """ A class to save and retrieve soil data
        to/from Parse.com """

    parse_classname = 'SoilData'


class Flow(SoilData):
    """ A class to send and retrive flow meter data
        to/from Parse.com """

    counter = 0
    pin = 0
    data_file = '/var/local/flow-data.json'

    def __init__(self, pin):

        self.pin = pin

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


class MoistureSensor(ResistanceFromCapacitorMixin, ADCMixin, SoilData):
    """ This class consists of mixins that will
        read the Moisture sensor data from the mcp3008, and save it to
        parse.com """

    """ Define the pins for our sensors """
    resistance_supply_pin = 22
    resistance_dischange_pin = 4
    temperature_adc_channel = 0

    def __init__(self, *args, **kwargs):
        super(MoistureSensor, self).__init__(*args, **kwargs)
        super(SoilData, self).__init__(*args, **kwargs)

        """ Initially, set the last_saved attribute """
        latest_data = self.get_latest_data()
        last_saved = latest_data['results'][0]['createdAt']
        self.last_saved = dateutil.parser.parse(last_saved)

    def get_moisture(self):

        ohms = self.sample_resistance_from_capacitance()

        return ohms

    def get_temperature(self, fahrenheit=False):

        self.setup()

        reading = self.sample(channel_num=self.temperature_adc_channel)

        """ Convert the value to voltage, then to celsius """
        celsius = (reading * 330.0) / 1023.0 - 50.0

        """ Convert it to farenheit if needed """
        if fahrenheit:
            return (celsius * 9.0 / 5.0) + 32.0

        return celsius

    def save_data(self, payload):

        self.last_saved = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)

        super(MoistureSensor, self).save_data(payload)

    def get_results(self):
        """ Gets the results of both temperature and moisture """

        moisture = self.get_moisture()

        temp = self.get_temperature()

        return moisture, temp

    def get_latest_data(self, interval=30):

        params = {
            'order': '-createdAt',
            'limit': 1,
        }

        return self.get_data(payload=params)

