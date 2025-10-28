# ultrasonic_test.py
import RPi.GPIO as GPIO
import time

# 핀 설정
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

print("초음파 센서 거리 측정 시작...")

try:
    while True:
        # 트리거 핀에 10µs 펄스 발생
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # Echo 핀에서 HIGH가 유지된 시간 측정
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        # 거리 계산 (소리 속도 = 34300 cm/s)
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # 왕복 거리이므로 절반

        print(f"거리: {distance:.1f} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("\n측정 종료.")
    GPIO.cleanup()
