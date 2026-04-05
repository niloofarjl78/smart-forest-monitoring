"""Central catalog service for service discovery and configuration."""

from flask import Flask, jsonify, request
import json, os, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.common.mongodb_client import MongoDBClient

app = Flask(__name__)

class CatalogService:
    """Manages service registration and configuration."""
    def __init__(self):
        self.services = {}
        self.sensors = {}
        self.config, self.locations, self.service_config = self._load_configs()
        self.mongo_client = MongoDBClient()

    def _load_configs(self):
        """Load configuration files from disk."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, '..', '..')
        
        try:
            with open(os.path.join(project_root, 'config', 'config.json'), 'r') as f:
                config = json.load(f)
            with open(os.path.join(project_root, 'config', 'locations.json'), 'r') as f:
                locations = json.load(f)
            with open(os.path.join(project_root, 'config', 'services.json'), 'r') as f:
                service_config = json.load(f)
            
            telegram_path = os.path.join(project_root, 'config', 'telegram_config.json')
            if os.path.exists(telegram_path):
                with open(telegram_path, 'r') as tf:
                    config['telegram'] = json.load(tf)
                    
            return config, locations, service_config
        except:
            return {"system": {"name": "Forest Guard"}}, {"locations": []}, {"services": []}

    def register_service(self, service_data):
        """Register a new service with the catalog."""
        service_id = service_data.get('name', 'unknown')
        self.services[service_id] = {**service_data, 'registered_at': datetime.now().isoformat(), 'last_heartbeat': datetime.now().isoformat()}

    def register_sensor(self, sensor_data):
        """Register a new sensor with the catalog."""
        sensor_id = sensor_data.get('id', 'unknown')
        self.sensors[sensor_id] = {**sensor_data, 'registered_at': datetime.now().isoformat()}

catalog = CatalogService()

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "catalog", "timestamp": datetime.now().isoformat()})

@app.route('/api/services', methods=['GET', 'POST'])
def handle_services():
    if request.method == 'POST':
        catalog.register_service(request.get_json())
        return jsonify({"status": "registered"})
    return jsonify(catalog.services)

@app.route('/api/sensors', methods=['GET', 'POST'])
def handle_sensors():
    if request.method == 'POST':
        catalog.register_sensor(request.get_json())
        return jsonify({"status": "registered"})
    return jsonify(catalog.sensors)

@app.route('/api/config/<config_type>')
def get_config(config_type):
    config_map = {
        'mongodb': catalog.config.get('mongodb', {}),
        'influxdb': catalog.config.get('influxdb', {}),
        'mqtt': catalog.config.get('mqtt', {}),
        'telegram': catalog.config.get('telegram', {}),
        'locations': catalog.locations,
        'services': catalog.service_config,
        'config': catalog.config
    }
    
    if config_type == 'thresholds':
        thresholds_path = os.path.join(os.path.dirname(__file__), '../../config/thresholds.json')
        if os.path.exists(thresholds_path):
            with open(thresholds_path, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'error': 'Thresholds file not found'}), 404
    
    return jsonify(config_map.get(config_type, {}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
