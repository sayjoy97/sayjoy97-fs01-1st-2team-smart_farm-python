"""
히터, LED, 환기팬 통합 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from Actuator.heater import Heater
from Actuator.led import LED
from Actuator.ventilation_fan import VentilationFan

def test_all():
    print("=" * 60)
    print("🧪 히터 + LED + 환기팬 통합 테스트")
    print("=" * 60)
    
    # 핀 설정 (main.py와 동일)
    heater_pins = [16, 17]
    led_pins = [27, 25, 18]
    fan_pins = [20, 12]
    
    print(f"\n📌 핀 설정:")
    print(f"  🔥 히터: {heater_pins}")
    print(f"  💡 LED: {led_pins}")
    print(f"  🌀 환기팬: {fan_pins}")
    
    # 객체 생성
    print(f"\n🔧 초기화 중...")
    try:
        heater = Heater(heater_pins)
        led = LED(led_pins)
        fan = VentilationFan(fan_pins)
        print("✅ 초기화 완료!")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        return
    
    try:
        # 테스트 1: 각각 켜기
        print("\n" + "=" * 60)
        print("테스트 1: 각각 켜기 (2초씩)")
        print("=" * 60)
        
        print("\n🔥 히터 ON")
        heater.turn_on()
        time.sleep(2)
        
        print("💡 LED ON")
        led.turn_on()
        time.sleep(2)
        
        print("🌀 환기팬 ON")
        fan.turn_on()
        time.sleep(2)
        
        # 테스트 2: 모두 켜진 상태로 5초
        print("\n" + "=" * 60)
        print("테스트 2: 모두 ON 상태로 5초 유지")
        print("=" * 60)
        print("⚡ 모든 액추에이터 작동 중...")
        time.sleep(5)
        
        # 테스트 3: 각각 끄기
        print("\n" + "=" * 60)
        print("테스트 3: 각각 끄기 (2초씩)")
        print("=" * 60)
        
        print("\n🛑 히터 OFF")
        heater.turn_off()
        time.sleep(2)
        
        print("🛑 LED OFF")
        led.turn_off()
        time.sleep(2)
        
        print("🛑 환기팬 OFF")
        fan.turn_off()
        time.sleep(2)
        
        # 테스트 4: 3회 반복 (모두 동시에)
        print("\n" + "=" * 60)
        print("테스트 4: 모두 동시에 3회 토글")
        print("=" * 60)
        
        for i in range(3):
            print(f"\n🔄 {i+1}/3 - 모두 ON")
            heater.turn_on()
            led.turn_on()
            fan.turn_on()
            time.sleep(2)
            
            print(f"🔄 {i+1}/3 - 모두 OFF")
            heater.turn_off()
            led.turn_off()
            fan.turn_off()
            time.sleep(2)
        
        print("\n✅ 모든 테스트 완료!")
        
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 테스트 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 정리
        print("\n🧹 GPIO 정리 중...")
        try:
            heater.turn_off()
            led.turn_off()
            fan.turn_off()
            time.sleep(0.5)
            
            heater.cleanup()
            led.cleanup()
            fan.cleanup()
            print("✅ 정리 완료!")
        except Exception as e:
            print(f"⚠️  정리 중 오류: {e}")
        
        print("\n" + "=" * 60)
        print("🏁 테스트 종료")
        print("=" * 60)


if __name__ == "__main__":
    test_all()
