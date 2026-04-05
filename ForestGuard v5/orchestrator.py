#!/usr/bin/env python3
"""Orchestrator service for managing all Forest Guard components."""
import subprocess, os, time, argparse, sys
from datetime import datetime

class ForestGuardOrchestrator:
    """Manages starting and stopping of all Forest Guard services."""
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.services = [
            ("MQTT_Broker", [sys.executable, "scripts/check_mosquitto.py"]),
            ("Catalog", [sys.executable, "-m", "src.catalog.catalog"]),
            ("Dashboard", [sys.executable, "-m", "src.dashboard.app"]),
            ("Data_Processor", [sys.executable, "-m", "src.data_processor.processor"]),
            ("Alert_Manager", [sys.executable, "-m", "src.alert_manager.alerts"]),
            ("GeoJSON_Service", [sys.executable, "-m", "src.geojson.geojson_service"]),
            ("Telegram_Bot", [sys.executable, "-m", "src.telegram_bot.bot"]),
            ("Sensor_Manager", [sys.executable, "-m", "src.sensors.sensor_manager"])
        ]

    def log(self, msg):
        """Log a message with timestamp."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def wipe_data(self):
        """Remove temporary data and reset sensor state."""
        running_sensors = os.path.join(self.root_dir, 'running_sensors.json')
        if os.path.exists(running_sensors):
            os.remove(running_sensors)
        wipe_script = os.path.join(self.root_dir, 'scripts', 'wipe_mongodb.py')
        if os.path.exists(wipe_script):
            subprocess.run([sys.executable, wipe_script, '--sensors-only'], capture_output=True)

    def start_service(self, name, cmd):
        """Start a single service in a new command window."""
        if name == "MQTT_Broker":
            result = subprocess.run([sys.executable, "scripts/check_mosquitto.py"], capture_output=True, text=True)
            if "Mosquitto is running" in result.stdout:
                return self.log("MQTT already running")
        self.log(f"Starting {name}")
        
        cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
        full_cmd = f'start "Forest Guard - {name}" cmd /k "cd /d "{self.root_dir}" && {cmd_str}"'
        
        subprocess.Popen(full_cmd, shell=True, cwd=self.root_dir)
        time.sleep(1.5)

    def start_all(self, skip_wipe=False):
        """Start all Forest Guard services in the correct order."""
        if not skip_wipe:
            self.wipe_data()
        self.log("Starting Forest Guard System...")
        for name, cmd in self.services:
            self.start_service(name, cmd)
        self.log("All services started! Dashboard: http://localhost:5001")

    def stop_all(self):
        """Stop all running Forest Guard services."""
        self.log("Stopping all services...")
        for proc in ["python.exe", "mosquitto.exe"]:
            subprocess.run(f'taskkill /F /IM {proc}', shell=True, capture_output=True)
        self.log("System stopped")

def main():
    """Entry point for the Forest Guard orchestrator."""
    parser = argparse.ArgumentParser(description="Forest Guard Orchestrator")
    parser.add_argument('--stop', action='store_true', help='Stop all services')
    parser.add_argument('--skip-wipe', action='store_true', help='Skip wiping data')
    args = parser.parse_args()
    
    orchestrator = ForestGuardOrchestrator()
    if args.stop:
        orchestrator.stop_all()
    else:
        orchestrator.start_all(skip_wipe=args.skip_wipe)

if __name__ == "__main__":
    main()
