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
        # 아날로그 값을 읽어와서 반환
        adc_value = self.channel.value  # 0 ~ 65535 사이의 값
        voltage = self.channel.voltage   # 전압 값
        return adc_value, voltage


    def close(self):
        # SPI 및 CS 핀 정리
        self.cs.deinit()
        self.spi.deinit()
