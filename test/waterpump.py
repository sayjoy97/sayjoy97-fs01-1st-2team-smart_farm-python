"""
워터펌프 제어 테스트 (L9110S 모터 드라이버 B채널)

사용법:
    python test/waterpump.py
    
동작:
    - 3초마다 워터펌프 ON/OFF 반복
    - Ctrl+C로 종료
    
연결:
    - IB1 → GPIO 5
    - IB2 → GPIO 6
    - VCC → 5V
    - GND → GND
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Actuator.water_pump import WaterPump
import time

# L9110S B채널 제어핀
IB1 = 5
IB2 = 6

print("=" * 60)
print("💧 워터펌프 제어 테스트 시작 (L9110S B채널)")
print("=" * 60)
print(f"📍 GPIO 핀: IB1={IB1}, IB2={IB2}")
print("💡 Ctrl+C로 종료")
print("=" * 60)

try:
    # 워터펌프 초기화
    pump = WaterPump(IB1, IB2)
    
    while True:
        # 펌프 ON (정방향)
        pump.turn_on()
        print("💦 워터펌프 작동 중...")
        time.sleep(3)

        # 펌프 OFF
        pump.turn_off()
        print("🛑 펌프 정지!")
        time.sleep(3)

except KeyboardInterrupt:
    print("\n\n🛑 프로그램 종료")
finally:
    pump.cleanup()
    print("✅ 정리 완료")
