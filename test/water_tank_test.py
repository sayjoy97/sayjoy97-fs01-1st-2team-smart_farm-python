"""
물탱크 모니터링 시스템 테스트

급수 물탱크와 물받이 물탱크를 시뮬레이션하여 
알림 시스템이 정상 작동하는지 테스트합니다.
"""
import time
from service.water_tank_monitor import WaterTankMonitor


class MockMqttClient:
    """테스트용 Mock MQTT 클라이언트"""
    def __init__(self, device_serial):
        self.device_serial = device_serial
        self.notifications = []
    
    def send_notification_logs(self, message):
        print(f"\n📢 [MQTT 알림] {message}")
        self.notifications.append(message)


def test_water_tank_monitor():
    """물탱크 모니터 전체 시나리오 테스트"""
    
    print("=" * 70)
    print("💧 물탱크 모니터링 시스템 테스트")
    print("=" * 70)
    
    # Mock 클라이언트 및 모니터 초기화
    mock_mqtt = MockMqttClient("A1001")
    monitor = WaterTankMonitor(mock_mqtt, "A1001")
    
    print("\n📋 설정 정보:")
    print(f"   - 급수탱크 총 높이: {monitor.supply_tank_height}cm")
    print(f"   - 급수탱크 낮음 경고: {monitor.supply_low_threshold}cm")
    print(f"   - 급수탱크 위험 경고: {monitor.supply_critical_threshold}cm")
    print(f"   - 알림 쿨다운: {monitor.alert_cooldown}초 ({monitor.alert_cooldown/60}분)")
    
    # ========================================
    # 시나리오 1: 급수탱크 정상 → 낮음 → 위험
    # ========================================
    print("\n\n" + "=" * 70)
    print("📝 시나리오 1: 급수탱크 수위 감소")
    print("=" * 70)
    
    print("\n[1-1] 급수탱크 정상 상태 (수위 20cm)")
    distance = 10  # 센서 거리 10cm = 수위 20cm
    status = monitor.check_supply_tank(distance)
    assert status == "정상", f"예상: 정상, 실제: {status}"
    print(f"   ✅ 상태: {status}")
    
    time.sleep(1)
    
    print("\n[1-2] 급수탱크 낮음 상태 (수위 4cm)")
    distance = 26  # 센서 거리 26cm = 수위 4cm
    status = monitor.check_supply_tank(distance)
    assert status == "낮음", f"예상: 낮음, 실제: {status}"
    print(f"   ✅ 상태: {status}")
    print(f"   📢 알림 전송됨: {len(mock_mqtt.notifications)}개")
    
    time.sleep(1)
    
    print("\n[1-3] 급수탱크 위험 상태 (수위 2cm)")
    distance = 28  # 센서 거리 28cm = 수위 2cm
    status = monitor.check_supply_tank(distance)
    assert status == "위험", f"예상: 위험, 실제: {status}"
    print(f"   ✅ 상태: {status}")
    print(f"   📢 알림 전송됨: {len(mock_mqtt.notifications)}개")
    
    # ========================================
    # 시나리오 2: 물받이탱크 정상 → 넘침
    # ========================================
    print("\n\n" + "=" * 70)
    print("📝 시나리오 2: 물받이탱크 넘침 감지")
    print("=" * 70)
    
    print("\n[2-1] 물받이탱크 정상 상태 (물 없음)")
    water_detected = False
    status = monitor.check_overflow_tank(water_detected)
    assert status == "정상", f"예상: 정상, 실제: {status}"
    print(f"   ✅ 상태: {status}")
    
    time.sleep(1)
    
    print("\n[2-2] 물받이탱크 넘침 발생 (물 감지됨)")
    water_detected = True
    status = monitor.check_overflow_tank(water_detected)
    assert status == "넘침", f"예상: 넘침, 실제: {status}"
    print(f"   ✅ 상태: {status}")
    print(f"   📢 알림 전송됨: {len(mock_mqtt.notifications)}개")
    
    # ========================================
    # 시나리오 3: 급수 차단 로직 테스트
    # ========================================
    print("\n\n" + "=" * 70)
    print("📝 시나리오 3: 급수 차단 로직")
    print("=" * 70)
    
    print("\n[3-1] 급수탱크 위험 상태 - 급수 차단 확인")
    should_block = monitor.should_block_watering()
    assert should_block == True, f"예상: True (차단), 실제: {should_block}"
    print(f"   ✅ 급수 차단: {should_block}")
    
    print("\n[3-2] 급수탱크 정상 복구")
    distance = 10  # 수위 20cm (정상)
    monitor.check_supply_tank(distance)
    
    print("\n[3-3] 물받이탱크만 넘침 상태 - 급수 차단 확인")
    should_block = monitor.should_block_watering()
    assert should_block == True, f"예상: True (차단), 실제: {should_block}"
    print(f"   ✅ 급수 차단: {should_block}")
    
    print("\n[3-4] 물받이탱크도 정상 복구")
    monitor.check_overflow_tank(False)
    
    print("\n[3-5] 모두 정상 - 급수 허용 확인")
    should_block = monitor.should_block_watering()
    assert should_block == False, f"예상: False (허용), 실제: {should_block}"
    print(f"   ✅ 급수 허용: {not should_block}")
    
    # ========================================
    # 시나리오 4: 알림 쿨다운 테스트
    # ========================================
    print("\n\n" + "=" * 70)
    print("📝 시나리오 4: 알림 쿨다운 (중복 방지)")
    print("=" * 70)
    
    # 알림 쿨다운을 짧게 설정 (테스트용)
    original_cooldown = monitor.alert_cooldown
    monitor.alert_cooldown = 3  # 3초로 설정
    
    # 알림 카운터 초기화
    initial_count = len(mock_mqtt.notifications)
    
    print(f"\n[4-1] 급수탱크 위험 알림 (1차)")
    monitor.check_supply_tank(28)  # 위험 상태
    count_after_1st = len(mock_mqtt.notifications)
    print(f"   📢 알림 개수: {count_after_1st - initial_count}개 (예상: 1개)")
    
    print(f"\n[4-2] 즉시 재확인 - 쿨다운으로 알림 차단됨")
    monitor.check_supply_tank(28)  # 위험 상태 (쿨다운 중)
    count_after_2nd = len(mock_mqtt.notifications)
    print(f"   📢 알림 개수: {count_after_2nd - count_after_1st}개 (예상: 0개)")
    assert count_after_2nd == count_after_1st, "쿨다운 중에는 알림이 전송되지 않아야 함"
    
    print(f"\n[4-3] {monitor.alert_cooldown}초 대기 중...")
    time.sleep(monitor.alert_cooldown + 0.5)
    
    print(f"\n[4-4] 쿨다운 종료 - 알림 재전송됨")
    monitor.check_supply_tank(28)  # 위험 상태 (쿨다운 종료)
    count_after_3rd = len(mock_mqtt.notifications)
    print(f"   📢 알림 개수: {count_after_3rd - count_after_2nd}개 (예상: 1개)")
    assert count_after_3rd > count_after_2nd, "쿨다운 종료 후 알림이 전송되어야 함"
    
    # 쿨다운 복원
    monitor.alert_cooldown = original_cooldown
    
    # ========================================
    # 결과 요약
    # ========================================
    print("\n\n" + "=" * 70)
    print("📊 테스트 결과 요약")
    print("=" * 70)
    
    summary = monitor.get_status_summary()
    print(f"\n현재 상태:")
    print(f"   - 급수탱크: {summary['supply_tank']}")
    print(f"   - 물받이탱크: {summary['overflow_tank']}")
    print(f"   - 전체 상태: {summary['alert_status']}")
    
    print(f"\n전송된 알림:")
    print(f"   - 총 {len(mock_mqtt.notifications)}개")
    for i, notification in enumerate(mock_mqtt.notifications, 1):
        print(f"   {i}. {notification}")
    
    print("\n" + "=" * 70)
    print("✅ 모든 테스트 통과!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_water_tank_monitor()
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
