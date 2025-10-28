import RPi.GPIO as gpio

class Heater:
    """히터 (LED로 구현)"""
    def __init__(self, pin):
        self.pin = pin
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin, gpio.OUT)
        self.is_on = False

    def turn_on(self):
        gpio.output(self.pin, gpio.HIGH)
        self.is_on = True
        print(f"🔥 히터 ON (GPIO {self.pin})")

    def turn_off(self):
        gpio.output(self.pin, gpio.LOW)
        self.is_on = False
        print(f"❄️  히터 OFF (GPIO {self.pin})")

    def cleanup(self):
        gpio.cleanup(self.pin)


if __name__ == "__main__":
    import time

    TEST_PIN = 17
    heater = Heater(TEST_PIN)

    try:
        for _ in range(3):  # 간단한 토글 테스트
            heater.turn_on()
            time.sleep(2)
            heater.turn_off()
            time.sleep(2)
    except KeyboardInterrupt:
        print("테스트가 사용자에 의해 중단되었습니다.")
    finally:
        heater.cleanup()

