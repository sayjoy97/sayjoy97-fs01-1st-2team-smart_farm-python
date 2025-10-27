import mh_z19
import time

print("🌫️ MH-Z19 CO₂ 센서 테스트 시작... (Ctrl + C 종료)\n")

try:
    while True:
        result = mh_z19.read()
        if result is not None and 'co2' in result:
            print(f"🌿 CO₂ 농도: {result['co2']} ppm")
        else:
            print("⚠️ 센서 데이터를 읽을 수 없습니다.")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 종료합니다.")
