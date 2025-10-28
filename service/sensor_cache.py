"""
불안정한 센서(DHT11, CO2)를 위한 백그라운드 캐싱 시스템
2초마다 센서를 읽고, 최근 성공한 값을 저장
"""
import threading
import time
from collections import deque


class SensorCache:
    """센서 값을 백그라운드에서 주기적으로 읽어 캐싱"""
    
    def __init__(self, sensor, sensor_name="Sensor"):
        self.sensor = sensor
        self.sensor_name = sensor_name
        self.last_value = None
        self.running = False
        self.thread = None
    
    def start(self):
        """백그라운드 센서 읽기 시작"""
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """백그라운드 센서 읽기 중지"""
        self.running = False
    
    def _read_loop(self):
        """2초마다 센서 읽기"""
        while self.running:
            try:
                value = self.sensor.read()
                if value is not None:
                    self.last_value = value
            except:
                pass
            time.sleep(2)
    
    def get(self):
        """최근 성공한 값 반환"""
        return self.last_value

