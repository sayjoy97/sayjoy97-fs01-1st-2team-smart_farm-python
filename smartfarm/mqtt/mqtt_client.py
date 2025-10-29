import paho.mqtt.client as mqtt
from datetime import datetime

class MqttClient:
    #MQTT 통신 class
    
    def __init__(self, farm_uid, broker="localhost"):
        self.farm_uid = farm_uid  # 예: "A1001:1"
        self.device_serial = farm_uid.split(':')[0]
        self.slot = int(farm_uid.split(':')[1])
        
        # MQTT 클라이언트 생성
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # 현재 프리셋 저장 (기본값)
        self.current_preset = {
            'OptimalTemp': '25',
            'OptimalHumidity': '60',
            'LightIntensity': '3000',
            'SoilMoisture': '2000',
            'Co2Level': '800'
        }
        self.preset_received = False  # 프리셋 수신 여부
        
        # 브로커 연결
        print(f"MQTT 브로커 연결: {broker}")
        self.client.connect(broker, 1883, 60)
        self.client.loop_start()
        print("연결 완료!")
    

    #sub 메서드
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT 연결 성공")
            
            # 프리셋 구독 (자기 슬롯만)
            preset_topic = f"smartfarm/{self.farm_uid}/preset"
            self.client.subscribe(preset_topic)
            print(f"구독 완료 (프리셋): {preset_topic}")
            
            # 프리셋 응답 구독 (자기 슬롯만)
            preset_response_topic = f"smartfarm/{self.farm_uid}/preset/response"
            self.client.subscribe(preset_response_topic)
            print(f"구독 완료 (프리셋 응답): {preset_response_topic}")
        else:
            print(f"연결 실패: {rc}")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')

        print(f"\n[수신] 토픽: {topic}")
        print(f"[수신] 페이로드: {payload}")

        # 프리셋 업데이트 수신 (유저가 설정 변경)
        if topic == f"smartfarm/{self.farm_uid}/preset":
            params = {}
            for pair in payload.split(';'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key.strip()] = value.strip()

            if params:
                self.current_preset = { **self.current_preset, **params }
                print(f"✅ [프리셋 업데이트]")
                print(f"   {self.current_preset}")
        
        # 프리셋 응답 수신 (시작 시 DB 조회 결과)
        elif topic == f"smartfarm/{self.farm_uid}/preset/response":
            if payload == "none":
                print(f"ℹ️  [프리셋 없음] 기본값 사용")
                self.preset_received = True
            else:
                params = {}
                for pair in payload.split(';'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params[key.strip()] = value.strip()

                if params:
                    self.current_preset = { **self.current_preset, **params }
                    self.preset_received = True
                    print(f"✅ [DB 프리셋 수신]")
                    print(f"   {self.current_preset}")
    
    def get_preset(self):
        """현재 프리셋 반환"""
        return self.current_preset
    
    def request_preset(self):
        """DB 서버에 프리셋 요청"""
        topic = f"smartfarm/{self.farm_uid}/preset/request"
        self.client.publish(topic, self.farm_uid, qos=1)
        print(f"📡 [프리셋 요청] {self.farm_uid}")
    
    def is_preset_ready(self):
        """프리셋 수신 여부 확인"""
        return self.preset_received
    

    #pub 메서드
    def send_sensor_data(self, temp=None, hum=None, light=None, soil=None, co2=None):
        """센서 데이터 전송 - DB 서버가 구독 중 (누락된 값은 제외)"""
        # 읽은 센서값만 포함 (None이 아닌 값만)
        data_parts = []
        if temp is not None:
            data_parts.append(f"temp={temp}")
        if hum is not None:
            data_parts.append(f"humidity={hum}")
        if light is not None:
            data_parts.append(f"measuredLight={light}")
        if soil is not None:

            # Boolean을 1/0으로 변환
            soil_value = 1 if soil else 0
            data_parts.append(f"soil={soil_value}")

            data_parts.append(f"soil={soil}")
        if co2 is not None:
            data_parts.append(f"co2={co2}")
        
        # 전송할 데이터가 없으면 종료
        if not data_parts:
            print("⚠️  전송할 센서 데이터 없음")
            return
        
        data = ";".join(data_parts)
        
        # 토픽 생성 및 전송 (DB 서버가 smartfarm/+/sensor/# 구독 중)
        topic = f"smartfarm/{self.farm_uid}/sensor/data"
        self.client.publish(topic, data, qos=0)
        
        print(f"📤 센서 데이터: {data}")
    
    def send_notification_logs(self, message):
        """알림 로그 전송 - DB 서버가 구독 중"""
        topic = f"smartfarm/{self.device_serial}/sensor/nl"
        self.client.publish(topic, message, qos=1)
        
        print(f"📢 알림 전송: {message}")
    
#종료
    def close(self):
        self.client.loop_stop()
        self.client.disconnect()

