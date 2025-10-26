# 스마트팜 시스템 (멀티슬롯 지원)

## 🏗️ 시스템 구성

### 전체 아키텍처
```
[유저 콘솔(Java)] ←→ [DB] ←→ [DB 서버(Java MQTT)] ←→ [MQTT 브로커] ←→ [라즈베리파이]
```

### 역할 분담
- **라즈베리파이**: 센서 데이터 수집, 액추에이터 자율 제어
- **DB 서버**: MQTT 게이트웨이, 센서 데이터 저장, 프리셋 관리
- **유저 콘솔**: DB 조회/수정 (MQTT 직접 사용 안 함)

---

## 📋 전체 사용 방법

### 1단계: 환경 준비

**MQTT 브로커 설치 및 실행**
```bash
# Mosquitto 설치 (Ubuntu/Debian)
sudo apt install mosquitto mosquitto-clients

# 실행 확인
sudo systemctl status mosquitto
```

**라즈베리파이 패키지 설치**
```bash
sudo apt update
sudo apt install -y python3-pip
pip3 install paho-mqtt RPi.GPIO adafruit-blinka pyserial spidev
```

### 2단계: DB 준비 (Java 콘솔)

**디바이스 사전 등록**
```sql
INSERT INTO devices (device_serial, device_name, status) 
VALUES ('A1001', '스마트팜 디바이스 1', 'active');
```

**유저 회원가입 및 디바이스 등록**
- Java 콘솔에서 회원가입
- 라즈베리파이 시리얼 넘버 입력하여 등록
- DB의 `devices` 테이블에 `user_id` 업데이트

**식물 설정 (프리셋 저장)**
- Java 콘솔에서 식물 추가
- 슬롯별 목표 환경 설정 (온도, 습도, 조도 등)
- DB의 `farms` 테이블에 `farmUid` (예: A1001:1, A1001:2) 단위로 저장

### 3단계: DB 서버 실행 (Java)

```java
// DBServerApp.java 또는 MainApp.java에서
MqttManager dbServer = new MqttManager(true); // DB 서버 모드
```

**DB 서버가 하는 일:**
1. `smartfarm/+/sensor/#` 구독 → 센서/알림 수신하여 DB 저장
2. `smartfarm/+/preset/request` 구독 → 프리셋 요청 수신
3. DB 조회 후 `smartfarm/{farmUid}/preset/response` 응답
4. 유저가 프리셋 변경 시 `smartfarm/{farmUid}/preset` 발행

### 4단계: 라즈베리파이 설정 및 실행

**`smartfarm/main.py` 설정**
```python
# 디바이스 정보
device_serial = "A1001"
broker = "192.168.0.10"  # DB 서버 IP 또는 localhost
interval = 10

# 슬롯 설정 (1슬롯: [1], 4슬롯: [1,2,3,4])
slots = [1, 2, 3, 4]

# 슬롯별 액추에이터 핀
actuator_pin_map = {
    1: {'heater': 17, 'water': 27, 'fan': 22},
    2: {'heater': 5,  'water': 6,  'fan': 13},
    3: {'heater': 19, 'water': 26, 'fan': 21},
    4: {'heater': 20, 'water': 16, 'fan': 12},
}

# 슬롯별 센서 핀/채널
sensor_pin_map = {
    1: {'dht11_pin': board.D4,  'photo_channel': 0, 'water_channel': 0, 'co2_port': '/dev/serial0'},
    2: {'dht11_pin': board.D17, 'photo_channel': 1, 'water_channel': 1, 'co2_port': '/dev/serial1'},
    3: {'dht11_pin': board.D18, 'photo_channel': 2, 'water_channel': 2, 'co2_port': '/dev/serial2'},
    4: {'dht11_pin': board.D27, 'photo_channel': 3, 'water_channel': 3, 'co2_port': '/dev/serial3'},
}

# 초음파 센서 (통합 - 모든 슬롯 공유)
ultrasonic_trig = 23
ultrasonic_echo = 24
```

**실행**
```bash
cd ~/sayjoy97-fs01-1st-2team-smart_farm-python
python3 smartfarm/main.py
```

**실행 시 자동 동작:**
1. 각 슬롯별 MQTT 클라이언트 생성
2. 각 슬롯별 프리셋 요청 (`smartfarm/A1001:1/preset/request`)
3. DB 서버로부터 프리셋 수신 (없으면 기본값)
4. 초음파 센서 1회 읽기 (통합)
5. 각 슬롯별 센서 읽기 (DHT11, 조도, 토양, CO2)
6. 각 슬롯별 센서 데이터 전송
7. 각 슬롯별 프리셋 기반 자율 제어

### 5단계: 동작 흐름

