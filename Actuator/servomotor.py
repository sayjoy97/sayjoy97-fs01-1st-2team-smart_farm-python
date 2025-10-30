import RPi.GPIO as gpio
import time

class ServoMotor:
    def __init__(self, pin):
        self.pin = pin
        try:
            gpio.setmode(gpio.BCM)
        except RuntimeError:
            pass  # 이미 설정됨
        gpio.setup(self.pin, gpio.OUT)
        self.pwm = gpio.PWM(self.pin, 50)  # 50Hz 주파수
        self.pwm.start(0)

    def set_angle(self, angle):
        duty_cycle = angle / 18 + 2  # 각도를 듀티 사이클로 변환
        gpio.output(self.pin, True)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)
        gpio.output(self.pin, False)
        self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        self.pwm.start(12.5)
        time.sleep(0.5)
        self.pwm.stop()
        gpio.cleanup(self.pin)
