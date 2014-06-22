from lib.garden import Settings
from time import sleep

settings = Settings()

while True:

    sleep(1)

    settings.get_data()

    print settings.changed






