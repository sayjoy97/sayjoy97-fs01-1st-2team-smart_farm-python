"""
액추에이터 자동 제어 로직
프리셋과 센서값을 비교하여 자동으로 액추에이터를 제어합니다.
"""

class ActuatorController:
    def __init__(self, heater, water_pump, ventilation_fan):
        self.heater = heater
        self.water_pump = water_pump
        self.ventilation_fan = ventilation_fan
        
        # 이전 상태 저장 (불필요한 제어 방지)
        self.last_heater_state = None
        self.last_pump_state = None
        self.last_fan_state = None
    
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
        
        # 프리셋 값 가져오기
        optimal_temp = float(preset.get('OptimalTemp', 25))
        optimal_humidity = float(preset.get('OptimalHumidity', 60))
        optimal_soil = float(preset.get('SoilMoisture', 50))
        
        # 1. 히터 제어 (온도 기반)
        if temp is not None:
            if temp < optimal_temp - 2:  # 온도가 2도 이상 낮으면
                if not self.heater.is_on:
                    self.heater.turn_on()
                    self.last_heater_state = True
            elif temp > optimal_temp + 1:  # 온도가 1도 이상 높으면
                if self.heater.is_on:
                    self.heater.turn_off()
                    self.last_heater_state = False
        
        # 2. 물펌프 제어 (토양 수분 기반)
        if soil is not None:
            # 토양 수분이 낮으면 (ADC 값이 높으면 건조)
            if soil > optimal_soil + 500:  # ADC 값 기준
                if not self.water_pump.is_on:
                    self.water_pump.turn_on()
                    self.last_pump_state = True
            elif soil < optimal_soil - 200:
                if self.water_pump.is_on:
                    self.water_pump.turn_off()
                    self.last_pump_state = False
        
        # 3. 환기팬 제어 (습도 기반)
        if humidity is not None:
            if humidity > optimal_humidity + 10:  # 습도가 10% 이상 높으면
                if not self.ventilation_fan.is_on:
                    self.ventilation_fan.turn_on()
                    self.last_fan_state = True
            elif humidity < optimal_humidity - 5:
                if self.ventilation_fan.is_on:
                    self.ventilation_fan.turn_off()
                    self.last_fan_state = False
    
    def stop_all(self):
        """모든 액추에이터 정지"""
        if self.heater.is_on:
            self.heater.turn_off()
        if self.water_pump.is_on:
            self.water_pump.turn_off()
        if self.ventilation_fan.is_on:
            self.ventilation_fan.turn_off()

