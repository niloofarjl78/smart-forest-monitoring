"""
Common utility functions for Forest Guard.
"""

import json
import random
from datetime import datetime

def load_config(config_path="config/config.json"):
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Config load failed: {e}")
        return {}

def generate_sensor_id(sensor_type, zone):
    return f"{sensor_type.upper()}-{zone}"

def get_current_timestamp():
    return datetime.now().isoformat()

def simulate_sensor_value(base_value, variance=0.1):
    variation = base_value * variance * (random.random() - 0.5) * 2
    return round(base_value + variation, 2)

def is_critical_value(value, thresholds, sensor_type):
    try:
        return value > thresholds[sensor_type]["critical"]
    except KeyError:
        return False
