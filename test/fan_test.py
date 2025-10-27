"""
환기팬 제어 테스트 (ULN2003 릴레이 모듈)

사용법:
    python test/fan_test.py
    
동작:
    - 3초마다 환기팬 ON/OFF 반복
    - Ctrl+C로 종료
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Actuator.ventilation_fan import VentilationFan
import time

# 환기팬 GPIO 핀 번호 (ULN2003의 IN 핀 연결)
FAN_PIN = 20

print("=" * 60)
print("🌀 환기팬 제어 테스트 시작 (ULN2003 릴레이 모듈)")
print("=" * 60)
print(f"📍 GPIO 핀: {FAN_PIN}")
print("💡 Ctrl+C로 종료")
print("=" * 60)

try:
    # 환기팬 초기화
    fan = VentilationFan(FAN_PIN)
    
    while True:
        # 팬 ON
        fan.turn_on()
        print("💨 팬 켜짐!")
        time.sleep(3)

        # 팬 OFF
        fan.turn_off()
        print("🛑 팬 꺼짐!")
        time.sleep(3)

except KeyboardInterrupt:
    print("\n\n🛑 프로그램 종료")
finally:
    fan.cleanup()
    print("✅ 정리 완료")
