"""
Common MQTT helper utilities.
"""

import paho.mqtt.client as mqtt
import requests
import random
import string

def get_catalog_config(config_type):
    try:
        resp = requests.get(f"http://localhost:5002/api/config/{config_type}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {}
    except Exception as e:
        return {}

def get_mqtt_client(mqtt_config=None, client_id=None):
    if mqtt_config is None:
        mqtt_config = get_catalog_config("mqtt")
    broker = mqtt_config.get("broker", "localhost")
    port = mqtt_config.get("port", 1883)
    if client_id is None:
        client_id = mqtt_config.get("client_id_prefix", "forest_fire_") + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    client = mqtt.Client(client_id=client_id)
    try:
        client.connect(broker, port, 60)
        return client
    except Exception as e:
        return None
