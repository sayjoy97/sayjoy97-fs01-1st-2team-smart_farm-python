# water_level_mcp3208.py
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3208 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time

class WaterLevelSensor:
    def __init__(self, channel_number=3, cs_pin=board.D8):#핀 번호 설정
        # SPI 객체 생성
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        # CS 핀 설정
        self.cs = digitalio.DigitalInOut(cs_pin)
        # MCP3208 객체 생성
        self.mcp = MCP.MCP3208(self.spi, self.cs)
        # 지정된 채널 번호로 아날로그 입력 채널 생성
        self.channel = AnalogIn(self.mcp, channel_number)

    def read(self):
        try:
            adc_value = self.channel.value 
            voltage = self.channel.voltage
            return adc_value, voltage
        except Exception as e:
            print("센서 읽기 오류:", e)
            return None, None

    def close(self):
        """SPI 연결 종료"""
        self.cs.deinit()
        self.spi.deinit()


if __name__ == "__main__":
    sensor = WaterLevelSensor(channel_number=0)
    try:
        adc_value, voltage = sensor.read()
        if adc_value is not None:
            print(f" 워터센서: {adc_value}/65535 ({voltage:.2f}V)")
            if adc_value < 12800:      # ~20%
                print(" 건조함")
            elif adc_value < 40000:    # ~60%
                print("  적정")
            else:
                print(" 충분히 젖음")
        else:
            print("센서값 읽기 실패")
    finally:
        sensor.close()
