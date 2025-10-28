# -------------------------------
# 조도센서 (LDR) + MCP3208 테스트
# MCP3208: 아날로그 값을 0~4095 사이로 디지털로 변환
# LDR(조도센서): 빛의 세기에 따라 저항값이 변함
# -------------------------------

import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# SPI 통신 설정 (라즈베리파이용)
spi = busio.SPI(clock=board.SCLK, MISO=board.MISO, MOSI=board.MOSI)

# MCP3208의 CS(Chip Select) 핀 연결 (GPIO4 또는 GPIO8 중 실제 연결된 쪽 선택)
cs = digitalio.DigitalInOut(board.D8)  # 보통 GPIO8 (물리핀 24)
mcp = MCP.MCP3008(spi, cs)

# MCP3208의 CH0에 조도센서 연결
ldr_channel = AnalogIn(mcp, MCP.P0)

print("🌞 조도센서(LDR) 값 읽기 시작...\n")
try:
    while True:
        adc_value = ldr_channel.value  # 0~65535 사이 값
        voltage = ldr_channel.voltage  # 전압값 (0~3.3V)
        print(f"ADC Raw: {adc_value} | Voltage: {voltage:.2f}V")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n프로그램 종료.")