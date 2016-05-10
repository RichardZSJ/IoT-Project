import mraa
import time

RedPin = 3
BluePin = 4
# humidity_seneor = mraa.Gpio(sensorPin)
# humidity_seneor.dir(mraa.DIR_IN)
i = 0

redLED = mraa.Gpio(RedPin)
blueLED = mraa.Gpio(BluePin)

redLED.dir(mraa.DIR_OUT)
blueLED.dir(mraa.DIR_OUT)

try:
	while (1):
		redLED.write(True)
		blueLED.write(False)
		time.sleep(1)
		redLED.write(False)
		blueLED.write(True)
		time.sleep(1)

except KeyboardInterrupt:
	redLED.write(False)
	blueLED.write(False)
	exit
