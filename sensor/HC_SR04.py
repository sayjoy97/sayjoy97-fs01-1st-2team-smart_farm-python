# 파일명: ultrasonic_sensor.py
from hcsr04sensor import sensor

class UltrasonicSensor:
    def __init__(self, trig_pin: int, echo_pin: int):
        """
        초음파 센서 초기화
        trig_pin: 트리거 핀 (출력)
        echo_pin: 에코 핀 (입력)
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.sensor = sensor.Measurement(trig_pin, echo_pin)

    def read(self, samples: int = 9, wait: float = 0.08) -> float:
        """
        거리(cm) 반환
        samples: 샘플 수 (평균값 필터용)
        wait: 샘플 간 대기 시간 (초)
        """
        distance = self.sensor.raw_distance(sample_size=samples, sample_wait=wait)
        return round(distance, 2)

# ---------------------- 테스트용 실행 ----------------------
if __name__ == "__main__":
    TRIG = 23  # BCM 번호
    ECHO = 24  # BCM 번호

    ultrasonic = UltrasonicSensor(TRIG, ECHO)
    dist = ultrasonic.read()
    print(f"거리: {dist} cm")
