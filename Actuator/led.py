import RPi.GPIO as gpio

class LED:
    def __init__(self, pin):
        try:
            gpio.setmode(gpio.BCM)
        except RuntimeError:
            pass  # 이미 설정됨
        if isinstance(pin, int):
            self.pin = pin
            gpio.setup(self.pin, gpio.OUT)
        elif isinstance(pin, list):
            self.pins = pin
            for p in self.pins:
                gpio.setup(p, gpio.OUT)
        self.is_on = False

    def turn_on(self):
        if hasattr(self, 'pins'):
            for p in self.pins:
                gpio.output(p, gpio.HIGH)
        else:
            gpio.output(self.pin, gpio.HIGH)
        self.is_on = True

    def turn_off(self):
        if hasattr(self, 'pins'):
            for p in self.pins:
                gpio.output(p, gpio.LOW)
        else:
            gpio.output(self.pin, gpio.LOW)
        self.is_on = False

    def cleanup(self):
        if hasattr(self, 'pins'):
            gpio.cleanup(self.pins)
        else:
            gpio.cleanup(self.pin)