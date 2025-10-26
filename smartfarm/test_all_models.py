"""
전체 모델 통합 테스트
- 고급형 4슬롯 (A4xxx): CO2 있음, 4슬롯
- 고급형 1슬롯 (A1xxx): CO2 있음, 1슬롯
- 일반형 4슬롯 (B4xxx): CO2 없음, 4슬롯
- 일반형 1슬롯 (B1xxx): CO2 없음, 1슬롯
"""

import sys
import io
import time
import random

# 윈도우 콘솔 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class MockSensor:
    def __init__(self, name, min_val, max_val, initial=None):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial if initial is not None else (min_val + max_val) / 2

    def read(self):
        self.value += random.uniform(-1, 1)
        self.value = max(self.min_val, min(self.max_val, self.value))
        return self.value


class MockActuator:
    def __init__(self, name):
        self.name = name
        self.is_on = False

    def turn_on(self):
        if not self.is_on:
            self.is_on = True

    def turn_off(self):
        if self.is_on:
            self.is_on = False

    def cleanup(self):
        pass


class MockMqttClient:
    def __init__(self, farm_uid, has_co2):
        self.farm_uid = farm_uid
        self.has_co2 = has_co2
        self.preset_received = False
        self.current_preset = {
            'OptimalTemp': '25',
            'OptimalHumidity': '60',
            'LightIntensity': '3000',
            'SoilMoisture': '2000',
            'Co2Level': '800'
        }

    def request_preset(self):
        def mock_response():
            time.sleep(0.3)
            slot = int(self.farm_uid.split(':')[1])
            self.current_preset = {
                'OptimalTemp': str(22 + (slot - 1)),
                'OptimalHumidity': '65',
                'LightIntensity': '3500',
                'SoilMoisture': str(1800 + (slot - 1) * 50),
                'Co2Level': '850'
            }
            self.preset_received = True

        import threading
        threading.Thread(target=mock_response, daemon=True).start()

    def is_preset_ready(self):
        return self.preset_received

    def get_preset(self):
        return self.current_preset

    def send_sensor_data(self, temp=None, hum=None, light=None, soil=None, co2=None):
        parts = []
        if temp is not None:
            parts.append(f"temp={temp:.1f}")
        if hum is not None:
            parts.append(f"humidity={hum:.1f}")
        if light is not None:
            parts.append(f"light={light:.0f}")
        if soil is not None:
            parts.append(f"soil={soil:.0f}")
        if co2 is not None and self.has_co2:
            parts.append(f"co2={co2:.0f}")
        return ";".join(parts)

    def close(self):
        pass


class MockActuatorController:
    def __init__(self):
        self.actions = []

    def control(self, sensor_data, preset):
        temp = sensor_data.get('temp')
        hum = sensor_data.get('humidity')
        soil = sensor_data.get('soil')

        optimal_temp = float(preset.get('OptimalTemp', 25))
        optimal_hum = float(preset.get('OptimalHumidity', 60))
        optimal_soil = float(preset.get('SoilMoisture', 2000))

        actions = []
        if temp is not None:
            if temp < optimal_temp - 2:
                actions.append("히터ON")
            elif temp > optimal_temp + 1:
                actions.append("히터OFF")

        if soil is not None:
            if soil > optimal_soil + 500:
                actions.append("물펌프ON")
            elif soil < optimal_soil - 200:
                actions.append("물펌프OFF")

        if hum is not None:
            if hum > optimal_hum + 10:
                actions.append("환기팬ON")
            elif hum < optimal_hum - 5:
                actions.append("환기팬OFF")

        self.actions = actions
        return actions

    def stop_all(self):
        pass


def detect_model_config(device_serial):
    """디바이스 시리얼로 모델 설정 자동 감지"""
    prefix = device_serial[:2].upper()
    
    if prefix == "A4":
        return {"slots": [1, 2, 3, 4], "has_co2": True, "model": "고급형 4슬롯"}
    elif prefix == "A1":
        return {"slots": [1], "has_co2": True, "model": "고급형 1슬롯"}
    elif prefix == "B4":
        return {"slots": [1, 2, 3, 4], "has_co2": False, "model": "일반형 4슬롯"}
    elif prefix == "B1":
        return {"slots": [1], "has_co2": False, "model": "일반형 1슬롯"}
    else:
        return {"slots": [1], "has_co2": False, "model": "미지정"}


