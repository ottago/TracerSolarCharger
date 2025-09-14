# Tracer Solar Charger - Home Assistant Integration

A comprehensive Home Assistant custom component for monitoring Tracer3210AN solar charge controllers via Modbus RTU.

## Features

- **30+ Sensors**: Complete monitoring of PV, battery, load, and system parameters
- **Real-time Data**: Live updates every 30 seconds (configurable)
- **Energy Monitoring**: Daily and total energy generation/consumption tracking
- **Status Monitoring**: Battery status, charging status, and system alerts
- **Device Classes**: Proper Home Assistant device classes for voltage, current, power, energy, and temperature
- **Easy Setup**: Configuration flow with automatic device discovery

## Installation

### Method 1: Manual Installation

1. **Copy the integration files**:
   ```bash
   # Copy the entire folder to your Home Assistant custom_components directory
   cp -r homeassistant/custom_components/tracer_solar_charger /config/custom_components/
   ```

2. **Restart Home Assistant**

3. **Add the integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Tracer Solar Charger"
   - Follow the setup wizard

### Method 2: HACS Installation (if published)

1. **Add custom repository** (if not in default HACS):
   - Go to HACS → Integrations
   - Click the three dots menu → Custom repositories
   - Add repository URL and select "Integration"

2. **Install the integration**:
   - Search for "Tracer Solar Charger" in HACS
   - Click Install
   - Restart Home Assistant

## Configuration

### Setup via UI

1. **Go to Settings → Devices & Services**
2. **Click "Add Integration"**
3. **Search for "Tracer Solar Charger"**
4. **Configure the connection**:
   - **Serial Device Path**: `/dev/ttyUSB0` (or your device path)
   - **Modbus Slave ID**: `1` (default)
   - **Baud Rate**: `115200` (default)

### Manual Configuration (configuration.yaml)

```yaml
tracer_solar_charger:
  device: "/dev/ttyUSB0"
  slave_id: 1
  baudrate: 115200
```

## Available Sensors

### PV (Solar Panel) Sensors
- **PV Voltage** (`sensor.solar_charger_pv_voltage`) - Solar panel voltage
- **PV Current** (`sensor.solar_charger_pv_current`) - Solar panel current
- **PV Power** (`sensor.solar_charger_pv_power`) - Solar panel power output

### Battery Sensors
- **Battery Voltage** (`sensor.solar_charger_battery_voltage`) - Battery voltage
- **Battery Current** (`sensor.solar_charger_battery_current`) - Battery charging current
- **Battery Power** (`sensor.solar_charger_battery_power`) - Battery charging power
- **Battery SOC** (`sensor.solar_charger_battery_state_of_charge`) - State of charge percentage
- **Battery Temperature** (`sensor.solar_charger_battery_temperature`) - Battery temperature

### Load Sensors
- **Load Voltage** (`sensor.solar_charger_load_voltage`) - Load output voltage
- **Load Current** (`sensor.solar_charger_load_current`) - Load current consumption
- **Load Power** (`sensor.solar_charger_load_power`) - Load power consumption

### System Sensors
- **Device Temperature** (`sensor.solar_charger_device_temperature`) - Controller temperature
- **Heat Sink Temperature** (`sensor.solar_charger_heat_sink_temperature`) - Heat sink temperature

### Status Sensors
- **Battery Status** (`sensor.solar_charger_battery_status`) - Battery status and alerts
- **Charging Status** (`sensor.solar_charger_charging_status`) - Charging mode and status
- **Load Status** (`sensor.solar_charger_load_status`) - Load connection status

### Energy Statistics
- **Energy Generated Today** (`sensor.solar_charger_energy_generated_today`) - Daily energy generation
- **Energy Consumed Today** (`sensor.solar_charger_energy_consumed_today`) - Daily energy consumption
- **Total Energy Generated** (`sensor.solar_charger_total_energy_generated`) - Lifetime energy generation
- **Max Battery Voltage Today** (`sensor.solar_charger_max_battery_voltage_today`) - Daily peak voltage
- **Min Battery Voltage Today** (`sensor.solar_charger_min_battery_voltage_today`) - Daily minimum voltage
- **Battery Full Charges** (`sensor.solar_charger_battery_full_charges`) - Total charge cycles
- **Operating Days** (`sensor.solar_charger_operating_days`) - Total operating days

