import paho.mqtt.client as mqtt
from datetime import datetime

class MqttClient:
    #MQTT 통신 class
    
    def __init__(self, user_id, device_serial, broker="localhost"):
        self.user_id = user_id
        self.device_serial = device_serial
        
        # MQTT 클라이언트 생성
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # 현재 프리셋 저장
        self.current_preset = {}
        
        # 브로커 연결
        print(f"MQTT 브로커 연결: {broker}")
        self.client.connect(broker, 1883, 60)
        self.client.loop_start()
        print("연결 완료!")
    

    #sub 메서드들들
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT 연결 성공")
            # 디바이스 단위로 명령 구독
            topic = f"{self.user_id}/smartfarm/{self.device_serial}/cmd"
            self.client.subscribe(topic)
            print(f"구독 완료: {topic}")
        else:
            print(f"연결 실패: {rc}")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        print(f"\n[수신] 토픽: {topic}")
        print(f"[수신] 명령: {payload}")
        
        # 명령 처리 - 디바이스 단위로 명령 수신
        if "/cmd" in topic:
            # 페이로드 파싱 (key=value;key=value 형식)
            params = {}
            for pair in payload.split(';'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key] = value
            
            print(f"[명령 파라미터]: {params}")
            
            # 프리셋 명령인 경우 저장
            if 'Co2Level' in params or 'OptimalTemp' in params:
                self.current_preset = params
                print(f"[프리셋 설정 완료]")
    

    #pub 메서드들들
    def send_sensor_data(self, farm_order, temp, hum, light, soil, co2=None):
        """센서 데이터 전송"""
        farm_uid = f"{self.device_serial}:{farm_order}"
        topic = f"{self.user_id}/smartfarm/{farm_uid}/sensor/data"
        
        # DB 서버 파싱 형식에 맞춰 전송
        data = f"temp={temp};humidity={hum};measuredLight={light};soil={soil}"
        if co2 is not None:
            data += f";co2={co2}"
        
        self.client.publish(topic, data)
        print(f"전송: {data}")
    
    def send_notification_logs(self, message):
        """알림 로그 전송 - 평문으로 전송"""
        topic = f"{self.user_id}/smartfarm/{self.device_serial}/sensor/nl"
        
        # 평문 그대로 전송
        self.client.publish(topic, message, qos=1)
        print(f"알림 전송: {message}")
    
#종료료
    def close(self):
        self.client.loop_stop()
        self.client.disconnect()

