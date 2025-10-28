import RPi.GPIO as GPIO

class WaterPump:
    """물펌프 제어 (L9110S 모터 드라이버 B채널 사용)"""
    def __init__(self, pin_ib1, pin_ib2=None):
        """
        물펌프 초기화 (L9110S B채널)
        
        Args:
            pin_ib1: IB1 핀 (제어 핀 1)
            pin_ib2: IB2 핀 (제어 핀 2), 없으면 pin_ib1+1 사용
        """
        self.pin_ib1 = pin_ib1
        self.pin_ib2 = pin_ib2 if pin_ib2 is not None else pin_ib1 + 1
        
        try:
            GPIO.setmode(GPIO.BCM)
        except RuntimeError:
            pass  # 이미 설정됨
        GPIO.setup(self.pin_ib1, GPIO.OUT)
        GPIO.setup(self.pin_ib2, GPIO.OUT)
        
        # 초기 상태: OFF
        GPIO.output(self.pin_ib1, GPIO.LOW)
        GPIO.output(self.pin_ib2, GPIO.LOW)
        
        self.is_on = False
        print(f"💧 물펌프 초기화 완료 (GPIO {self.pin_ib1}/{self.pin_ib2})")

    def turn_on(self):
        """물펌프 켜기 (정방향)"""
        GPIO.output(self.pin_ib1, GPIO.HIGH)
        GPIO.output(self.pin_ib2, GPIO.LOW)
        self.is_on = True
        print(f"� 물펌프 ON (GPIO {self.pin_ib1}/{self.pin_ib2})")

    def turn_off(self):
        """물펌프 끄기"""
        GPIO.output(self.pin_ib1, GPIO.LOW)
        GPIO.output(self.pin_ib2, GPIO.LOW)
        self.is_on = False
        print(f"� 물펌프 OFF (GPIO {self.pin_ib1}/{self.pin_ib2})")

    def cleanup(self):
        """GPIO 정리"""
        if self.is_on:
            self.turn_off()
        GPIO.cleanup([self.pin_ib1, self.pin_ib2])
        print(f"🧹 물펌프 GPIO {self.pin_ib1}/{self.pin_ib2} 정리 완료")

