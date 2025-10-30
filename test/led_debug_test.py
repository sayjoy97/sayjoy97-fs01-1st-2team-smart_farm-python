"""
LED 3개 핀 개별 테스트 (디버깅용)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import RPi.GPIO as GPIO

# LED 핀 번호
LED_PINS = [27, 25, 18]

print("🔧 LED 개별 핀 테스트 시작\n")

try:
    GPIO.setmode(GPIO.BCM)
    
    # 모든 핀 초기화
    for pin in LED_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        print(f"  GPIO {pin} 초기화 완료")
    
    print("\n" + "=" * 50)
    
    # 1. 한 번에 모두 켜기
    print("\n[테스트 1] 3개 LED 동시 켜기")
    for pin in LED_PINS:
        GPIO.output(pin, GPIO.HIGH)
        print(f"  ✅ GPIO {pin} ON")
    print("⏳ 5초 대기 - 3개 모두 켜져있는지 확인하세요!")
    time.sleep(5)
    
    # 모두 끄기
    for pin in LED_PINS:
        GPIO.output(pin, GPIO.LOW)
    print("\n  🛑 모두 OFF\n")
    time.sleep(2)
    
    # 2. 하나씩 순차적으로 켜기
    print("[테스트 2] LED 순차 점등 (2초씩)")
    for pin in LED_PINS:
        print(f"  💡 GPIO {pin} ON")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(pin, GPIO.LOW)
        print(f"  🛑 GPIO {pin} OFF")
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    
    # 3. 최종 동시 점등 확인
    print("\n[테스트 3] 최종 확인 - 3개 동시 점등")
    for pin in LED_PINS:
        GPIO.output(pin, GPIO.HIGH)
    print("  💡 3개 LED 모두 ON")
    print("⏳ 5초 대기...")
    time.sleep(5)
    
    print("\n✅ 테스트 완료!")
    
except KeyboardInterrupt:
    print("\n\n🛑 사용자에 의해 중단됨")
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
finally:
    print("\n🧹 GPIO 정리 중...")
    for pin in LED_PINS:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup(LED_PINS)
    print("✅ 정리 완료\n")
