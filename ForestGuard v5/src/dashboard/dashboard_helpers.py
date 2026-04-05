"""
Centralized dashboard helper functions - single source of truth for dashboard logic
"""
import json
import os
from datetime import datetime, timedelta
from src.common.rest_helper import get_catalog_config, get_sensors
from src.common.mongodb_client import MongoDBClient

# Configuration constants
DEFAULT_COORDINATE = [0, 0]
DEFAULT_MAP_CENTER = [33.4484, -112.0740]  # Phoenix, AZ
DEFAULT_MAP_ZOOM = 6

def get_mongo_client():
    """Get connected MongoDB client"""
    try:
        client = MongoDBClient()
        if client.connect():
            return client
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
    return None

def get_sensor_status(sensor_type, value, thresholds=None):
    """Determine sensor status based on thresholds"""
    if thresholds is None:
        thresholds = get_catalog_config("thresholds")
    
    sensor_thresholds = thresholds.get(sensor_type, {})
    warning_threshold = sensor_thresholds.get('warning')
    critical_threshold = sensor_thresholds.get('critical')
    
    if warning_threshold is None or critical_threshold is None:
        return 'normal'
    
    if sensor_type == 'humidity':
        if value <= critical_threshold:
            return 'critical'
        elif value <= warning_threshold:
            return 'warning'
        else:
            return 'normal'
    elif sensor_type == 'smoke':
        if value >= critical_threshold:
            return 'critical'
        elif value >= warning_threshold:
            return 'warning'
        else:
            return 'normal'
    else:  # temperature
        if value >= critical_threshold:
            return 'critical'
        elif value >= warning_threshold:
            return 'warning'
        else:
            return 'normal'

def get_latest_sensor_data(mongo_client=None, thresholds=None):
    """Get latest sensor data for each sensor type"""
    if mongo_client is None:
        mongo_client = get_mongo_client()
    if not mongo_client:
        return {}
        
    if thresholds is None:
        thresholds = get_catalog_config("thresholds")
    
    try:
        latest_data = {}
        for sensor_type in ['temperature', 'humidity', 'smoke']:
            query = {"sensor_type": sensor_type}
            result = mongo_client.db.sensor_data.find_one(query, sort=[("timestamp", -1)])
            
            if result:
                latest_data[sensor_type] = {
                    'value': result.get('value', 0),
                    'timestamp': result.get('timestamp', ''),
                    'location': result.get('zone', 'Unknown'),  # Standardize on 'zone'
                    'sensor_id': result.get('sensor_id', 'Unknown'),
                    'status': get_sensor_status(sensor_type, result.get('value', 0), thresholds)
                }
            else:
                latest_data[sensor_type] = {
                    'value': 0, 
                    'timestamp': '', 
                    'location': 'Unknown', 
                    'sensor_id': 'Unknown', 
                    'status': 'offline'
                }
        return latest_data
    except Exception as e:
        print(f"Error getting latest sensor data: {e}")
        return {}

def get_all_sensors_data(mongo_client=None, limit=50):
    """Get deduplicated sensor data for all sensors"""
    if mongo_client is None:
        mongo_client = get_mongo_client()
    if not mongo_client:
        return []
    
    try:
        # Get latest readings
        latest_readings = mongo_client.get_latest_data(limit)
        
        # Deduplicate by sensor_type + zone, keeping latest timestamp
        sensor_map = {}
        for reading in latest_readings:
            sensor_type = reading.get('sensor_type', 'unknown')
            zone = reading.get('zone', 'unknown')
            key = f"{sensor_type}_{zone}"
            
            if key not in sensor_map or reading.get('timestamp', '') > sensor_map[key].get('timestamp', ''):
                sensor_map[key] = reading
        
        # Convert to list format with status
        sensors = []
        thresholds = get_catalog_config("thresholds")
        
        for reading in sensor_map.values():
            sensors.append({
                'sensor_id': reading.get('sensor_id', 'unknown'),
                'sensor_type': reading.get('sensor_type', 'unknown'),
                'zone': reading.get('zone', 'unknown'),
                'value': reading.get('value', 0),
                'status': get_sensor_status(reading.get('sensor_type', ''), reading.get('value', 0), thresholds),
                'timestamp': reading.get('timestamp', datetime.now().isoformat()),
                'coordinates': get_sensor_coordinates(reading)
            })
        
        return sensors
    except Exception as e:
        print(f"Error getting all sensors data: {e}")
        return []

def get_sensor_coordinates(reading):
    """Extract coordinates from sensor reading"""
    try:
        location = reading.get('location', {})
        if isinstance(location, dict):
            coords = location.get('coordinates')
            if coords and len(coords) >= 2:
                return coords
        return DEFAULT_COORDINATE
    except:
        return DEFAULT_COORDINATE

def get_sensor_list():
    """Get sensor list from catalog service"""
    try:
        sensors = get_sensors()
        if isinstance(sensors, dict) and 'sensors' in sensors:
            return sensors['sensors']
        return sensors if isinstance(sensors, list) else []
    except Exception as e:
        print(f"Error getting sensor list: {e}")
        return []
