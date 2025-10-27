import RPi.GPIO as GPIO
import time

# L9110S B채널 제어핀 # V : 5V, gnd = gnd 
IB1 = 5
IB2 = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(IB1, GPIO.OUT)
GPIO.setup(IB2, GPIO.OUT)

print("💧 워터펌프 테스트 시작 (B채널 / Ctrl+C로 종료)")

try:
    while True:
        # 펌프 ON (정방향)
        GPIO.output(IB1, GPIO.HIGH)
        GPIO.output(IB2, GPIO.LOW)
        print("💦 워터펌프 작동 중...")
        time.sleep(3)

        # 펌프 OFF
        GPIO.output(IB1, GPIO.LOW)
        GPIO.output(IB2, GPIO.LOW)
        print("🛑 펌프 정지!")
        time.sleep(3)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("프로그램 종료")
