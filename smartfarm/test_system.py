"""
스마트팜 시스템 모의 테스트
라즈베리파이 없이 로직을 검증합니다.
"""

import time
import threading
import sys
import io

# 윈도우 콘솔 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 모의 센서 클래스
class MockSensor:
    def __init__(self, name, min_val, max_val):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.value = (min_val + max_val) / 2
    
    def read(self):
        # 랜덤하게 값 변화
        import random
        self.value += random.uniform(-2, 2)
        self.value = max(self.min_val, min(self.max_val, self.value))
        return self.value

# 모의 액추에이터 클래스
class MockActuator:
    def __init__(self, name):
        self.name = name
        self.is_on = False
    
    def turn_on(self):
        if not self.is_on:
            self.is_on = True
            print(f"    🟢 {self.name} ON")
    
    def turn_off(self):
        if self.is_on:
            self.is_on = False
            print(f"    ⚪ {self.name} OFF")
    
    def cleanup(self):
        pass

# 모의 MQTT 클라이언트
class MockMqttClient:
    def __init__(self, device_serial):
        self.device_serial = device_serial
        self.current_preset = {
            'OptimalTemp': '25',
            'OptimalHumidity': '60',
            'LightIntensity': '3000',
            'SoilMoisture': '2000',
            'Co2Level': '800'
        }
        self.preset_received = False
        print(f"✅ MQTT 클라이언트 초기화 (디바이스: {device_serial})")
    
    def request_preset(self):
        print(f"📡 프리셋 요청: smartfarm/{self.device_serial}/preset/request")
        # 모의 응답 (1초 후)
        def mock_response():
            time.sleep(1)
            # DB에 데이터가 있다고 가정
            self.current_preset = {
                'OptimalTemp': '22',
                'OptimalHumidity': '65',
                'LightIntensity': '3500',
                'SoilMoisture': '1800',
                'Co2Level': '850'
            }
            self.preset_received = True
            print(f"✅ 프리셋 수신 완료!")
            print(f"   온도: {self.current_preset['OptimalTemp']}°C")
            print(f"   습도: {self.current_preset['OptimalHumidity']}%")
        
        threading.Thread(target=mock_response, daemon=True).start()
    
    def is_preset_ready(self):
        return self.preset_received
    
    def get_preset(self):
        return self.current_preset
    
    def send_sensor_data(self, temp, hum, light, soil, co2):
        data = f"temp={temp:.1f};humidity={hum:.1f};measuredLight={light:.0f};soil={soil:.0f}"
        if co2:
            data += f";co2={co2:.0f}"
        print(f"📤 센서 데이터: {data}")
    
    def close(self):
        print("🔌 MQTT 연결 종료")

# 모의 액추에이터 컨트롤러
class MockActuatorController:
    def __init__(self, heater, water_pump, ventilation_fan):
        self.heater = heater
        self.water_pump = water_pump
        self.ventilation_fan = ventilation_fan
    
    def control(self, sensor_data, preset):
        if not preset:
            return
        
        temp = sensor_data.get('temp')
        humidity = sensor_data.get('humidity')
        soil = sensor_data.get('soil')
        
        optimal_temp = float(preset.get('OptimalTemp', 25))
        optimal_humidity = float(preset.get('OptimalHumidity', 60))
        optimal_soil = float(preset.get('SoilMoisture', 2000))
        
        print(f"\n🎛️  자동 제어 판단:")
        print(f"   온도: {temp:.1f}°C (목표: {optimal_temp}°C)")
        print(f"   습도: {humidity:.1f}% (목표: {optimal_humidity}%)")
        print(f"   토양: {soil:.0f} (목표: {optimal_soil})")
        
        # 히터 제어
        if temp < optimal_temp - 2:
            self.heater.turn_on()
        elif temp > optimal_temp + 1:
            self.heater.turn_off()
        
        # 물펌프 제어
        if soil > optimal_soil + 500:
            self.water_pump.turn_on()
        elif soil < optimal_soil - 200:
            self.water_pump.turn_off()
        
        # 환기팬 제어
        if humidity > optimal_humidity + 10:
            self.ventilation_fan.turn_on()
        elif humidity < optimal_humidity - 5:
            self.ventilation_fan.turn_off()
    
    def stop_all(self):
        self.heater.turn_off()
        self.water_pump.turn_off()
        self.ventilation_fan.turn_off()

