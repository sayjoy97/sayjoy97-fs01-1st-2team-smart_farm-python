# 온/습도 센서
import time
import board
import adafruit_dht

class DHT11:
    def __init__(self, pin):
        self.dht_device = adafruit_dht.DHT11(pin)


    def read(self):
        try:
            measured_temp = self.dht_device.temperature
            measured_humidity = self.dht_device.humidity
            time.sleep(900)
        except RuntimeError as e:
            print(f"Error reading DHT11 sensor: {e}")
        finally:
            return measured_temp, measured_humidity


    def close(self):
        self.dht_device.exit()