```
[라즈베리파이 부팅]
        ↓
슬롯 1: smartfarm/A1001:1/preset/request → DB 서버
슬롯 2: smartfarm/A1001:2/preset/request → DB 서버
슬롯 3: smartfarm/A1001:3/preset/request → DB 서버
슬롯 4: smartfarm/A1001:4/preset/request → DB 서버
        ↓
← DB 서버: smartfarm/A1001:1/preset/response (OptimalTemp=22;...)
← DB 서버: smartfarm/A1001:2/preset/response (OptimalTemp=24;...)
        ↓
[10초마다 반복]
  슬롯 1 센서 읽기 → smartfarm/A1001:1/sensor/data 전송 → 자율 제어
  슬롯 2 센서 읽기 → smartfarm/A1001:2/sensor/data 전송 → 자율 제어
  슬롯 3 센서 읽기 → smartfarm/A1001:3/sensor/data 전송 → 자율 제어
  슬롯 4 센서 읽기 → smartfarm/A1001:4/sensor/data 전송 → 자율 제어
        ↓
[유저가 콘솔에서 슬롯 2 프리셋 변경]
        ↓
DB 저장 → DB 서버: smartfarm/A1001:2/preset 발행
        ↓
← 라즈베리파이: 슬롯 2 프리셋 즉시 업데이트
```

---

## 📡 MQTT 토픽 구조

### farmUid 형식
```
farmUid = {deviceSerial}:{slotNumber}
예: A1001:1, A1001:2, B2002:1
```

### 라즈베리파이 → DB 서버
```
smartfarm/{farmUid}/sensor/data        # 센서 데이터 (예: A1001:1/sensor/data)
smartfarm/{deviceSerial}/sensor/nl     # 알림 로그 (디바이스 전체)
smartfarm/{farmUid}/preset/request     # 프리셋 요청
```

### DB 서버 → 라즈베리파이
```
smartfarm/{farmUid}/preset             # 프리셋 업데이트
smartfarm/{farmUid}/preset/response    # 프리셋 응답
```

## 🎛️ 자동 제어 로직

### 히터 (온도 기반)
- 온도 < 목표 - 2°C → 히터 ON
- 온도 > 목표 + 1°C → 히터 OFF

### 물펌프 (토양 수분 기반)
- 토양 ADC > 목표 + 500 → 물펌프 ON
- 토양 ADC < 목표 - 200 → 물펌프 OFF

### 환기팬 (습도 기반)
- 습도 > 목표 + 10% → 환기팬 ON
- 습도 < 목표 - 5% → 환기팬 OFF

## 📊 센서 구성

| 센서 | 타입 | 슬롯별 독립 | 핀/채널 |
|------|------|-------------|---------|
| DHT11 (온습도) | 디지털 | ✅ | GPIO 핀 |
| 조도센서 | 아날로그 | ✅ | ADC 채널 (MCP3008) |
| 토양수분 | 아날로그 | ✅ | ADC 채널 (MCP3208) |
| CO2센서 | 시리얼 | ✅ | UART 포트 |
| 초음파 | 디지털 | ❌ (통합) | TRIG/ECHO 1세트 |

## 📦 필요한 패키지

```bash
pip3 install paho-mqtt RPi.GPIO adafruit-blinka pyserial spidev
```

## ⚠️ 주의사항

### 실행 순서 (중요!)
1. MQTT 브로커 실행
2. **DB 서버(Java) 실행** ← 필수!
3. 라즈베리파이 실행

### 트러블슈팅
- **프리셋 응답 없음**: DB 서버가 실행 중인지 확인
- **센서값이 None**: 센서 연결 및 핀 번호 확인
- **MQTT 연결 실패**: `broker` IP 주소 및 방화벽 확인
- **GPIO 권한 오류**: `sudo` 또는 `gpio` 그룹에 추가

### DB 서버 구현 체크리스트
- [ ] `smartfarm/+/sensor/#` 구독
- [ ] `smartfarm/+/preset/request` 구독
- [ ] `messageArrived`에서 `/preset/request` 처리
- [ ] DB에서 farmUid로 프리셋 조회
- [ ] `publishPresetResponse(farmUid, preset)` 호출
- [ ] 유저가 프리셋 변경 시 `publishPresetUpdate(farmUid, preset)` 호출

## 🔍 디버깅

### MQTT 토픽 모니터링
```bash
# 모든 센서 데이터 확인
mosquitto_sub -t "smartfarm/+/sensor/#" -v

# 모든 프리셋 관련 메시지 확인
mosquitto_sub -t "smartfarm/+/preset/#" -v

# 특정 슬롯만 확인
mosquitto_sub -t "smartfarm/A1001:1/#" -v
```

### 프리셋 수동 발행 테스트
```bash
# 프리셋 응답 테스트
mosquitto_pub -t "smartfarm/A1001:1/preset/response" \
  -m "OptimalTemp=22;OptimalHumidity=65;LightIntensity=3000;SoilMoisture=1800;Co2Level=800"

# 프리셋 업데이트 테스트
mosquitto_pub -t "smartfarm/A1001:1/preset" \
  -m "OptimalTemp=25;OptimalHumidity=70"
```

## 📚 참고 문서

- **MQTT 통신 규약**: `src/mqtt 통신 규약.md` 참조
- **DB 스키마**: `src/sql/` 참조
- **센서 핀아웃**: 라즈베리파이 GPIO 맵 확인
