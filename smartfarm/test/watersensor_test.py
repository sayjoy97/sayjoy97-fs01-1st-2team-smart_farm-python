import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
MOISTURE_PIN = 26
GPIO.setup(MOISTURE_PIN, GPIO.IN)

try:
    while True:
        if GPIO.input(MOISTURE_PIN) == 0:
            print("💧 습한 토양 감지!")
        else:
            print("🌵 건조한 토양 감지!")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()