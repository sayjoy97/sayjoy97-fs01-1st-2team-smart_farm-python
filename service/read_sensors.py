from sensor.dht11 import DHT11
from sensor.photoresister import PhotoResister
from sensor.MH_Z19B import CO2Sensor
from sensor.HC_SR04 import UltrasonicSensor
from sensor.water import WaterLevelSensor
from sensor.soil_moisture import SoilMoistureSensor
from service.sensor_cache import SensorCache
from mqtt.mqtt_client import MqttClient
import board


# 전역 캐시 저장소
_dht11_caches = {}
_co2_caches = {}


def init_sensor_caches(slot, sensor_pins, has_co2=True):
    """슬롯별 센서 캐시 초기화"""
    global _dht11_caches, _co2_caches
    
    # DHT11 캐시
    if slot not in _dht11_caches:
        dht11 = DHT11(sensor_pins['dht11_pin'])
        _dht11_caches[slot] = SensorCache(dht11, "DHT11")
        _dht11_caches[slot].start()
    
    # CO2 캐시
    if has_co2 and 'co2_port' in sensor_pins and sensor_pins['co2_port']:
        if slot not in _co2_caches:
            co2 = CO2Sensor(sensor_pins['co2_port'])
            _co2_caches[slot] = SensorCache(co2, "CO2")
            _co2_caches[slot].start()


def stop_sensor_caches():
    """모든 센서 캐시 중지"""
    for cache in _dht11_caches.values():
        cache.stop()
    for cache in _co2_caches.values():
        cache.stop()
    _dht11_caches.clear()
    _co2_caches.clear()


def read_slot_sensors(slot, sensor_pins, has_co2=True):
    """슬롯별 센서 값 읽기 (캐시 사용)"""
    
    # 안정적인 센서 (즉시 읽기)
    photo_sensor = PhotoResister(sensor_pins['photo_channel'])
    soil_sensor = SoilMoistureSensor(sensor_pins['soil_channel'])

    try:
        # DHT11 - 캐시에서 가져오기
        temp, hum = None, None
        if slot in _dht11_caches:
            value = _dht11_caches[slot].get()
            if value:
                temp, hum = value
        
        # 조도, 토양 - 즉시 읽기
        light_adc, _ = photo_sensor.read()
        soil_adc, _ = soil_sensor.read()
        
        # CO2 - 캐시에서 가져오기
        co2 = None
        if has_co2 and slot in _co2_caches:
            co2 = _co2_caches[slot].get()
        
        return temp, hum, light_adc, soil_adc, co2
    
    finally:
        photo_sensor.close()
        soil_sensor.close()


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


def read_water_tank_sensor(water_pin):
    """물통 수위 센서 읽기 (통합 - 슬롯 공유)
    
    Args:
        water_pin: GPIO 핀 (기본값: board.D26)
    
    Returns:
        water_detected: True(물 있음), False(물 없음)
    """
    
    print("\n[통합] 물통 수위 센서 읽기...")
    
    water_sensor = WaterLevelSensor(water_pin)
    try:
        water_detected = water_sensor.read()
        status = "정상" if water_detected else "낮음 (보충 필요)"
        print(f"[통합] 물통 수위: {status}")
        return water_detected
    finally:
        water_sensor.close()


if __name__ == "__main__":
    try:
        # 테스트용 센서 핀 설정
        test_pins = {
            'dht11_pin': board.D4,
            'photo_channel': 0,
            'soil_channel': 0,
            'co2_port': '/dev/serial0'
        }
        
        # 슬롯 1 센서 읽기
        temp, hum, light, soil, co2 = read_slot_sensors(1, test_pins)
        print(f"\n슬롯 1 센서값: 온도={temp}, 습도={hum}, 조도={light}, 토양={soil}, CO2={co2}")
        
        # 초음파 센서 읽기
        distance = read_ultrasonic_sensor()
        print(f"초음파 센서: {distance} cm")
        
        # 물통 수위 센서 읽기
        water_ok = read_water_tank_sensor(board.D26)
        print(f"물통 수위: {'정상' if water_ok else '낮음'}")
        
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류 발생: {e}")

