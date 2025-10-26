# 온/습도 센서
import time
import board
import adafruit_dht

class DHT11:
    def __init__(self, pin):
        """DHT11 초기화"""
        self.dht_device = adafruit_dht.DHT11(pin)

    def read(self):
        try:        
            temp = self.dht_device.temperature
            humidity = self.dht_device.humidity
            return round(temp, 1), round(humidity, 1)
        except:
            return None, None

    def close(self):
        """센서 해제"""
        self.dht_device.exit()



if __name__ == "__main__":
    sensor = DHT11(board.D4)  # 예: GPIO4번
    try:
        temp, hum = sensor.read()
        if temp is not None:
            print(f"온도: {temp}°C / 습도: {hum}%")
        else:
            print("센서값 읽기 실패")
    finally:
        sensor.close()
