# 워터 센서 (디지털 신호)
import board
import digitalio

class WaterLevelSensor:
    def __init__(self, pin=board.D26):
        """워터 센서 초기화 (GPIO 26번 핀)"""
        self.sensor = digitalio.DigitalInOut(pin)
        self.sensor.direction = digitalio.Direction.INPUT

    def read(self):
        """
        워터 센서 값을 읽어옴
        :return: True(물 감지됨), False(물 없음)
        """
        try:
            return self.sensor.value
        except Exception as e:
            print("센서 읽기 오류:", e)
            return None

    def close(self):
        """센서 해제"""
        try:
            self.sensor.deinit()
        except Exception as e:
            print(f"센서 정리 오류: {e}")


if __name__ == "__main__":
    sensor = WaterLevelSensor(board.D26)
    try:
        water_detected = sensor.read()
        if water_detected is not None:
            if water_detected:
                print("워터센서: 물 감지됨")
            else:
                print("워터센서: 물 없음 (건조)")
        else:
            print("센서값 읽기 실패")
    finally:
        sensor.close()
