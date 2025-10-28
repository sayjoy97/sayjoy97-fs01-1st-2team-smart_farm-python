import RPi.GPIO as gpio

class WaterPump:
    """물펌프 (LED로 구현)"""
    def __init__(self, pin):
        self.pin = pin
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin, gpio.OUT)
        self.is_on = False

    def turn_on(self):
        gpio.output(self.pin, gpio.HIGH)
        self.is_on = True
        print(f"💧 물펌프 ON (GPIO {self.pin})")

    def turn_off(self):
        gpio.output(self.pin, gpio.LOW)
        self.is_on = False
        print(f"🚫 물펌프 OFF (GPIO {self.pin})")

    def cleanup(self):
        gpio.cleanup(self.pin)

