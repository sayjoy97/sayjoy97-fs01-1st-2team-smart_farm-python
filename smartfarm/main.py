"""
스마트팜 라즈베리파이 메인 프로그램 (멀티슬롯 지원)

사용 방법:
    1. device_serial: 디바이스 시리얼 넘버 설정
    2. slots: 슬롯 번호 리스트 (예: [1], [1,2,3,4])
    3. pin_map: 슬롯별 GPIO 핀 번호 설정
    4. python smartfarm/main.py 실행
"""

import time
import board
from mqtt.mqtt_client import MqttClient
from service.read_sensors import read_slot_sensors, read_ultrasonic_sensor
from service.actuator_control import ActuatorController
from Actuator.heater import Heater
from Actuator.water_pump import WaterPump
from Actuator.ventilation_fan import VentilationFan


def main():
    # ========================================
    # 여기만 수정하세요!
    # ========================================
    
    # 디바이스 시리얼 넘버
    device_serial = "A1001"
    
    # MQTT 브로커 주소 (같은 컴퓨터: localhost, 다른 컴퓨터: IP 주소)
    broker = "192.168.14.69" # 경신 : 69번 우영: 62
    
    # 센서 읽기 주기 (초)
    interval = 10
    
    # 디바이스 모델 자동 판별 (시리얼 규칙)
    # - 고급형 4슬롯: A4xxx  → slots=[1,2,3,4], has_co2=True
    # - 고급형 1슬롯: A1xxx  → slots=[1],       has_co2=True
    # - 일반형 4슬롯: B4xxx  → slots=[1,2,3,4], has_co2=False
    # - 일반형 1슬롯: B1xxx  → slots=[1],       has_co2=False
    model_prefix = device_serial[:2].upper()  # 예: A4, A1, B4, B1
    if model_prefix == "A4":
        slots = [1, 2, 3, 4]
        has_co2 = True
    elif model_prefix == "A1":
        slots = [1]
        has_co2 = True
    elif model_prefix == "B4":
        slots = [1, 2, 3, 4]
        has_co2 = False
    elif model_prefix == "B1":
        slots = [1]
        has_co2 = False
    else:
        # 기본값: 1슬롯, CO2 없음
        slots = [1]
        has_co2 = False
    
    # 슬롯별 액추에이터 GPIO 핀 번호
    actuator_pin_map = {
        1: {'heater': 17, 'water': 21, 'fan': 18},      # 슬롯 1
        2: {'heater': 5,  'water': 6,  'fan': 13},      # 슬롯 2
        3: {'heater': 19, 'water': 26, 'fan': 21},      # 슬롯 3
        4: {'heater': 20, 'water': 16, 'fan': 12},      # 슬롯 4
    }
    
    # 슬롯별 센서 핀 번호 / 채널
    sensor_pin_map = {
        1: {'dht11_pin': board.D22,  'photo_channel': 0, 'water_pin': board.D26, 'co2_port': '/dev/serial0' if has_co2 else None},   # 슬롯 1
        2: {'dht11_pin': board.D17, 'photo_channel': 1, 'water_pin': board.D26, 'co2_port': '/dev/serial1' if has_co2 else None},   # 슬롯 2
        3: {'dht11_pin': board.D18, 'photo_channel': 2, 'water_pin': board.D26, 'co2_port': '/dev/serial2' if has_co2 else None},   # 슬롯 3
        4: {'dht11_pin': board.D27, 'photo_channel': 3, 'water_pin': board.D26, 'co2_port': '/dev/serial3' if has_co2 else None},   # 슬롯 4
    }
    
    # 초음파 센서 (통합 - 슬롯 공유)
    ultrasonic_trig = 23
    ultrasonic_echo = 24
    
    # 워터 펌프 
    
    # ========================================
    # 아래는 수정하지 마세요
    # ========================================

    print("=" * 60)
    print("🌱 스마트팜 시스템 시작")
    print("=" * 60)
    print(f"📟 디바이스: {device_serial}")
    print(f"📍 슬롯: {slots}")
    print(f"🌐 MQTT 브로커: {broker}")
    print(f"⏱️  센서 읽기 주기: {interval}초")
    print("=" * 60)

    # 슬롯별 객체 저장
    clients = {}
    controllers = {}
    actuators = {}  # cleanup 용도

    try:
        # 슬롯별 초기화
        print("\n🔧 슬롯 초기화 중...")
        for slot in slots:
            farm_uid = f"{device_serial}:{slot}"
            act_pins = actuator_pin_map[slot]
            sens_pins = sensor_pin_map[slot]
            
            print(f"\n  슬롯 {slot} ({farm_uid})")
            print(f"    🔥 히터: GPIO {act_pins['heater']}")
            print(f"    💧 물펌프: GPIO {act_pins['water']}")
            print(f"    🌀 환기팬: GPIO {act_pins['fan']}")
            print(f"    🌡️  DHT11: GPIO {sens_pins['dht11_pin']}")
            print(f"    💡 조도센서: 채널 {sens_pins['photo_channel']}")
            print(f"    💧 워터센서: GPIO {sens_pins['water_pin']}")
            print(f"    🌫️  CO2센서: {sens_pins['co2_port'] if has_co2 else '없음(일반형)'}")
            
            # 액추에이터 초기화
            heater = Heater(act_pins['heater'])
            water_pump = WaterPump(act_pins['water'])
            ventilation_fan = VentilationFan(act_pins['fan'])
            
            # 액추에이터 컨트롤러 초기화
            controller = ActuatorController(heater, water_pump, ventilation_fan)
            
            # MQTT 클라이언트 초기화
            client = MqttClient(farm_uid, broker)
            
            # 저장
            clients[slot] = client
            controllers[slot] = controller
            actuators[slot] = (heater, water_pump, ventilation_fan)

        # 프리셋 요청
        print(f"\n📡 DB 서버에 프리셋 요청 중...")
        for slot in slots:
            clients[slot].request_preset()
        
        # 프리셋 응답 대기 (최대 10초)
        print(f"⏳ 프리셋 응답 대기 중...")
        wait_count = 0
        all_ready = False
        while not all_ready and wait_count < 10:
            all_ready = all(clients[s].is_preset_ready() for s in slots)
            if not all_ready:
                print(f"   ({wait_count + 1}/10초)")
                time.sleep(1)
                wait_count += 1
        
        print("\n✅ 프리셋 설정 완료!")
        for slot in slots:
            if clients[slot].is_preset_ready():
                preset = clients[slot].get_preset()
                print(f"\n  슬롯 {slot}")
                print(f"    온도: {preset.get('OptimalTemp')}°C")
                print(f"    습도: {preset.get('OptimalHumidity')}%")
                print(f"    조도: {preset.get('LightIntensity')} lux")
                print(f"    토양: {preset.get('SoilMoisture')} ADC")
                print(f"    CO2: {preset.get('Co2Level')} ppm")
            else:
                print(f"\n  슬롯 {slot}: 기본값으로 동작")
        
        print("\n" + "=" * 60)
        print("💡 센서 데이터는 DB 서버로 전송")
        print("💡 프리셋 기반 자동 제어 시작")
        print("=" * 60)
        print("\n✅ 센서 데이터 전송 및 자동 제어 시작...\n")
        
        # 메인 루프
        while True:
            try:
                # 초음파 센서 읽기 (통합 - 슬롯 공유)
                distance = read_ultrasonic_sensor(ultrasonic_trig, ultrasonic_echo)
                
                # 슬롯별 처리
                for slot in slots:
                    # 슬롯별 센서 읽기
                    temp, hum, light_adc, water_detected, co2 = read_slot_sensors(slot, sensor_pin_map[slot], has_co2=has_co2)
                    
                    # 센서 데이터 전송
                    clients[slot].send_sensor_data(temp, hum, light_adc, water_detected, co2)
                    
                    # 액추에이터 자동 제어 (프리셋 기반)
                    sensor_data = {
                        'temp': temp,
                        'humidity': hum,
                        'light': light_adc,
                        'water': water_detected,
                        'co2': co2
                    }
                    preset = clients[slot].get_preset()
                    controllers[slot].control(sensor_data, preset)
                
                # 대기
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 사용자에 의해 중단됨")
                break
            except Exception as e:
                print(f"❌ 루프 오류: {e}")
                print(f"⏳ {interval}초 후 재시도...")
                time.sleep(interval)
                
    finally:
        print("\n🔌 MQTT 연결 종료 중...")
        for slot in slots:
            clients[slot].close()
        
        # 액추에이터 정리
        print("🧹 액추에이터 정리 중...")
        for slot in slots:
            controllers[slot].stop_all()
            heater, water_pump, ventilation_fan = actuators[slot]
            heater.cleanup()
            water_pump.cleanup()
            ventilation_fan.cleanup()
        
        print("✅ 프로그램 종료\n")


if __name__ == "__main__":
    main()