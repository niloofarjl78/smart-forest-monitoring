"""
Common REST helper utilities.
"""

import requests

CATALOG_URL = "http://localhost:5002"

def get_catalog_config(config_type):
    try:
        response = requests.get(f"{CATALOG_URL}/api/config/{config_type}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}

def register_service(service_data):
    try:
        response = requests.post(f"{CATALOG_URL}/api/services", json=service_data, timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def register_sensor(sensor_data):
    try:
        response = requests.post(f"{CATALOG_URL}/api/sensors", json=sensor_data, timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def get_services():
    try:
        response = requests.get(f"{CATALOG_URL}/api/services", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def get_sensors():
    try:
        response = requests.get(f"{CATALOG_URL}/api/sensors", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []
