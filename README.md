# Anker Solix X1 Modbus Integration

A custom Home Assistant integration to communicate with Anker Solix X1 energy storage systems via Modbus TCP.

This integration was built to replace manual `modbus.yaml` configurations, allowing you to easily set up your inverter from the Home Assistant UI while automatically retaining all your historical Energy Dashboard data!

## Features
- **100% UI Configurable:** No more editing massive YAML files.
- **Data Continuity:** Designed to use the exact same Entity IDs as standard community YAML configurations. Your historical energy statistics will transition seamlessly.
- **Comprehensive:** Maps all 141 known sensors, including PV generation, grid power, battery status, and internal temperatures.

## Supported Entities
This integration exposes all critical metrics across various categories, including but not limited to:
- **Summary Information:** Plant Status, Battery Status, SOC, SOH
- **Power Flow:** PV Power, Grid Power, Load Power, Battery Charge/Discharge Power
- **Energy Counters:** Daily/Total PV Generation, Battery Charge, Feed-in, Purchased Energy
- **PCS Status & Alarms:** Rated Power, MPPT strings, System Alarms (1-8), Internal Temperature
- **Voltage & Current:** PV1-PV4 Voltage and Current, Grid Voltage

## Installation

### Method 1: HACS (Recommended)
1. Open Home Assistant and navigate to **HACS**.
2. Go to **Integrations**, click the three dots in the top right, and select **Custom repositories**.
3. Add `https://github.com/cbource/anker-solix-x1-modbus` as an **Integration**.
4. Click "Install" on the Anker Solix X1 Modbus repository.
5. Restart Home Assistant.

### Method 2: Manual
1. Download the latest release from this repository.
2. Copy the `custom_components/anker_solix_x1` folder into your Home Assistant `config/custom_components` directory.
3. Restart Home Assistant.

## Configuration
1. Before adding the integration, **ensure you disable/comment out your old `modbus.yaml`** configuration and restart Home Assistant. The inverter may drop connections if both the YAML and the integration try to poll simultaneously.
2. Go to **Settings > Devices & Services > Integrations**.
3. Click **Add Integration** and search for "Anker Solix X1".
4. Enter your Inverter's IP Address (e.g., `192.168.0.139`), Port (default `502`), and **Scan Interval**.
   - **Scan Interval (Polling Frequency):** Defines how often the integration queries the inverter for updates. The unit is in **seconds**. 
   - **Recommendation:** A value of `30` seconds is recommended. Setting this too low (e.g., `< 10`) may overwhelm the inverter's Modbus TCP interface and cause connection timeouts, while setting it too high will result in sluggish dashboard updates.
5. Click Submit. All 141 sensors will be automatically created!

## Potential Issues & Troubleshooting
- **Connection Refused / Timeout**: Modbus TCP typically only allows one connection at a time. Make sure you don't have another tool, Node-RED flow, or a residual `modbus.yaml` configuration trying to poll the inverter at the same time.
- **Unavailable Entities**: If your entities show up as unavailable, verify the inverter is online and connected to the same local network as your Home Assistant instance. Check the Home Assistant logs for specific Modbus exceptions.
- **Energy Dashboard Not Updating**: If you transitioned from YAML and the dashboard stopped updating, verify that the new Entity IDs exactly match the old ones. (e.g., `sensor.solix_x1_daily_pv_generation`).

## Disclaimer
This integration is community-supported and not officially affiliated with Anker. Use at your own risk.