### Configuration Sensors (Read-only)
- **Battery Type** (`sensor.solar_charger_battery_type`) - Configured battery type
- **Battery Capacity** (`sensor.solar_charger_battery_capacity`) - Configured battery capacity
- **Float Voltage Setting** (`sensor.solar_charger_float_voltage_setting`) - Float voltage setting
- **Low Voltage Disconnect Setting** (`sensor.solar_charger_low_voltage_disconnect_setting`) - LVD setting

## Dashboard Examples

### Basic Solar Monitoring Card

```yaml
type: entities
title: Solar Charger Status
entities:
  - entity: sensor.solar_charger_pv_voltage
    name: Solar Voltage
  - entity: sensor.solar_charger_pv_current
    name: Solar Current
  - entity: sensor.solar_charger_pv_power
    name: Solar Power
  - entity: sensor.solar_charger_battery_voltage
    name: Battery Voltage
  - entity: sensor.solar_charger_battery_state_of_charge
    name: Battery SOC
  - entity: sensor.solar_charger_load_power
    name: Load Power
```

### Energy Dashboard Integration

The integration provides energy sensors that work with Home Assistant's Energy Dashboard:

1. **Go to Settings → Dashboards → Energy**
2. **Add Solar Production**:
   - Select `sensor.solar_charger_energy_generated_today`
3. **Add Grid Consumption** (if applicable):
   - Select `sensor.solar_charger_energy_consumed_today`

### Advanced Gauge Card

```yaml
type: gauge
entity: sensor.solar_charger_battery_state_of_charge
name: Battery Level
min: 0
max: 100
severity:
  green: 50
  yellow: 25
  red: 0
```

### Power Flow Card (with custom card)

```yaml
type: custom:power-flow-card
entities:
  grid: sensor.solar_charger_load_power
  solar: sensor.solar_charger_pv_power
  battery: sensor.solar_charger_battery_power
  battery_charge: sensor.solar_charger_battery_state_of_charge
```

## Troubleshooting

### Connection Issues

1. **Check device path**:
   ```bash
   ls -la /dev/tty*
   # Look for your USB-to-RS485 adapter
   ```

2. **Check permissions**:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # Or add homeassistant user to dialout group
   sudo usermod -a -G dialout homeassistant
   ```

3. **Test connection manually**:
   ```bash
   # Use the CLI tool to test
   ./solar-charger --device /dev/ttyUSB0 discover
   ```

### Sensor Issues

1. **Check logs**:
   - Go to Settings → System → Logs
   - Filter by "tracer_solar_charger"

2. **Restart integration**:
   - Go to Settings → Devices & Services
   - Find "Tracer Solar Charger"
   - Click "Restart"

3. **Check sensor availability**:
   - Some sensors may show "unavailable" if the corresponding register is not supported by your device firmware

### Performance Optimization

1. **Adjust scan interval**:
   ```yaml
   # In configuration.yaml
   tracer_solar_charger:
     scan_interval: 60  # Increase to 60 seconds for less frequent updates
   ```

2. **Disable unused sensors**:
   - Go to Settings → Devices & Services
   - Click on your Tracer Solar Charger device
   - Disable sensors you don't need

## Hardware Requirements

- **Tracer3210AN Solar Charge Controller**
- **USB-to-RS485 converter** (or direct serial connection)
- **RJ45 cable** connected according to pinout specification
- **Home Assistant** running on hardware with USB/serial port access

## Technical Details

- **Protocol**: Modbus RTU
- **Baud Rate**: 115200 (configurable)
- **Update Interval**: 30 seconds (configurable)
- **Registers Read**: 80+ registers across multiple function codes
- **Error Handling**: Automatic retry and graceful degradation

## Support

For issues and support:
1. Check the [troubleshooting section](#troubleshooting)
2. Review Home Assistant logs
3. Test with the standalone CLI tool first
4. Open an issue with detailed logs and configuration

## License

This integration is provided as-is for interfacing with Tracer3210AN solar charge controllers.
