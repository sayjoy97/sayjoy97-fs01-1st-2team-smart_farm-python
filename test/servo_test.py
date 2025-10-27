import RPi.GPIO as GPIO
import time

SERVO_PIN = 21  # 주황선 연결 핀 번호

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 50Hz 주파수로 PWM 객체 생성
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

print("🧭 서보모터 테스트 시작...")

def set_angle(angle):
    duty = 2.5 + (angle / 18)  # 각도를 DutyCycle로 변환
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

try:
    while True:
        print("⏩ 0도")
        set_angle(0)
        time.sleep(1)

        print("⏩ 90도")
        set_angle(90)
        time.sleep(1)

        print("⏩ 180도")
        set_angle(180)
        time.sleep(1)

except KeyboardInterrupt:
    servo.stop()
    GPIO.cleanup()
    print("서보모터 테스트 종료.")