def main():
    print("=" * 60)
    print("🧪 스마트팜 시스템 모의 테스트")
    print("=" * 60)
    
    # 모의 센서 초기화
    temp_sensor = MockSensor("온도", 15, 35)
    temp_sensor.value = 20  # 초기값: 20°C (목표 22보다 낮음)
    
    humidity_sensor = MockSensor("습도", 30, 90)
    humidity_sensor.value = 78  # 초기값: 78% (목표 65보다 높음)
    
    light_sensor = MockSensor("조도", 0, 4095)
    light_sensor.value = 1500
    
    soil_sensor = MockSensor("토양", 0, 4095)
    soil_sensor.value = 2400  # 초기값: 2400 (목표 1800보다 높음, 건조)
    
    co2_sensor = MockSensor("CO2", 400, 2000)
    co2_sensor.value = 850
    
    # 모의 액추에이터 초기화
    heater = MockActuator("히터")
    water_pump = MockActuator("물펌프")
    ventilation_fan = MockActuator("환기팬")
    
    # 컨트롤러 초기화
    controller = MockActuatorController(heater, water_pump, ventilation_fan)
    
    # MQTT 클라이언트 초기화
    client = MockMqttClient("A1001")
    
    # 프리셋 요청
    print("\n📡 DB 서버에 프리셋 요청...")
    client.request_preset()
    
    # 프리셋 응답 대기
    wait_count = 0
    while not client.is_preset_ready() and wait_count < 5:
        print(f"⏳ 응답 대기 중... ({wait_count + 1}/5초)")
        time.sleep(1)
        wait_count += 1
    
    print("\n" + "=" * 60)
    print("💡 센서 데이터 전송 및 자동 제어 시작")
    print("=" * 60)
    
    try:
        for cycle in range(5):  # 5회 반복
            print(f"\n{'=' * 60}")
            print(f"📊 사이클 {cycle + 1}/5")
            print(f"{'=' * 60}")
            
            # 센서 읽기
            temp = temp_sensor.read()
            hum = humidity_sensor.read()
            light = light_sensor.read()
            soil = soil_sensor.read()
            co2 = co2_sensor.read()
            
            print(f"📡 센서 읽기:")
            print(f"   온도: {temp:.1f}°C")
            print(f"   습도: {hum:.1f}%")
            print(f"   조도: {light:.0f}")
            print(f"   토양: {soil:.0f}")
            print(f"   CO2: {co2:.0f} ppm")
            
            # 센서 데이터 전송
            client.send_sensor_data(temp, hum, light, soil, co2)
            
            # 액추에이터 자동 제어
            sensor_data = {
                'temp': temp,
                'humidity': hum,
                'light': light,
                'soil': soil,
                'co2': co2
            }
            preset = client.get_preset()
            controller.control(sensor_data, preset)
            
            # 제어 후 센서값 변화 시뮬레이션
            if heater.is_on:
                temp_sensor.value += 1.5  # 히터로 온도 상승
            if water_pump.is_on:
                soil_sensor.value -= 300  # 물펌프로 수분 증가
            if ventilation_fan.is_on:
                humidity_sensor.value -= 5  # 환기팬으로 습도 감소
            
            time.sleep(2)  # 2초 대기
        
        print("\n" + "=" * 60)
        print("✅ 테스트 완료!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 테스트 중단됨")
    
    finally:
        controller.stop_all()
        client.close()
        print("\n✅ 시스템 종료\n")

if __name__ == "__main__":
    main()

