"""
물탱크 모니터링 및 알림 시스템

두 개의 물탱크를 관리:
1. 급수 물탱크 (초음파 센서) - 펌프에 공급하는 물
2. 물받이 물탱크 (워터 센서) - 넘친 물을 받는 곳
"""
import time
from datetime import datetime


class WaterTankMonitor:
    def __init__(self, mqtt_client, device_serial):
        """
        물탱크 모니터링 초기화
        
        Args:
            mqtt_client: MQTT 클라이언트 인스턴스
            device_serial: 디바이스 시리얼 번호 (예: "A1001")
        """
        self.mqtt_client = mqtt_client
        self.device_serial = device_serial
        
        # 급수 물탱크 설정 (초음파 센서)
        self.supply_tank_height = 30  # 탱크 총 높이 (cm)
        self.supply_low_threshold = 5  # 낮음 경고 (cm)
        self.supply_critical_threshold = 3  # 위험 경고 (cm)
        
        # 물받이 물탱크 설정 (워터 센서)
        # True = 물 감지됨 (넘침), False = 정상
        
        # 알림 중복 방지 (마지막 알림 시간)
        self.last_supply_low_alert = 0
        self.last_supply_critical_alert = 0
        self.last_overflow_alert = 0
        
        # 알림 쿨다운 (초) - 같은 알림을 너무 자주 보내지 않도록
        self.alert_cooldown = 300  # 5분
        
        # 상태 추적
        self.supply_status = "정상"  # 정상, 낮음, 위험
        self.overflow_status = "정상"  # 정상, 넘침
    
    def check_supply_tank(self, distance_cm):
        """
        급수 물탱크 수위 체크 (초음파 센서)
        
        Args:
            distance_cm: 초음파 센서로 측정한 거리 (cm)
                        - 센서는 탱크 상단에 부착
                        - 거리가 작을수록 = 수위가 높음
                        - 거리가 클수록 = 수위가 낮음
        
        Returns:
            status: "정상", "낮음", "위험"
        """
        if distance_cm is None:
            print("⚠️  급수탱크: 센서 읽기 실패")
            return self.supply_status
        
        # 수위 계산 (탱크 높이 - 센서 거리 = 물 높이)
        water_level = self.supply_tank_height - distance_cm
        
        current_time = time.time()
        
        # 위험 수준 (거의 비어있음)
        if water_level <= self.supply_critical_threshold:
            status = "위험"
            print(f"🚨 급수탱크: 위험! (수위: {water_level:.1f}cm)")
            
            # 쿨다운 체크 후 알림 전송
            if current_time - self.last_supply_critical_alert > self.alert_cooldown:
                self.send_alert(
                    level="CRITICAL",
                    tank="급수탱크",
                    message=f"급수 물탱크 수위 위험! (수위: {water_level:.1f}cm) 즉시 물을 보충하세요!"
                )
                self.last_supply_critical_alert = current_time
        
        # 낮음 수준
        elif water_level <= self.supply_low_threshold:
            status = "낮음"
            print(f"⚠️  급수탱크: 낮음 (수위: {water_level:.1f}cm)")
            
            # 쿨다운 체크 후 알림 전송
            if current_time - self.last_supply_low_alert > self.alert_cooldown:
                self.send_alert(
                    level="WARNING",
                    tank="급수탱크",
                    message=f"급수 물탱크 수위 낮음 (수위: {water_level:.1f}cm) 물을 보충하세요."
                )
                self.last_supply_low_alert = current_time
        
        # 정상
        else:
            status = "정상"
            print(f"✅ 급수탱크: 정상 (수위: {water_level:.1f}cm)")
        
        self.supply_status = status
        return status
    
    def check_overflow_tank(self, water_detected):
        """
        물받이 물탱크 체크 (워터 센서)
        
        Args:
            water_detected: 물 감지 여부
                          - True: 물이 감지됨 (넘침 발생)
                          - False: 물 없음 (정상)
        
        Returns:
            status: "정상", "넘침"
        """
        if water_detected is None:
            print("⚠️  물받이탱크: 센서 읽기 실패")
            return self.overflow_status
        
        current_time = time.time()
        
        # 물이 감지됨 = 넘침 발생
        if water_detected:
            status = "넘침"
            print(f"🚨 물받이탱크: 넘침 감지!")
            
            # 쿨다운 체크 후 알림 전송
            if current_time - self.last_overflow_alert > self.alert_cooldown:
                self.send_alert(
                    level="WARNING",
                    tank="물받이탱크",
                    message="물받이 탱크에 물이 감지되었습니다! 배수를 확인하세요."
                )
                self.last_overflow_alert = current_time
        
        # 정상
        else:
            status = "정상"
            print(f"✅ 물받이탱크: 정상 (넘침 없음)")
        
        self.overflow_status = status
        return status
    
    def send_alert(self, level, tank, message):
        """
        알림 전송 (MQTT)
        
        Args:
            level: 알림 레벨 ("WARNING", "CRITICAL")
            tank: 탱크 이름 ("급수탱크", "물받이탱크")
            message: 알림 메시지
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 알림 메시지 포맷
        notification = f"[{level}] [{tank}] {message} ({timestamp})"
        
        # MQTT로 알림 전송
        self.mqtt_client.send_notification_logs(notification)
        
        print(f"📢 알림 전송: {notification}")
    
    def get_status_summary(self):
        """
        전체 물탱크 상태 요약
        
        Returns:
            dict: 상태 정보
        """
        return {
            "supply_tank": self.supply_status,
            "overflow_tank": self.overflow_status,
            "alert_status": "정상" if self.supply_status == "정상" and self.overflow_status == "정상" else "주의"
        }
    
    def should_block_watering(self):
        """
        급수 차단 여부 판단
        
        Returns:
            bool: True면 급수 차단, False면 정상 작동
        """
        # 급수탱크가 위험 수준이면 펌프 작동 금지
        if self.supply_status == "위험":
            print("🚫 급수탱크 수위 위험 - 물펌프 작동 차단!")
            return True
        
        # 물받이탱크에 넘침이 감지되면 펌프 작동 금지
        if self.overflow_status == "넘침":
            print("🚫 물받이탱크 넘침 감지 - 물펌프 작동 차단!")
            return True
        
        return False


if __name__ == "__main__":
    # 테스트용 Mock MQTT 클라이언트
    class MockMqttClient:
        def send_notification_logs(self, message):
            print(f"[MQTT] {message}")
    
    # 모니터 초기화
    monitor = WaterTankMonitor(MockMqttClient(), "A1001")
    
    print("\n=== 테스트 1: 급수탱크 정상 ===")
    monitor.check_supply_tank(10)  # 수위 20cm (정상)
    
    print("\n=== 테스트 2: 급수탱크 낮음 ===")
    monitor.check_supply_tank(26)  # 수위 4cm (낮음)
    
    print("\n=== 테스트 3: 급수탱크 위험 ===")
    monitor.check_supply_tank(28)  # 수위 2cm (위험)
    
    print("\n=== 테스트 4: 물받이탱크 정상 ===")
    monitor.check_overflow_tank(False)  # 물 없음 (정상)
    
    print("\n=== 테스트 5: 물받이탱크 넘침 ===")
    monitor.check_overflow_tank(True)  # 물 감지됨 (넘침)
    
    print("\n=== 상태 요약 ===")
    print(monitor.get_status_summary())
    
    print("\n=== 급수 차단 여부 ===")
    print(f"급수 차단: {monitor.should_block_watering()}")
