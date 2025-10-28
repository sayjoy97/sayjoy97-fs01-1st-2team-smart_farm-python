import mh_z19

class CO2Sensor:
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