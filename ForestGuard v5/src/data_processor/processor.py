"""Processes and stores sensor data for Forest Guard."""

import json, time
from src.common.mqtt_helper import get_mqtt_client
from src.common.mongodb_client import MongoDBClient
from src.common.rest_helper import register_service

class DataProcessor:
    """Handles processing and storage of sensor data."""
    def __init__(self):
        register_service({
            "name": "data_processor", 
            "port": 5005, 
            "host": "localhost", 
            "status": "running", 
            "endpoints": ["/api/health"]
        })
        self.mongo_client = MongoDBClient()
        self.mqtt_client = get_mqtt_client()
        
    def process_sensor_data(self, client, userdata, msg):
        """Process incoming sensor data from MQTT."""
        try:
            data = json.loads(msg.payload.decode())
            print(f"[DATA_PROCESSOR] Processing {data.get('sensor_id', 'unknown')} (zone: {data.get('zone', 'unknown')}, type: {data.get('sensor_type', 'unknown')}, value: {data.get('value', 'N/A')})")
            
            # Save to MongoDB
            if self.mongo_client.insert_sensor_data(data):
                print(f"[DATA_PROCESSOR] Saved to MongoDB: {data['sensor_id']}")
            
            # Convert value to float for consistency
            if 'value' in data:
                try:
                    data['value'] = float(data['value'])
                except:
                    pass
                
        except Exception as e:
            print(f"[DATA_PROCESSOR] Processing failed: {e}")
    
    def start_processing(self):
        """Start the data processing service."""
        if not (self.mongo_client.connect() and self.mqtt_client):
            print("[DATA_PROCESSOR] Failed to connect to services")
            return False
        
        print("[DATA_PROCESSOR] Starting data processing service...")
        self.mqtt_client.on_message = self.process_sensor_data
        self.mqtt_client.loop_start()
        self.mqtt_client.subscribe("sensors/#")
        print("[DATA_PROCESSOR] Subscribed to sensor data")
        return True

def main():
    processor = DataProcessor()
    try:
        if processor.start_processing():
            while True:
                time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping data processor...")

if __name__ == "__main__":
    main()