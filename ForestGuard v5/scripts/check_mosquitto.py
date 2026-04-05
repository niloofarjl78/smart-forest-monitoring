#!/usr/bin/env python3
"""Check if Mosquitto MQTT broker is running."""

import sys
import subprocess

def is_mosquitto_running():
    """Check if Mosquitto is running."""
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                'tasklist /FI "IMAGENAME eq mosquitto.exe"',
                shell=True, capture_output=True, text=True
            )
            return 'mosquitto.exe' in result.stdout
        else:
            result = subprocess.run(
                ['pgrep', '-x', 'mosquitto'],
                capture_output=True, text=True
            )
            return result.returncode == 0
    except Exception:
        return False

def main():
    """Check and print Mosquitto status."""
    if is_mosquitto_running():
        print("Mosquitto is running")
        return 0
    else:
        print("Mosquitto is not running")
        return 1

if __name__ == "__main__":
    sys.exit(main())
