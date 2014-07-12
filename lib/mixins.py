import requests
import json
import ConfigParser
import smtplib
from email.mime.text import MIMEText


class NotificationMixin(object):

    def notify_by_email(self, email_to=[], email_from=None, body=None):

        msg = MIMEText(body, 'plain')
        msg['Subject'] = body
        msg['From'] = email_from
        msg['To'] = email_to

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()

        server.login(self.gmail_user, self.gmail_password)

        server.sendmail(self.email_from, self.email_to, msg.as_string())


class LocalConfigMixin(object):
    """ Loads settings from the local config
        file """

    local_config_file = '/etc/veggiebot.conf'
    local_config_loaded = False

    def load_config(self, force=True):

        if self.local_config_loaded:
            return

        local_config = ConfigParser.ConfigParser()

        local_config.read(self.local_config_file)

        options = local_config.items('PARSE_CREDENTIALS')

        for k, v in options:
            setattr(self, k, v)

        self.local_config_loaded = True


class ParseDataMixin(LocalConfigMixin):
    """ A mixin for sending and retrieving data
        from parse.com """

    data_file = None
    endpoint = None
    parse_classname = None

    def __init__(self, *args, **kwargs):
        self.load_config()

        self.parse_headers = {
            "X-Parse-Application-Id": self.parse_application_id,
            "X-Parse-REST-API-Key": self.parse_api_key,
            "Content-Type": "application/json",
        }

        super(ParseDataMixin, self).__init__(*args, **kwargs)

    def get_data(self, payload={}):

        resp = requests.get(self.get_parse_endpoint(),
                            headers=self.parse_headers, params=payload)

        return resp.json()

    def save_data(self, data):

        return requests.post(self.get_parse_endpoint(),
                      data=json.dumps(data),
                      headers=self.parse_headers)

    def update_object(self, object_id, data):
        """ Updates an existing Parse.com object """

        endpoint = '/'.join([self.get_parse_endpoint(), object_id])

        return requests.put(endpoint,
                            data=json.dumps(data),
                            headers=self.parse_headers)


    def get_parse_endpoint(self):

        return 'https://api.parse.com/1/classes/%s' % self.parse_classname
