"""
Simplified Sensor Manager - Centralized sensor lifecycle management.
"""
import sys, subprocess, json, os, psutil, requests

PROCESS_FILE = "running_sensors.json"
SENSORS = {'humidity': 'src.sensors.humidity_sensor', 'temperature': 'src.sensors.temperature_sensor', 'smoke': 'src.sensors.smoke_sensor'}

def load_processes():
    """Load and validate running processes"""
    try:
        if os.path.exists(PROCESS_FILE):
            with open(PROCESS_FILE, 'r') as f:
                return {k: v for k, v in json.load(f).items() if psutil.pid_exists(v)}
    except: pass
    return {}

def save_processes(processes):
    """Save process tracking to file"""
    try:
        with open(PROCESS_FILE, 'w') as f:
            json.dump(processes, f)
    except Exception as e:
        print(f"Save error: {e}")

def get_zones():
    """Fetch zones from catalog service"""
    try:
        resp = requests.get("http://localhost:5002/api/config/locations", timeout=5)
        return [loc['zone'] for loc in resp.json().get('locations', [])] if resp.status_code == 200 else []
    except:
        return []

def manage_sensor(action, sensor_type, zone, processes):
    """Start or stop a sensor"""
    key = f"{sensor_type}_{zone}"
    
    if action == "start":
        if key in processes:
            print(f"{sensor_type} sensor for {zone} already running.")
            return False
        if sensor_type not in SENSORS:
            print(f"Unknown sensor: {sensor_type}")
            return False
        try:
            proc = subprocess.Popen([sys.executable, "-m", SENSORS[sensor_type], zone])
            processes[key] = proc.pid
            print(f"Started {sensor_type} sensor for {zone}.")
            return True
        except Exception as e:
            print(f"Start failed: {e}")
            return False
    
    elif action == "stop":
        pid = processes.get(key)
        if not pid:
            print(f"No running {sensor_type} sensor for {zone}")
            return False
        try:
            psutil.Process(pid).terminate()
            del processes[key]
            print(f"Stopped {sensor_type} sensor for {zone}.")
            return True
        except psutil.NoSuchProcess:
            del processes[key]
            print(f"{sensor_type} sensor for {zone} already stopped.")
            return True
        except Exception as e:
            print(f"Stop failed: {e}")
            return False

def main():
    processes = load_processes()
    
    # No arguments: Start all sensors
    if len(sys.argv) == 1:
        print("Starting all sensors...")
        for zone in get_zones():
            for sensor_type in SENSORS:
                manage_sensor("start", sensor_type, zone, processes)
        save_processes(processes)
        print("All sensors started. Press Ctrl+C to stop.")
        try:
            while True: pass
        except KeyboardInterrupt:
            print("\nStopping all sensors...")
            for pid in processes.values():
                try: psutil.Process(pid).terminate()
                except: pass
            save_processes({})
            print("All sensors stopped.")
        return
    
    # Dynamic control: start/stop sensor_type zone
    if len(sys.argv) == 4 and sys.argv[1] in ["start", "stop"] and sys.argv[2] in SENSORS:
        action, sensor_type, zone = sys.argv[1], sys.argv[2], sys.argv[3]
        manage_sensor(action, sensor_type, zone, processes)
        save_processes(processes)
    else:
        print("Usage:")
        print("  python -m src.sensors.sensor_manager start <sensor_type> <zone>")
        print("  python -m src.sensors.sensor_manager stop <sensor_type> <zone>")
        print("  python -m src.sensors.sensor_manager  # Start all sensors")

if __name__ == "__main__":
    main()