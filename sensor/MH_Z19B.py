import mh_z19

class CO2Sensor:
    def __init__(self, device='/dev/serial0'):
        """
        CO2 센서 초기화 (MH-Z19B)
        
        Args:
            device: 시리얼 포트 (기본값: /dev/serial0)
        """
        self.device = device
    
    def read(self):
        """
        CO2 농도 읽기
        
        Returns:
            co2_value: CO2 농도 (ppm), 실패 시 None
        """
        try:
            # mh_z19 라이브러리는 serial_console_untouched 파라미터 사용
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
        """센서 정리 (라이브러리가 자동 처리)"""
        pass


if __name__ == "__main__":
    sensor = CO2Sensor()
    co2 = sensor.read()
    if co2:
        print(f"CO2 농도: {co2} ppm")
    else:
        print("CO2 센서 읽기 실패")
