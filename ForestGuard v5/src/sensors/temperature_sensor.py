"""Temperature sensor implementation for Forest Guard."""
import time, json, random, requests, sys, subprocess
from datetime import datetime
from src.common.mqtt_helper import get_mqtt_client, get_catalog_config
from src.common.rest_helper import register_sensor

def get_zones():
    try:
        resp = requests.get("http://localhost:5002/api/config/locations", timeout=3)
        return [loc['zone'] for loc in resp.json().get('locations', [])] if resp.status_code == 200 else []
    except:
        return ["phoenix-north", "flagstaff-north", "tucson-north", "sedona-south", "mesa-east", "turin-north"]

def get_coords(zone):
    try:
        resp = requests.get("http://localhost:5002/api/config/locations", timeout=3)
        if resp.status_code == 200:
            for loc in resp.json().get("locations", []):
                if loc["zone"] == zone:
                    coords = loc["coordinates"]
                    return [coords[0] + random.uniform(-0.0005, 0.0005), coords[1] + random.uniform(-0.0005, 0.0005)]
    except:
        pass
    return None

class TemperatureSensor:
    """Simulates and publishes temperature data for a zone."""
    def __init__(self, zone):
        self.zone = zone
        self.device_id = f"temp_sensor_{zone}"
        
    def start_monitoring(self):
        """Start monitoring and publishing temperature data."""
        try:
            mqtt_client = get_mqtt_client(get_catalog_config("mqtt"))
            if mqtt_client:
                register_sensor({"id": self.device_id, "type": "temperature", "zone": self.zone, "status": "active"})
                print(f"[TemperatureSensor] Started for zone: {self.zone}")
            else:
                print(f"[TemperatureSensor] Failed to connect for zone: {self.zone}")
                return
        except:
            print(f"[TemperatureSensor] Connection failed for zone: {self.zone}")
            return
        
        coords = get_coords(self.zone)
        while True:
            try:
                # Simple temperature simulation: normally 60-85°F, occasionally higher (aligned with Fahrenheit thresholds)
                if random.random() < 0.98:  # 98% normal temperatures
                    temp = round(random.uniform(60, 85), 2)
                elif random.random() < 0.015:  # 1.5% warning levels (90°F threshold)
                    temp = round(random.uniform(85, 95), 2)
                else:  # 0.5% critical levels (100°F threshold)
                    temp = round(random.uniform(95, 110), 2)
                
                reading = {
                    "sensor_id": self.device_id, "sensor_type": "temperature", "zone": self.zone,
                    "value": temp, "unit": "F", "timestamp": datetime.now().isoformat(),
                    "location": {"zone": self.zone, "coordinates": coords} if coords else {"zone": self.zone}
                }
                mqtt_client.publish(f"sensors/{self.zone}/temperature", json.dumps(reading))
                print(f"[TemperatureSensor] {self.zone}: {temp}°F")
                time.sleep(5)
            except KeyboardInterrupt:
                break
            except:
                time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        TemperatureSensor(sys.argv[1]).start_monitoring()
    else:
        try:
            from . import sensor_manager
            sensor_manager.main()
        except:
            for zone in get_zones():
                subprocess.Popen([sys.executable, "-m", "src.sensors.temperature_sensor", zone])
            print(f"[Fallback] Started temperature sensors for {len(get_zones())} zones")