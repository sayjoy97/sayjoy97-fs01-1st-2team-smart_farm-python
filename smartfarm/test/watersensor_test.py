# import RPi.GPIO as GPIO
# import time

# GPIO.setmode(GPIO.BCM)
# MOISTURE_PIN = 26
# GPIO.setup(MOISTURE_PIN, GPIO.IN)

# try:
#     while True:
#         if GPIO.input(MOISTURE_PIN) == 0:
#             print("💧 습한 토양 감지!")
#         else:
#             print("🌵 건조한 토양 감지!")
#         time.sleep(1)
# except KeyboardInterrupt:
#     GPIO.cleanup()


# 아날로그로 변환

# import spidev
# import time

# spi = spidev.SpiDev()
# spi.open(0, 0)
# spi.max_speed_hz = 1350000

# def read_channel(channel):
#     adc = spi.xfer2([6 | (channel >> 2), (channel & 3) << 6, 0])
#     data = ((adc[1] & 0x0F) << 8) | adc[2]
#     return data

# def convert_to_percent(value):
#     wet = 200   # 완전히 젖은 상태 (물에 담갔을 때의 Raw 값)
#     dry = 4000 # 완전히 마른 상태 (공기 중 Raw 값)
#     if value > dry: value = dry
#     if value < wet: value = wet
#     percent = 100 - ((value - wet) / (dry - wet) * 100)
#     return round(percent, 1)

# try:
#     while True:
#         raw = read_channel(1)   
#         voltage = (raw / 4095.0) * 3.3
#         moisture = convert_to_percent(raw)
#         print(f"🌱 Raw: {raw} | 전압: {voltage:.2f}V | 수분: {moisture}%")
#         time.sleep(1)

# except KeyboardInterrupt:
#     spi.close()
#     print("🛑 종료합니다.")



# import spidev
# import time

# spi = spidev.SpiDev()
# spi.open(0, 0)
# spi.max_speed_hz = 1350000

# def read_channel(channel):
#     # MCP3208은 12비트 → 3바이트 전송
#     adc = spi.xfer2([6 | (channel >> 2), (channel & 3) << 6, 0])
#     data = ((adc[1] & 0x0F) << 8) | adc[2]
#     return data

# try:
#     while True:
#         raw = read_channel(0)  # CH0에서 데이터 읽기
#         voltage = (raw / 4095.0) * 3.3  # 전압으로 변환
#         print(f"🌱 Raw: {raw} | 전압: {voltage:.2f} V")

#         # 물에 담그면 raw 값이 작아지고,
#         # 건조하면 raw 값이 커짐 (센서에 따라 반대일 수도 있음)
#         time.sleep(1)

# except KeyboardInterrupt:
#     spi.close()
#     print("🛑 종료합니다.")


# import spidev
# import time

# # SPI 초기화
# spi = spidev.SpiDev()
# spi.open(0, 0)  # Bus 0, Device 0 (CE0)
# spi.max_speed_hz = 1350000

# def read_channel(channel):
#     # MCP3208에서 채널 읽기 (12비트)
#     adc = spi.xfer2([6 | (channel >> 2), (channel & 3) << 6, 0])
#     data = ((adc[1] & 0x0F) << 8) | adc[2]
#     return data

# try:
#     while True:
#         raw = read_channel(1)  # CH0: 토양 수분 센서 연결
#         voltage = (raw / 4095.0) * 3.3  # 전압 변환
#         moisture = 100 - int((raw / 4095.0) * 100)  # 0~100% 변환 (값이 낮을수록 습함)

#         print(f"💧 Raw: {raw} | 전압: {voltage:.2f} V | 추정 습도: {moisture}%")

#         # 참고:
#         # 건조할수록 raw 값이 높고 (저항 ↑)
#         # 물에 젖을수록 raw 값이 낮음 (저항 ↓)
#         # 👉 센서 종류에 따라 반대일 수도 있으니 직접 관찰해서 반대로 보정 가능
#         time.sleep(1)

# except KeyboardInterrupt:
#     spi.close()
#     print("🛑 프로그램 종료")


import RPi.GPIO as GPIO
import time

MOISTURE_PIN = 26  # 센서 DO 핀 연결 (디지털 출력)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_PIN, GPIO.IN)

print("🌱 토양 수분 센서 테스트 시작...")
print("Ctrl + C 로 종료")

try:
    while True:
        value = GPIO.input(MOISTURE_PIN)
        if value == 0:
            print("🌵 건조한 토양 감지!")
        else:
            print(" 💧 습한 토양 감지!")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("🛑 프로그램 종료")
