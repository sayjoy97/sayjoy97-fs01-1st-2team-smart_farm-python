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
    

    #sub 메서드들
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT 연결 성공")
            # 프리셋 명령 구독: user1/smartfarm/A1001:1/cmd/, user1/smartfarm/A1001:2/cmd/ 등
            topic = f"{self.user_id}/smartfarm/{self.device_serial}:+/cmd/#"
            self.client.subscribe(topic)
            print(f"구독 완료: {topic}")
        else:
            print(f"연결 실패: {rc}")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
    

    #pub 메서드들
    def send_sensor_data(self, farm_slot, measured_temp, measured_humidity, measured_light, measured_soil_moisture, measured_co2=None):
        """센서 데이터 전송"""
        farm_uid = f"{self.device_serial}:{farm_slot}"
        topic = f"{self.user_id}/smartfarm/{farm_uid}/sensor/data"
        
        data = f"measured_temp={measured_temp};measured_humidity={measured_humidity};measured_light={measured_light};measured_soil_moisture={measured_soil_moisture}"
        if measured_co2 is not None:
            data += f";measured_co2={measured_co2}"
        
        now = datetime.now().isoformat(timespec="seconds")
        data += f";ts={now}"
        
        self.client.publish(topic, data)
        print(f"전송: {data}")
    
    def send_notification_logs(self, message):
        topic = f"{self.user_id}/smartfarm/{self.device_serial}/nl"
        
        # 타임스탬프 추가
        now = datetime.now().isoformat(timespec="seconds")
        data = f"message={message};ts={now}"
        
        self.client.publish(topic, data, qos=1)
        print(f"알림 전송: {message}")
    
#종료
    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
