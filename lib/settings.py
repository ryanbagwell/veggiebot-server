from .mixins import ParseDataMixin


class Settings(ParseDataMixin):
    """ A class to load app settings from parse.com """

    parse_classname = 'Settings'

    defaults = {
        'pumpStatus': 'off',
        'autoThreshold': '500',
    }

    changed = {}

    def __init__(self, *args, **kwargs):

        super(Settings, self).__init__(*args, **kwargs)

        try:
            self.refresh()
        except Exception as e:
            print e

    def get_data(self):

        q = '{"user":{"$inQuery":{"where":{"email":"%s"},"className":"_User"}}}' % self.parse_user_email

        params = {
            'where': q
        }

        return super(Settings, self).get_data(payload=params)

    def refresh(self):
        """ Pulls the latest settings from Parse.com,
            and populates the changed property """

        json_data = self.get_data()

        values = dict(self.defaults.items() + json_data['results'][0].items())

        for k, v in values.items():

            if getattr(self, k, None) != v:
                self.changed[k] = v
            else:
                try:
                    self.changed.pop(k, None)
                except:
                    pass

            setattr(self, k, v)
