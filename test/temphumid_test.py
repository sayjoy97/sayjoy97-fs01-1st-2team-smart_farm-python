import time
# 데이터 송신용 board모듈 - 라즈베리파이나 아두이노에서 핀에 정보를 추상화해서 
# 일관된 방법으로 핀을 제어할 수 있도록 도와주는 라이브러리 
import board  
import adafruit_dht

# D가 라즈베리파이의 GPIO핀을 표현한 이름 D25 ->GPIO25 핀
mydht11 = adafruit_dht.DHT11(board.D5)

while True:
    try:
        # 습도 
        humidity_data = mydht11.humidity
        # 온도
        temperature_data = mydht11.temperature
        print(humidity_data,  temperature_data)
        # 센서 내부에서 초기화 작업시 필요한 시간
        time.sleep(2)
    except RuntimeError as error:
        print(error)
    finally:
        pass
# 오류가 자주 뜸.
# try:
#     while True:
#         # 습도 
#         humidity_data = mydht11.humidity
#         # 온도
#         temperature_data = mydht11.temperature
#         print(humidity_data,  temperature_data)
#         # 센서 내부에서 초기화 작업시 필요한 시간
#         time.sleep(2)
        
# except RuntimeError as error:
#     print(error.args[0])
    
# finally:
#     pass