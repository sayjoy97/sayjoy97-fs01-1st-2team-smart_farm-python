import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

class PhotoResister:
    def __init__(self, channel_number):
        # SPI 객체 생성
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        # CS 핀 설정
        self.cs = digitalio.DigitalInOut(board.D8)
        # MCP3008 객체 생성
        self.mcp = MCP.MCP3008(self.spi, self.cs)
        # 지정된 채널 번호로 아날로그 입력 채널 생성
        self.channel = AnalogIn(self.mcp, channel_number)

    def read(self):
        """
        조도센서 값을 반환
        :return: (디지털 값, 전압) 튜플 반환
        """
        return self.channel.value, self.channel.voltage


    def close(self):
        # SPI 및 CS 핀 정리
        self.cs.deinit()
        self.spi.deinit()


if __name__ == "__main__":
    sensor = PhotoResister(0) # MCP3008 채널 번호 (0-7)
    adc_value, voltage = sensor.read()
    print(f"조도센서 값: {adc_value} (전압: {voltage:.2f}V)")
    sensor.close()