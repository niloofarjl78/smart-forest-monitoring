 ForestGuard IoT System

ForestGuard is an IoT-based forest monitoring system that detects potential fire hazards using environmental sensors. It provides real-time monitoring and alerting for forested areas across multiple zones.

 Key Features

- Real-time environmental monitoring (temperature, humidity, smoke)
- Multi-zone sensor deployment
- Instant Telegram alerts for critical conditions
- Web-based dashboard for monitoring
- Centralized service management
- MQTT-based sensor communication

 Quick Start

Prerequisites
- Python 3.8+
- MongoDB
- Mosquitto MQTT Broker

Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Running the System

Start all services with a single command:
```bash
python orchestrator.py
```

Access the dashboard at: http://localhost:5001

Startup Sequence

The system follows this startup order when launched via the orchestrator:

1. MQTT Broker (Mosquitto) - Message broker for sensor communication
2. Catalog Service (Port 5002) - Central configuration and service registry
3. Dashboard (Port 5001) - Web interface for monitoring
4. Data Processor (Port 5005) - Processes and stores sensor data
5. Alert Manager (Port 5004) - Handles alert generation
6. GeoJSON Service - Provides geographical data for the dashboard
7. Telegram Bot - Sends alerts to configured users
8. Sensor Manager - Manages sensor nodes and data collection

Manual Startup (Without Orchestrator)

If you need to start services individually, use these commands in separate terminal windows:

| Service | Command | Port | Notes |
|---------|---------|------|-------|
| MQTT Broker | `mosquitto -v` | 1883 | Must be running first |
| Catalog | `python -m src.catalog.catalog` | 5002 | Central configuration |
| Dashboard | `python -m src.dashboard.app` | 5001 | Web interface |
| Data Processor | `python -m src.data_processor.processor` | 5005 | Data processing |
| Alert Manager | `python -m src.alert_manager.alerts` | 5004 | Alert handling |
| GeoJSON Service | `python -m src.geojson.geojson_service` | - | Map data |
| Telegram Bot | `python -m src.telegram_bot.bot` | - | Notifications |
| Sensor Manager | `python -m src.sensors.sensor_manager` | - | Sensor control |

Configuration

Edit `config/config.yaml` to modify system settings, including:
- MQTT broker details
- MongoDB connection
- Sensor configurations
- Alert thresholds

Ports

| Service | Port |
|---------|------|
| Dashboard | 5001 |
| Catalog | 5002 |
| Alert Manager | 5004 |
| Data Processor | 5005 |
| MQTT Broker | 1883 |
| MongoDB | 27017 |

License

MIT
