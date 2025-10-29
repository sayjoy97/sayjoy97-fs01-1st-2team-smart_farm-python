import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
led_pins = [17, 25]

for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)

try:
    while True:
        print("빨강 LED ON")
        GPIO.output(17, True)
        time.sleep(1)
        print("노랑 LED ON")
        GPIO.output(25, True)
        time.sleep(1)
        GPIO.output(17, False)
        GPIO.output(25, False)
        print("LED OFF\n")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()