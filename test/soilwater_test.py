import spidev
import RPi.GPIO as GPIO
import time

# MCP3008 SPI 설정 (Bus 0, CE1 사용)
spi = spidev.SpiDev()
spi.open(0, 0) # ce채널 ㅣ            
spi.max_speed_hz = 1350000  # SPI 통신 속도

# D0 입력핀
D0_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(D0_PIN, GPIO.IN)

def read_adc(channel):
    """MCP3008에서 지정 채널(0~7) 값 읽기 (0~1023 범위)"""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

try:
    print("🌿 토양 수분 센서 (A0→CH1, D0→GPIO13) 테스트 시작 (Ctrl+C로 종료)")

    while True:
        # A0 → CH1 아날로그 값 읽기
        analog_value = read_adc(1)
        voltage = analog_value * 3.3 / 1023

        # D0 → GPIO13 디지털 입력 읽기
        digital_state = GPIO.input(D0_PIN)

        print(f"A0(CH1): {analog_value:4d} ({voltage:.2f} V) | D0(GPIO13): {digital_state}")

        time.sleep(1)

except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()
    print("🛑 종료")
