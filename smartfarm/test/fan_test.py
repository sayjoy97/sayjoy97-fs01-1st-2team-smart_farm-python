import RPi.GPIO as GPIO
import time

# 제어할 GPIO 핀 번호 (ULN2003의 IN1 연결)
FAN_PIN = 20

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

print("🌀 팬 제어 테스트 시작 (Ctrl + C로 종료)")

try:
    while True:
        # 팬 ON
        GPIO.output(FAN_PIN, GPIO.HIGH)
        print("💨 팬 켜짐!")
        time.sleep(3)

        # 팬 OFF
        GPIO.output(FAN_PIN, GPIO.LOW)
        print("🛑 팬 꺼짐!")
        time.sleep(3)

except KeyboardInterrupt:
    print("프로그램 종료")
finally:
    GPIO.cleanup()
