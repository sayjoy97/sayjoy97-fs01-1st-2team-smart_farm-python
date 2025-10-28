"""
액추에이터 자동 제어 로직
프리셋과 센서값을 비교하여 자동으로 액추에이터를 제어합니다.
"""
from datetime import datetime

class ActuatorController:
    def __init__(self, heater, water_pump, ventilation_fan, led, water_monitor, co2_servo=None):
        self.heater = heater
        self.water_pump = water_pump
        self.ventilation_fan = ventilation_fan
        self.led = led  # LED 조명
        self.water_monitor = water_monitor  # 물탱크 모니터 
        self.co2_servo = co2_servo  # CO2 카트리지 제어용 서보 (옵션)
        self.co2_release_angle = 90
        self.co2_idle_angle = 0
        self.co2_low_margin = 150
        self.co2_recover_margin = 50
        self.is_servo_releasing = False
        
        # 이전 상태 저장 (불필요한 제어 방지)
        self.last_heater_state = None
        self.last_pump_state = None
        self.last_fan_state = None
        self.last_led_state = None

        if self.co2_servo:
            # 시작 시 CO2 카트리지를 닫힌 상태로 맞춰둡니다.
            self.co2_servo.set_angle(self.co2_idle_angle)
    
    def control(self, sensor_data, preset):
        """
        센서 데이터와 프리셋을 비교하여 액추에이터 제어
        
        Args:
            sensor_data: dict with keys: temp, humidity, light, soil, co2
            preset: dict with keys: OptimalTemp, OptimalHumidity, LightIntensity, SoilMoisture, Co2Level
        """
        if not preset:
            print("⚠️  프리셋 없음 - 액추에이터 제어 대기 중")
            return
        
        temp = sensor_data.get('temp')
        humidity = sensor_data.get('humidity')
        soil = sensor_data.get('soil')
        co2 = sensor_data.get('co2')
        light = sensor_data.get('light')  # 조도 값 추가
        
        # 프리셋 값 가져오기
        optimal_temp = float(preset.get('OptimalTemp', 25))
        optimal_humidity = float(preset.get('OptimalHumidity', 60))
        optimal_soil = float(preset.get('SoilMoisture', 50))
        optimal_co2 = float(preset.get('Co2Level', 800))
        optimal_light = float(preset.get('LightIntensity', 5000))  # 조도 프리셋 추가
        
        # 1. 히터 및 환풍팬 제어 (온도 기반)
        if temp is not None:
            if temp < optimal_temp - 2:  # 온도가 2도 이상 낮으면
                if not self.heater.is_on:
                    self.heater.turn_on()
                    self.last_heater_state = True
                # 온도가 낮을 때는 환풍팬 끄기
                if self.ventilation_fan.is_on:
                    self.ventilation_fan.turn_off()
                    self.last_fan_state = False
            elif temp > optimal_temp + 2:  # 온도가 2도 이상 높으면
                if self.heater.is_on:
                    self.heater.turn_off()
                    self.last_heater_state = False
                # 온도가 높을 때는 환풍팬 켜서 냉각
                if not self.ventilation_fan.is_on:
                    self.ventilation_fan.turn_on()
                    self.last_fan_state = True
            elif optimal_temp - 2 <= temp <= optimal_temp + 2:  # 적정 온도 범위
                # 온도가 적정 범위일 때는 히터만 끄고, 환풍팬은 습도 제어에 맡김
                if self.heater.is_on:
                    self.heater.turn_off()
                    self.last_heater_state = False
        
        # 2. 물펌프 제어 (토양 수분 기반) + 물탱크 안전 체크
        if soil is not None:
            # 물탱크 안전 체크 (급수탱크 위험 또는 물받이탱크 넘침 시 차단)
            if self.water_monitor.should_block_watering():
                # 물탱크 문제 발생 - 펌프 강제 정지
                if self.water_pump.is_on:
                    print("🚫 물탱크 문제로 펌프 강제 정지!")
                    self.water_pump.turn_off()
                    self.last_pump_state = False
            else:
                # 정상 - 토양 수분 기반 제어
                if soil > optimal_soil + 500:  # ADC 값 기준 (값이 높으면 건조)
                    if not self.water_pump.is_on:
                        self.water_pump.turn_on()
                        self.last_pump_state = True
                elif soil < optimal_soil - 200:
                    if self.water_pump.is_on:
                        self.water_pump.turn_off()
                        self.last_pump_state = False
        
        # 3. 환기팬 제어 (습도 기반) - 온도 제어가 우선순위
        # 온도가 높아서 이미 팬이 켜진 경우는 습도 제어를 건너뜀
        if humidity is not None and temp is not None:
            # 온도가 정상 범위이고 습도만 높을 때
            if optimal_temp - 2 <= temp <= optimal_temp + 2:
                if humidity > optimal_humidity + 10:  # 습도가 10% 이상 높으면
                    if not self.ventilation_fan.is_on:
                        self.ventilation_fan.turn_on()
                        self.last_fan_state = True
                elif humidity < optimal_humidity - 5:
                    if self.ventilation_fan.is_on:
                        self.ventilation_fan.turn_off()
                        self.last_fan_state = False

        # 4. LED 조명 제어 (조도 기반 + 시간 제한: 8시~22시)
        if light is not None:
            current_hour = datetime.now().hour
            
            # LED 작동 시간대 체크 (8시~22시)
            if 8 <= current_hour < 22:
                # 조도가 낮으면 LED 켜기 (광합성 보조)
                if light < optimal_light - 1000:  # 기준값보다 1000 lux 낮으면
                    if not self.led.is_on:
                        self.led.turn_on()
                        self.last_led_state = True
                # 조도가 충분하면 LED 끄기 (에너지 절약)
                elif light > optimal_light + 500:  # 기준값보다 500 lux 높으면
                    if self.led.is_on:
                        self.led.turn_off()
                        self.last_led_state = False
            else:
                # 작동 시간대가 아니면 LED 끄기 (22시~8시)
                if self.led.is_on:
                    self.led.turn_off()
                    self.last_led_state = False

        # 5. CO2 제어 (서보 기반)
        if self.co2_servo and co2 is not None:
            release_threshold = max(0.0, optimal_co2 - self.co2_low_margin)
            recovery_threshold = max(release_threshold + self.co2_recover_margin, release_threshold + 10)
            recovery_threshold = min(optimal_co2, recovery_threshold)

            if co2 < release_threshold:
                if not self.is_servo_releasing:
                    print("🫧 CO2 낮음 - 서보모터로 카트리지 개방")
                    self.co2_servo.set_angle(self.co2_release_angle)
                    self.is_servo_releasing = True
            elif co2 >= recovery_threshold:
                if self.is_servo_releasing:
                    print("✅ CO2 정상화 - 서보모터 원위치")
                    self.co2_servo.set_angle(self.co2_idle_angle)
                    self.is_servo_releasing = False
    
    def stop_all(self):
        """모든 액추에이터 정지"""
        if self.heater.is_on:
            self.heater.turn_off()
        if self.water_pump.is_on:
            self.water_pump.turn_off()
        if self.ventilation_fan.is_on:
            self.ventilation_fan.turn_off()
        if self.led.is_on:
            self.led.turn_off()
        if self.co2_servo and self.is_servo_releasing:
            self.co2_servo.set_angle(self.co2_idle_angle)
            self.is_servo_releasing = False

