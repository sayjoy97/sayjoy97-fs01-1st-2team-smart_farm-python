# 토양 수분 센서 (아날로그 신호, MCP3208)
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

class SoilMoistureSensor:
    def __init__(self, channel_number=0, cs_pin=board.D8):
        """
        토양 수분 센서 초기화 (MCP3208 ADC 사용)
        
        Args:
            channel_number: MCP3208 채널 번호 (0~7)
            cs_pin: CS 핀 번호 (기본값: D8)
        """
        # SPI 객체 생성
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        # CS 핀 설정
        self.cs = digitalio.DigitalInOut(cs_pin)
        # MCP3008 객체 생성
        self.mcp = MCP.MCP3008(self.spi, self.cs)
        # 지정된 채널 번호로 아날로그 입력 채널 생성
        self.channel = AnalogIn(self.mcp, channel_number)

    def read(self):
        """
        토양 수분 센서 값을 읽어옴
        
        Returns:
            adc_value: ADC 값 (0~65535)
            voltage: 전압 (V)
        """
        try:
            adc_value = self.channel.value 
            voltage = self.channel.voltage
            return adc_value, voltage
        except Exception as e:
            print(f"토양수분 센서 읽기 오류: {e}")
            return None, None

    def close(self):
        """SPI 연결 종료"""
        try:
            self.cs.deinit()
            self.spi.deinit()
        except Exception as e:
            print(f"토양수분 센서 정리 오류: {e}")


if __name__ == "__main__":
    sensor = SoilMoistureSensor(channel_number=1)
    try:
        adc_value, voltage = sensor.read()
        if adc_value is not None:
            print(f"토양수분센서: {adc_value}/65535 ({voltage:.2f}V)")
            if adc_value < 12800:      # ~20%
                print("  상태: 건조함")
            elif adc_value < 40000:    # ~60%
                print("  상태: 적정")
            else:
                print("  상태: 충분히 젖음")
        else:
            print("센서값 읽기 실패")
    finally:
        sensor.close()
