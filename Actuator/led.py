import RPi.GPIO as gpio

class LED:
    def __init__(self, pin):
        try:
            gpio.setmode(gpio.BCM)
        except RuntimeError:
            pass  # 이미 설정됨
        
        # 항상 self.pin을 설정
        self.pin = pin
        
        if isinstance(pin, int):
            gpio.setup(self.pin, gpio.OUT)
            gpio.output(self.pin, gpio.LOW)
        elif isinstance(pin, list):
            for p in self.pin:
                gpio.setup(p, gpio.OUT)
                gpio.output(p, gpio.LOW)
        
        self.is_on = False

    def turn_on(self):
        if isinstance(self.pin, list):
            for p in self.pin:
                gpio.output(p, gpio.HIGH)
        else:
            gpio.output(self.pin, gpio.HIGH)
        self.is_on = True

    def turn_off(self):
        if isinstance(self.pin, list):
            for p in self.pin:
                gpio.output(p, gpio.LOW)
        else:
            gpio.output(self.pin, gpio.LOW)
        self.is_on = False

    def cleanup(self):
        gpio.cleanup(self.pin)