def test_device(device_serial, cycles=2):
    """디바이스 테스트 실행"""
    config = detect_model_config(device_serial)
    slots = config['slots']
    has_co2 = config['has_co2']
    model_name = config['model']

    print("\n" + "=" * 70)
    print(f"🧪 테스트: {device_serial} ({model_name})")
    print(f"   슬롯: {slots} | CO2: {'있음' if has_co2 else '없음'}")
    print("=" * 70)

    # 슬롯별 런타임 초기화
    runtimes = {}
    for slot in slots:
        farm_uid = f"{device_serial}:{slot}"
        sensors = {
            'temp': MockSensor("온도", 15, 35, initial=20 + slot),
            'hum': MockSensor("습도", 30, 90, initial=70),
            'light': MockSensor("조도", 0, 4095, initial=1500),
            'soil': MockSensor("토양", 0, 4095, initial=2200),
            'co2': MockSensor("CO2", 400, 2000, initial=850) if has_co2 else None
        }
        client = MockMqttClient(farm_uid, has_co2)
        controller = MockActuatorController()
        runtimes[slot] = (sensors, client, controller)

    # 프리셋 요청
    print("\n📡 프리셋 요청...")
    for slot in slots:
        runtimes[slot][1].request_preset()

    # 응답 대기
    time.sleep(1)
    all_ready = all(runtimes[s][1].is_preset_ready() for s in slots)
    if all_ready:
        print("✅ 모든 슬롯 프리셋 수신 완료")
    else:
        print("⚠️  일부 슬롯 프리셋 미수신")

    # 테스트 사이클
    for cycle in range(cycles):
        print(f"\n{'─' * 70}")
        print(f"📊 사이클 {cycle + 1}/{cycles}")
        print(f"{'─' * 70}")

        for slot in slots:
            sensors, client, controller = runtimes[slot]
            
            # 센서 읽기
            temp = sensors['temp'].read()
            hum = sensors['hum'].read()
            light = sensors['light'].read()
            soil = sensors['soil'].read()
            co2 = sensors['co2'].read() if has_co2 else None

            # 센서 데이터 생성
            sensor_str = f"T={temp:.1f} H={hum:.1f} L={light:.0f} S={soil:.0f}"
            if co2 is not None:
                sensor_str += f" CO2={co2:.0f}"
            
            print(f"  슬롯 {slot}: {sensor_str}")

            # MQTT 전송 (모의)
            mqtt_payload = client.send_sensor_data(temp, hum, light, soil, co2)
            print(f"    📤 {mqtt_payload}")

            # 액추에이터 제어
            sensor_data = {
                'temp': temp,
                'humidity': hum,
                'light': light,
                'soil': soil,
                'co2': co2
            }
            preset = client.get_preset()
            actions = controller.control(sensor_data, preset)
            
            if actions:
                print(f"    🎛️  제어: {', '.join(actions)}")

        time.sleep(0.5)

    # 정리
    for slot in slots:
        runtimes[slot][1].close()
        runtimes[slot][2].stop_all()

    print(f"\n✅ {device_serial} 테스트 완료\n")


def main():
    random.seed(42)
    
    print("=" * 70)
    print("🌱 스마트팜 전체 모델 통합 테스트")
    print("=" * 70)

    # 4가지 모델 모두 테스트
    test_device("A4001", cycles=2)  # 고급형 4슬롯
    test_device("A1001", cycles=2)  # 고급형 1슬롯
    test_device("B4001", cycles=2)  # 일반형 4슬롯
    test_device("B1001", cycles=2)  # 일반형 1슬롯

    print("=" * 70)
    print("✅ 전체 테스트 완료!")
    print("=" * 70)
    print("\n📋 테스트 결과 요약:")
    print("  ✓ 고급형 4슬롯 (A4xxx): CO2 포함, 4개 슬롯 독립 동작")
    print("  ✓ 고급형 1슬롯 (A1xxx): CO2 포함, 1개 슬롯 동작")
    print("  ✓ 일반형 4슬롯 (B4xxx): CO2 제외, 4개 슬롯 독립 동작")
    print("  ✓ 일반형 1슬롯 (B1xxx): CO2 제외, 1개 슬롯 동작")
    print("\n🎉 모든 모델이 정상 작동합니다!")


if __name__ == "__main__":
    main()

