import mraa
import time

sensorPin = 7;

motion_seneor = mraa.Gpio(sensorPin)
motion_seneor.dir(mraa.DIR_IN)
i = 0

try:
    while (1):
        if (motion_seneor.read()):
            print 'Motion detected ', i
            i += 1
            time.sleep(0.1)
except KeyboardInterrupt:
        exit
