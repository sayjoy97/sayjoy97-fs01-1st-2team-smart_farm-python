import RPi.GPIO as GPIO

class VentilationFan:
    """환기팬 제어 (ULN2003 릴레이 모듈 사용)"""
    def __init__(self, pin):
        """
        환기팬 초기화
        
        Args:
            pin: GPIO 핀 번호 (int) 또는 핀 리스트 (list)
        """
        try:
            GPIO.setmode(GPIO.BCM)
        except RuntimeError:
            pass  # 이미 설정됨
        
        # 항상 self.pin을 설정
        self.pin = pin
        
        if isinstance(pin, int):
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)
        elif isinstance(pin, list):
            for p in self.pin:
                GPIO.setup(p, GPIO.OUT)
                GPIO.output(p, GPIO.LOW)
        
        self.is_on = False
        print(f"🌀 환기팬 초기화 완료 (GPIO {pin})")

    def turn_on(self):
        """환기팬 켜기"""
        if isinstance(self.pin, list):
            for p in self.pin:
                GPIO.output(p, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.HIGH)
        self.is_on = True
        print(f"💨 환기팬 ON")

    def turn_off(self):
        """환기팬 끄기"""
        if isinstance(self.pin, list):
            for p in self.pin:
                GPIO.output(p, GPIO.LOW)
        else:
            GPIO.output(self.pin, GPIO.LOW)
        self.is_on = False
        print(f"🛑 환기팬 OFF")

    def cleanup(self):
        """GPIO 정리"""
        if self.is_on:
            self.turn_off()
        GPIO.cleanup(self.pin)
        print(f"🧹 환기팬 GPIO 정리 완료")


if __name__ == "__main__":
    import time

    TEST_PIN = 12
    fan = VentilationFan(TEST_PIN)

    try:
        for _ in range(3):  # 간단히 켜고 끄는 테스트
            fan.turn_on()
            time.sleep(2)
            fan.turn_off()
            time.sleep(2)
    except KeyboardInterrupt:
        print("테스트가 사용자에 의해 중단되었습니다.")
    finally:
        fan.cleanup()

