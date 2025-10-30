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
from service.read_sensors import read_slot_sensors, read_ultrasonic_sensor, read_water_tank_sensor, init_sensor_caches, stop_sensor_caches
from service.actuator_control import ActuatorController
from service.water_tank_monitor import WaterTankMonitor
from Actuator.heater import Heater
from Actuator.water_pump import WaterPump
from Actuator.ventilation_fan import VentilationFan
from Actuator.servomotor import ServoMotor
from Actuator.led import LED

def main():
    # ========================================
    # 여기만 수정하세요!
    # ========================================
    
    # 디바이스 시리얼 넘버
    device_serial = "B1002"
    
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
    
        # 슬롯별 액추에이터 GPIO 핀 번호 (test 파일 기준)
    actuator_pin_map = {
        1: {'heater': [16,17], 'led': [27,25,18], 'water_ib1': 5, 'water_ib2': 6, 'fan': [20,12], 'servo': 21},      # 슬롯 1
        # 2: {'heater': 19, 'water_ib1': 13, 'water_ib2': 26, 'fan': 21},    # 슬롯 2
        # 3: {'heater': 20, 'water_ib1': 16, 'water_ib2': 12, 'fan': 25},    # 슬롯 3
        # 4: {'heater': 23, 'water_ib1': 24, 'water_ib2': 27, 'fan': 18},    # 슬롯 4
    }
    
    # 슬롯별 센서 핀 번호 / 채널 (test 파일 기준)
    sensor_pin_map = {
        1: {'dht11_pin': board.D22,  'photo_channel': 0, 'soil_channel': 1, 'co2_port': '/dev/serial0' if has_co2 else None},   # 슬롯 1
        # 2: {'dht11_pin': board.D17, 'photo_channel': 1, 'soil_channel': 2, 'co2_port': '/dev/serial1' if has_co2 else None},   # 슬롯 2
        # 3: {'dht11_pin': board.D18, 'photo_channel': 2, 'soil_channel': 3, 'co2_port': '/dev/serial2' if has_co2 else None},   # 슬롯 3
        # 4: {'dht11_pin': board.D27, 'photo_channel': 3, 'soil_channel': 4, 'co2_port': '/dev/serial3' if has_co2 else None},   # 슬롯 4
    }
    
    # 초음파 센서 (통합 - 슬롯 공유, 물통 거리 측정)
    ultrasonic_trig = 23
    ultrasonic_echo = 24
    
    # 물통 수위 센서 (통합 - 슬롯 공유, 디지털 신호)
    water_tank_pin = board.D26

    # ========================================
    # 아래는 수정하지 마세요
    # ========================================

    print("=" * 60)
    print("🌱 스마트팜 시스템 시작")
    print("=" * 60)
    print(f"📟 디바이스: {device_serial}")
    print(f"🌐 MQTT 브로커: {broker}")
    print(f"⏱️  센서 읽기 주기: {interval}초")
    print("=" * 60)

    # 슬롯별 객체 저장
    clients = {}
    controllers = {}
    actuators = {}  # cleanup 용도
    
    def create_preset_callback(slot_num):
        """슬롯별 프리셋 업데이트 콜백 생성 (클로저)"""
        def on_preset_updated(new_preset):
            timestamp = time.strftime("%H:%M:%S")
            print(f"\n🔄 [{timestamp}] 슬롯 {slot_num} 프리셋 실시간 업데이트!")
            print(f"   🌡️  온도: {new_preset.get('OptimalTemp')}°C")
            print(f"   💧 습도: {new_preset.get('OptimalHumidity')}%")
            print(f"   💡 조도: {new_preset.get('LightIntensity')} lux")
            print(f"   🌱 토양: {new_preset.get('SoilMoisture')} ADC")
            print(f"   🌫️  CO2: {new_preset.get('Co2Level')} ppm")
            print(f"   ✅ 다음 제어 사이클({interval}초 이내)에 자동 반영됩니다.\n")
        return on_preset_updated
    
    # 물탱크 모니터 초기화 (디바이스 단위로 1개 - 모든 슬롯 공유)
    # 첫 번째 슬롯의 MQTT 클라이언트 사용 (알림 전송용)
    water_monitor = None

    try:
        # 슬롯별 초기화
        print("\n🔧 슬롯 초기화 중...")
        for slot in slots:
            farm_uid = f"{device_serial}:{slot}"
            act_pins = actuator_pin_map[slot]
            sens_pins = sensor_pin_map[slot]
            
            print(f"\n  슬롯 {slot} ({farm_uid})")
            print(f"    🔥 히터: GPIO {act_pins['heater']}")
            print(f"    💧 물펌프: GPIO {act_pins['water_ib1']}/{act_pins['water_ib2']}")
            print(f"    🌀 환기팬: GPIO {act_pins['fan']}")
            print(f"    led: GPIO {act_pins['led']}")
            print(f"    🌡️  DHT11: GPIO {sens_pins['dht11_pin']}")
            print(f"    💡 조도센서: 채널 {sens_pins['photo_channel']}")
            print(f"    🌱 토양센서: 채널 {sens_pins['soil_channel']}")
            print(f"    🌫️  CO2센서: {sens_pins['co2_port'] if has_co2 else '없음(일반형)'}")
            
            # 액추에이터 초기화
            heater = Heater(act_pins['heater'])
            water_pump = WaterPump(act_pins['water_ib1'], act_pins['water_ib2'])
            ventilation_fan = VentilationFan(act_pins['fan'])
            led =  LED(act_pins['led'])
                
            servo = None
            if 'servo' in act_pins and act_pins['servo'] is not None:
                servo = ServoMotor(act_pins['servo'])
                print(f"    🫧 CO2 서보: GPIO {act_pins['servo']}")
            
            # MQTT 클라이언트 초기화
            client = MqttClient(farm_uid, broker)
            
            # 프리셋 업데이트 콜백 등록 (MQTT로 실시간 변경 감지)
            preset_callback = create_preset_callback(slot)
            client.set_preset_update_callback(preset_callback)
            
            # 물탱크 모니터 초기화 (첫 번째 슬롯에서만)
            if water_monitor is None:
                water_monitor = WaterTankMonitor(client, device_serial)
                print(f"\n  💧 물탱크 모니터 초기화 완료")
                print(f"    - 급수탱크: 초음파 센서 (GPIO {ultrasonic_trig}/{ultrasonic_echo})")
                print(f"    - 물받이탱크: 워터 센서 (GPIO {water_tank_pin})")
            
            # 액추에이터 컨트롤러 초기화
            controller = ActuatorController(heater, water_pump, ventilation_fan, led, water_monitor, co2_servo=servo)
            
            # 저장
            clients[slot] = client
            controllers[slot] = controller
            actuators[slot] = {
                'heater': heater,
                'water_pump': water_pump,
                'ventilation_fan': ventilation_fan,
                'led': led,
                'servo': servo,
            }

        # 센서 캐시 초기화 (DHT11, CO2 백그라운드 스레드 시작)
        print("\n🔄 센서 캐시 초기화 중...")
        for slot in slots:
            init_sensor_caches(slot, sensor_pin_map[slot], has_co2=has_co2)
        time.sleep(3)  # 워밍업 대기

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
        print("💧 물탱크 모니터링 활성화")
        print("=" * 60)
        print("\n✅ 센서 데이터 전송 및 자동 제어 시작...\n")
        
        # 메인 루프
        while True:
            try:
                # ========================================
                # 통합 센서 읽기 (모든 슬롯 공유)
                # ========================================
                
                # 1. 급수 물탱크 (초음파 센서)
                distance = read_ultrasonic_sensor(ultrasonic_trig, ultrasonic_echo)
                supply_status = water_monitor.check_supply_tank(distance)
                
                # 2. 물받이 물탱크 (워터 센서)
                water_tank_detected = read_water_tank_sensor(water_tank_pin)
                overflow_status = water_monitor.check_overflow_tank(water_tank_detected)
                
                # 물탱크 상태 요약
                tank_summary = water_monitor.get_status_summary()
                if tank_summary['alert_status'] != "정상":
                    water_monitor.mqtt_client.send_notification_logs(f"[WARNING] [물탱크] 급수상태={supply_status}, 물받이상태={overflow_status}")
                    print(f"\n⚠️  물탱크 주의: 급수={supply_status}, 물받이={overflow_status}\n")
                
                # ========================================
                # 슬롯별 처리
                # ========================================
                for slot in slots:
                    # 슬롯별 센서 읽기 (온도, 습도, 조도, 토양수분, CO2)
                    temp, hum, light_adc, soil_adc, co2 = read_slot_sensors(slot, sensor_pin_map[slot], has_co2=has_co2)
                    
                    # 센서 데이터 전송
                    clients[slot].send_sensor_data(temp, hum, light_adc, soil_adc, co2)
                    
                    # 액추에이터 자동 제어 (프리셋 기반 + 물탱크 안전 체크)
                    sensor_data = {
                        'temp': temp,
                        'humidity': hum,
                        'light': light_adc,
                        'soil': soil_adc,
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
        
        # 센서 캐시 중지
        stop_sensor_caches()
        
        # 액추에이터 정리
        print("🧹 액추에이터 정리 중...")
        for slot in slots:
            controllers[slot].stop_all()
            actuator_set = actuators[slot]
            actuator_set['heater'].cleanup()
            actuator_set['water_pump'].cleanup()
            actuator_set['ventilation_fan'].cleanup()
            actuator_set['led'].cleanup()
            if actuator_set['servo']:
                actuator_set['servo'].cleanup()
        time.sleep(1)
        print("✅ 프로그램 종료\n")


if __name__ == "__main__":
    main()
