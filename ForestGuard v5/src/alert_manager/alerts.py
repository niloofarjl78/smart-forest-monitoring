"""
Handles alert logic for Forest Guard system.
"""

import json, requests, time
from datetime import datetime
from src.common.mqtt_helper import get_mqtt_client
from src.common.rest_helper import get_catalog_config, register_service

class AlertManager:
    """Manages alert generation and notifications."""
    def __init__(self):
        """Initialize the alert manager service."""
        register_service({"name": "alert_manager", "port": 5004, "host": "localhost", "status": "running", "endpoints": ["/api/health"]})
        self.thresholds = get_catalog_config("thresholds")
        self.telegram_config = get_catalog_config("telegram")
        self.mqtt_client = get_mqtt_client()
        
    def check_alert_conditions(self, client, userdata, msg):
        """Check if alert conditions are met for incoming sensor data."""
        try:
            data = json.loads(msg.payload.decode())
            sensor_type = data.get("sensor_type")
            value = data.get("value")
            
            if sensor_type in self.thresholds:
                thresholds = self.thresholds[sensor_type]
                if value > thresholds["critical"]:
                    self._send_alert("CRITICAL ALERT", data)
                elif value > thresholds["warning"]:
                    self._send_alert("WARNING", data)
        except:
            pass
    
    def _send_alert(self, level, data):
        """Send alert to all configured notification channels."""
        message = f"{level}\nSensor: {data.get('sensor_id')}\nType: {data.get('sensor_type', '').title()}\nValue: {data.get('value')}\nZone: {data.get('zone')}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self._send_telegram(message)
        print(f"{level}: {data.get('sensor_type')} = {data.get('value')} in {data.get('zone')}")
    
    def _send_telegram(self, message):
        """Send alert via Telegram."""
        try:
            bot_token = self.telegram_config.get("bot_token")
            chat_ids = self.telegram_config.get("authorized_chat_ids", [])
            
            if bot_token and chat_ids:
                for chat_id in chat_ids:
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", 
                                json={"chat_id": chat_id, "text": message})
        except:
            pass
    
    def start_monitoring(self):
        if not self.mqtt_client:
            print("[ALERT_MANAGER] Failed to connect to MQTT broker")
            return False
        
        print("[ALERT_MANAGER] Starting alert monitoring...")
        self.mqtt_client.subscribe("sensors/#")
        self.mqtt_client.on_message = self.check_alert_conditions
        self.mqtt_client.loop_start()
        return True

def main():
    alert_manager = AlertManager()
    try:
        if alert_manager.start_monitoring():
            while True:
                time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping alert manager...")

if __name__ == "__main__":
    main()
