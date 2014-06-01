import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


GPIO.setup(23, GPIO.IN)

i = 0


def increment():
		print i

GPIO.add_event_detect(23, GPIO.RISING, callback=increment, bouncetime=0)


while True:

	GPIO.wait_for_edge(23, GPIO.RISING)
	
	i = i + 1
	
