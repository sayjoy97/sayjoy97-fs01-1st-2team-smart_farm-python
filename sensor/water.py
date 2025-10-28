# 물통 수위 센서 (디지털 신호, GPIO)
import board
import digitalio

class WaterLevelSensor:
    def __init__(self, pin=board.D26):
        """
        물통 수위 센서 초기화 (디지털 신호)
        
        Args:
            pin: GPIO 핀 번호 (기본값: D26)
        """
        self.sensor = digitalio.DigitalInOut(pin)
        self.sensor.direction = digitalio.Direction.INPUT

    def read(self):
        """
        물통 수위 센서 값을 읽어옴
        
        Returns:
            True: 물 감지됨 (정상 수위)
            False: 물 없음 (수위 낮음)
        """
        try:
            return self.sensor.value
        except Exception as e:
            print(f"물통 수위 센서 읽기 오류: {e}")
            return None

    def close(self):
        """센서 해제"""
        try:
            self.sensor.deinit()
        except Exception as e:
            print(f"물통 수위 센서 정리 오류: {e}")


if __name__ == "__main__":
    sensor = WaterLevelSensor(board.D26)
    try:
        water_detected = sensor.read()
        if water_detected is not None:
            if water_detected:
                print("물통 수위: 정상 (물 감지됨)")
            else:
                print("물통 수위: 낮음 (물 보충 필요)")
        else:
            print("센서값 읽기 실패")
    finally:
        sensor.close()
