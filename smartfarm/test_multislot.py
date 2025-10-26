"""
멀티슬롯 모의 테스트 (하드웨어/브로커 없이 로직 검증)
 - 1슬롯과 4슬롯 시나리오를 연속 실행
 - 슬롯별 센서/액추에이터/프리셋을 각각 독립적으로 처리
"""

import time
import threading
import sys
import io
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
        self.value += random.uniform(-2, 2)
        self.value = max(self.min_val, min(self.max_val, self.value))
        return self.value


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


class MockMqttClient:
    def __init__(self, farm_uid):
        self.farm_uid = farm_uid  # 예: A1001:1
        self.device_serial = farm_uid.split(':')[0]
        self.current_preset = {
            'OptimalTemp': '25',
            'OptimalHumidity': '60',
            'LightIntensity': '3000',
            'SoilMoisture': '2000',
            'Co2Level': '800'
        }
        self.preset_received = False

    def request_preset(self):
        print(f"📡 프리셋 요청: smartfarm/{self.farm_uid}/preset/request")

        def mock_response():
            time.sleep(0.5)
            # 슬롯별로 약간 다른 프리셋 부여
            slot = int(self.farm_uid.split(':')[1])
            self.current_preset = {
                'OptimalTemp': str(22 + (slot - 1)),
                'OptimalHumidity': '65',
                'LightIntensity': '3500',
                'SoilMoisture': str(1800 + (slot - 1) * 50),
                'Co2Level': '850'
            }
            self.preset_received = True
            print(f"✅ 프리셋 수신 ({self.farm_uid}) → {self.current_preset}")

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
            parts.append(f"measuredLight={light:.0f}")
        if soil is not None:
            parts.append(f"soil={soil:.0f}")
        if co2 is not None:
            parts.append(f"co2={co2:.0f}")
        data = ";".join(parts) if parts else ""
        print(f"📤 [{self.farm_uid}] 센서 데이터: {data}")

    def close(self):
        pass


class MockActuatorController:
    def __init__(self, heater, water_pump, ventilation_fan):
        self.heater = heater
        self.water_pump = water_pump
        self.ventilation_fan = ventilation_fan

    def control(self, sensor_data, preset):
        if not preset:
            return
        temp = sensor_data.get('temp')
        hum = sensor_data.get('humidity')
        soil = sensor_data.get('soil')

        optimal_temp = float(preset.get('OptimalTemp', 25))
        optimal_humidity = float(preset.get('OptimalHumidity', 60))
        optimal_soil = float(preset.get('SoilMoisture', 2000))

        print(f"   제어 기준: T={optimal_temp} H={optimal_humidity} S={optimal_soil}")

        if temp is not None:
            if temp < optimal_temp - 2:
                self.heater.turn_on()
            elif temp > optimal_temp + 1:
                self.heater.turn_off()

        if soil is not None:
            if soil > optimal_soil + 500:
                self.water_pump.turn_on()
            elif soil < optimal_soil - 200:
                self.water_pump.turn_off()

        if hum is not None:
            if hum > optimal_humidity + 10:
                self.ventilation_fan.turn_on()
            elif hum < optimal_humidity - 5:
                self.ventilation_fan.turn_off()

    def stop_all(self):
        self.heater.turn_off()
        self.water_pump.turn_off()
        self.ventilation_fan.turn_off()


def build_slot_runtime(device_serial, slot):
    farm_uid = f"{device_serial}:{slot}"
    # 슬롯별 센서 세트
    sensors = {
        'temp': MockSensor("온도", 15, 35, initial=20 + (slot - 1)),
        'hum': MockSensor("습도", 30, 90, initial=75 - (slot - 1) * 3),
        'light': MockSensor("조도", 0, 4095, initial=1500 + (slot - 1) * 10),
        'soil': MockSensor("토양", 0, 4095, initial=2300 + (slot - 1) * 50),
        'co2': MockSensor("CO2", 400, 2000, initial=850)
    }
    # 액추에이터
    heater = MockActuator(f"히터@S{slot}")
    water = MockActuator(f"물펌프@S{slot}")
    fan = MockActuator(f"환기팬@S{slot}")
    controller = MockActuatorController(heater, water, fan)
    client = MockMqttClient(farm_uid)
    return sensors, controller, client


def run_test(device_serial, slots, cycles=3):
    print("=" * 70)
    print(f"🧪 멀티슬롯 모의 테스트 시작 | 디바이스={device_serial} | 슬롯={slots}")
    print("=" * 70)

    runtimes = {}
    for s in slots:
        sensors, controller, client = build_slot_runtime(device_serial, s)
        runtimes[s] = (sensors, controller, client)

    # 프리셋 요청
    print("\n📡 프리셋 요청...")
    for s in slots:
        runtimes[s][2].request_preset()

    # 응답 대기 (최대 3초)
    for i in range(6):
        if all(runtimes[s][2].is_preset_ready() for s in slots):
            break
        print(f"⏳ 응답 대기... ({i+1}/6)")
        time.sleep(0.5)

    print("\n✅ 프리셋 정리")
    for s in slots:
        print(f"  슬롯 {s}: {runtimes[s][2].get_preset()}")

    # 사이클 반복
    for c in range(cycles):
        print(f"\n{'-'*70}")
        print(f"📊 사이클 {c+1}/{cycles}")
        print(f"{'-'*70}")
        for s in slots:
            sensors, controller, client = runtimes[s]
            temp = sensors['temp'].read()
            hum = sensors['hum'].read()
            light = sensors['light'].read()
            soil = sensors['soil'].read()
            co2 = sensors['co2'].read()

            print(f"[S{s}] 센서: T={temp:.1f} H={hum:.1f} L={light:.0f} S={soil:.0f} CO2={co2:.0f}")
            client.send_sensor_data(temp, hum, light, soil, co2)

            sensor_data = {'temp': temp, 'humidity': hum, 'light': light, 'soil': soil, 'co2': co2}
            preset = client.get_preset()
            controller.control(sensor_data, preset)

            # 제어 효과 시뮬레이션
            if controller.heater.is_on:
                sensors['temp'].value += 1.2
            if controller.water_pump.is_on:
                sensors['soil'].value -= 250
            if controller.ventilation_fan.is_on:
                sensors['hum'].value -= 4

        time.sleep(1)

    # 종료 정리
    for s in slots:
        sensors, controller, client = runtimes[s]
        controller.stop_all()
        client.close()

    print("\n✅ 테스트 종료\n")


def main():
    random.seed(42)
    # 1슬롯 테스트
    run_test("A1001", [1], cycles=3)
    # 4슬롯 테스트
    run_test("A1001", [1, 2, 3, 4], cycles=3)


if __name__ == "__main__":
    main()


