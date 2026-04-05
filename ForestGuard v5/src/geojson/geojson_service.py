"""
GeoJSON service for Forest Guard.
"""

from flask import Flask, jsonify
import json, os, threading, time
from datetime import datetime
from src.common.mongodb_client import MongoDBClient
from src.common.rest_helper import register_service

app = Flask(__name__)

class GeoJSONService:
    def __init__(self):
        register_service({"name": "geojson_service", "port": 5007, "host": "localhost", "status": "running", "endpoints": ["/api/health"]})
        self.mongo_client = MongoDBClient()
        self.start_background_generation()

    def create_geojson_features(self):
        try:
            self.mongo_client.connect()
            features = []
            latest_readings = self.mongo_client.get_latest_data(100)
            
            sensor_map = {}
            for reading in latest_readings:
                sensor_id = reading.get('sensor_id')
                if sensor_id and (sensor_id not in sensor_map or reading.get('timestamp', '') > sensor_map[sensor_id].get('timestamp', '')):
                    sensor_map[sensor_id] = reading
            
            for sensor_id, result in sensor_map.items():
                location = result.get('location', {})
                if not location or not isinstance(location, dict):
                    continue
                
                coords = location.get('coordinates')
                if not coords and 'longitude' in location and 'latitude' in location:
                    coords = [location['longitude'], location['latitude']]
                
                if coords and len(coords) >= 2:
                    status = self._get_status(result.get('sensor_type'), result.get('value', 0))
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": coords},
                        "properties": {
                            "sensor_id": sensor_id,
                            "sensor_type": result.get('sensor_type', 'unknown'),
                            "value": result.get('value', 0),
                            "unit": result.get('unit', ''),
                            "zone": result.get('zone', 'unknown'),
                            "timestamp": result.get('timestamp', ''),
                            "status": status,
                            "color": "#ff4444" if status == "critical" else "#44ff44"
                        }
                    })
            
            return {"type": "FeatureCollection", "features": features}
        except Exception as e:
            print(f"[GEOJSON] Error creating features: {e}")
            return {"type": "FeatureCollection", "features": []}

    def _get_status(self, sensor_type, value):
        thresholds = {"temperature": 35, "humidity": 30, "smoke": 1}
        threshold = thresholds.get(sensor_type, 999)
        
        if sensor_type == 'humidity':
            return 'critical' if value < threshold else 'normal'
        elif sensor_type == 'smoke':
            return 'critical' if value >= threshold else 'normal'
        else:
            return 'critical' if value > threshold else 'normal'

    def save_geojson(self):
        geojson_data = self.create_geojson_features()
        try:
            output_path = os.path.join(os.path.dirname(__file__), '../../data/geojson/latest.geojson')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(geojson_data, f, indent=2)
            print(f"[GEOJSON] Updated: {len(geojson_data.get('features', []))} features")
        except Exception as e:
            print(f"[GEOJSON] Save error: {e}")

    def start_background_generation(self):
        def generate_loop():
            while True:
                self.save_geojson()
                time.sleep(30)
        
        thread = threading.Thread(target=generate_loop, daemon=True)
        thread.start()

geojson_service = GeoJSONService()

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "geojson_service", "timestamp": datetime.now().isoformat()})

@app.route('/api/geojson')
def get_geojson():
    return jsonify(geojson_service.create_geojson_features())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=False)
