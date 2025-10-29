import mh_z19

class CO2Sensor:

    def __init__(self, device='/dev/serial0'):
        self.device = device
    
    def read(self):
        try:
            # mh_z19 라이브러리는 serial_device 대신 serial_console_untouched 파라미터 사용
            result = mh_z19.read_all(serial_console_untouched=True)
            
            if result and 'co2' in result:
                co2_value = result['co2']
                print(f"CO2 센서: {co2_value} ppm")
                return co2_value
            else:
                print("CO2 센서: 읽기 실패")
                return None
        except Exception as e:
            print(f"CO2 센서 오류: {e}")
            return None
    
    def close(self):
        pass

if __name__ == "__main__":
    sensor = CO2Sensor()
    co2 = sensor.read()
    print(f"CO2 농도: {co2} ppm")

    def __init__(self, device=None):
        self.device = device  # 기본은 /dev/serial0

    def read(self):
        """CO2 농도 읽기"""
        result = mh_z19.read(serial_device=self.device)
        if result and "co2" in result:
            return result["co2"]
        return None


if __name__ == "__main__":
    sensor = CO2Sensor("/dev/serial0")
    co2 = sensor.read()
    print(f"CO₂ 농도: {co2} ppm")

