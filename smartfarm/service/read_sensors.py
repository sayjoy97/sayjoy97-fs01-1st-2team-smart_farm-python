from sensor.dht11 import DHT11
from sensor.photoresister import PhotoResister
from sensor.MH_Z19B import CO2Sensor
from sensor.HC_SR04 import UltrasonicSensor
from sensor.water import WaterLevelSensor
from mqtt.mqtt_client import MqttClient
import board


def read_slot_sensors(slot, sensor_pins, has_co2=True):
    """슬롯별 센서 값 읽기 (초음파 제외)
    
    Args:
        slot: 슬롯 번호
        sensor_pins: 슬롯별 센서 핀 설정 딕셔너리
            예: {
                'dht11_pin': board.D4,
                'photo_channel': 0,

                'water_pin': board.D26,

                'water_channel': 3,
                'co2_port': '/dev/serial0'
            }
    
    Returns:

        temp, hum, light_adc, water_detected, co2

        temp, hum, light_adc, soil_adc, co2
    """
    
    print(f"\n[슬롯 {slot}] 센서 값 읽기 시작...")
    
    # 센서 인스턴스 생성
    dht11_sensor = DHT11(sensor_pins['dht11_pin'])
    photo_sensor = PhotoResister(sensor_pins['photo_channel'])
    co2_sensor = None
    if has_co2 and 'co2_port' in sensor_pins and sensor_pins['co2_port']:
        co2_sensor = CO2Sensor(sensor_pins['co2_port'])

    water_sensor = WaterLevelSensor(sensor_pins['water_pin'])

    water_sensor = WaterLevelSensor(sensor_pins['water_channel'])


    try:
        # 각 센서를 순서대로 읽기
        temp, hum = dht11_sensor.read()
        light_adc, light_voltage = photo_sensor.read()
        co2 = co2_sensor.read() if co2_sensor else None

        water_detected = water_sensor.read()
        
        print(f"[슬롯 {slot}] 센서 읽기 완료!")
        
        return temp, hum, light_adc, water_detected, co2

        soil_adc, soil_voltage = water_sensor.read()
        
        print(f"[슬롯 {slot}] 센서 읽기 완료!")
        
        return temp, hum, light_adc, soil_adc, co2

    
    finally:
        # 센서 리소스 정리
        dht11_sensor.close()
        photo_sensor.close()
        water_sensor.close()


def read_ultrasonic_sensor(trig_pin=23, echo_pin=24):
    """초음파 센서 읽기 (통합 - 슬롯 공유)
    
    Args:
        trig_pin: TRIG 핀 번호 (기본값: 23)
        echo_pin: ECHO 핀 번호 (기본값: 24)
    
    Returns:
        distance: 거리 (cm)
    """
    
    print("\n[통합] 초음파 센서 읽기...")
    
    ultrasonic_sensor = UltrasonicSensor(trig_pin, echo_pin)
    try:
        distance = ultrasonic_sensor.read()
        print(f"[통합] 초음파 센서: {distance} cm")
        return distance
    finally:
        pass  # 초음파 센서는 GPIO만 사용하므로 별도 정리 불필요


if __name__ == "__main__":
    try:
        # 테스트용 센서 핀 설정
        test_pins = {
            'dht11_pin': board.D4,
            'photo_channel': 0,

            'water_pin': board.D26,

            'water_channel': 3,

            'co2_port': '/dev/serial0'
        }
        
        # 슬롯 1 센서 읽기

        temp, hum, light, water, co2 = read_slot_sensors(1, test_pins)
        print(f"\n슬롯 1 센서값: 온도={temp}, 습도={hum}, 조도={light}, 워터={water}, CO2={co2}")

        temp, hum, light, soil, co2 = read_slot_sensors(1, test_pins)
        print(f"\n슬롯 1 센서값: 온도={temp}, 습도={hum}, 조도={light}, 토양={soil}, CO2={co2}")

        
        # 초음파 센서 읽기
        distance = read_ultrasonic_sensor()
        print(f"초음파 센서: {distance} cm")
        
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류 발생: {e}")

