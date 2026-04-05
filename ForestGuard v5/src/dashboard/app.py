"""
Forest Guard Dashboard - Main Flask application
"""
from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
from src.common.mongodb_client import MongoDBClient
from src.common.rest_helper import get_catalog_config, register_service
from src.dashboard.dashboard_helpers import (
    get_mongo_client, 
    get_all_sensors_data, 
    get_latest_sensor_data,
    get_sensor_list,
    DEFAULT_MAP_CENTER
)

app = Flask(__name__)

class DashboardService:
    def __init__(self):
        self.register_with_catalog()
        self.load_config()
        self.mongo_client = get_mongo_client()
        
    def register_with_catalog(self):
        """Register dashboard service with catalog"""
        service_data = {
            "name": "dashboard",
            "port": 5001,
            "host": "localhost",
            "status": "running",
            "endpoints": ["/", "/sensors", "/api/health", "/api/sensors", "/api/geojson"]
        }
        register_service(service_data)
        
    def load_config(self):
        """Load configuration from catalog service"""
        try:
            self.config = get_catalog_config("config")
            self.thresholds = get_catalog_config("thresholds")
        except Exception as e:
            self.config = {}
            self.thresholds = {}
            print(f"Error loading config: {e}")

# Initialize dashboard service
dashboard = DashboardService()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/sensors')
def sensor_list():
    """Sensor list page (if needed)"""
    sensors = get_sensor_list()
    return jsonify({"sensors": sensors, "message": "Use /api/sensors for JSON data"})

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "dashboard", 
        "timestamp": datetime.now().isoformat(),
        "mongodb_connected": dashboard.mongo_client is not None
    })

@app.route('/api/sensors')
def api_sensors():
    """Unified API endpoint for all sensor data"""
    try:
        sensors = get_all_sensors_data(dashboard.mongo_client)
        return jsonify(sensors)
    except Exception as e:
        print(f"Error in /api/sensors: {e}")
        return jsonify([])

@app.route('/api/geojson')
def api_geojson():
    """API endpoint for GeoJSON sensor data"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, '..', '..')
        geojson_path = os.path.join(project_root, 'data', 'geojson', 'latest.geojson')
        
        if os.path.exists(geojson_path):
            with open(geojson_path, 'r') as f:
                geojson_data = json.load(f)
            return jsonify(geojson_data)
        else:
            # Return empty GeoJSON if file doesn't exist
            return jsonify({"type": "FeatureCollection", "features": []})
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return jsonify({"type": "FeatureCollection", "features": []})

@app.route('/favicon.ico')
def favicon():
    """Simple favicon handler"""
    return '', 204

if __name__ == '__main__':
    print(f"Starting Forest Guard Dashboard on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)

