# Solar Charger Interface for Tracer3210AN

A unified library and command-line interface for monitoring and managing the Tracer3210AN solar charge controller via Modbus RTU protocol, with Home Assistant integration.

## Features

- **Shared Core Library**: Common codebase for CLI and Home Assistant integration
- **Complete Parameter Access**: Read all 131 available parameters (79 unique parameters across 6 categories)
- **Configuration Writing**: Write 19 configuration parameters with validation and safety checks
- **Real-time Monitoring**: Continuous monitoring with configurable intervals
- **Multiple Output Formats**: Human-readable, JSON, and CSV output
- **Home Assistant Integration**: Complete custom component with 27+ sensors
- **Simplified Structure**: Flat folder structure with shared modules

## iSupported Hardware
This software has only been testes with the following hardware.  It may work for others.

    Model: Tracer3210AN
    Voltage 12/24v / Li
    Current 30A
    Max PV Voltage 100v
    Max PV Input Power 390w@12v / 780w@24v
    HUIZHOU EPERVER TECHNOLOGY CO LTD


## Project Structure

```
TracerSolarCharger/
├── tracer_solar_charger/          # Shared core library
│   ├── __init__.py
│   ├── modbus_client.py           # Modbus RTU communication
│   ├── device_data.py             # Data models and formatting
│   └── parameter_definitions.py   # Complete parameter mapping
├── cli.py                         # Command-line interface
├── solar-charger                  # CLI launcher script
├── homeassistant_integration/     # Home Assistant custom component
│   ├── __init__.py
│   ├── sensor.py
│   ├── config_flow.py
│   ├── const.py
│   ├── manifest.json
│   └── strings.json
├── install_homeassistant.sh       # HA integration installer
```

#### Backup and Restore Configuration
```bash
# Backup current settings
./solar-charger --device /dev/ttyUSB0 backup-config

# Restore from backup
./solar-charger --device /dev/ttyUSB0 restore-config backup_file.json
```

#### Write Multiple Parameters
Apply battery type with recommended settings:
```bash
./solar-charger --device /dev/ttyUSB0 write-config --battery-type LiFePO4
./solar-charger --device /dev/ttyUSB0 write-config --battery-capacity 200
./solar-charger --device /dev/ttyUSB0 write-config --config-file my_settings.json
```

## Parameter Categories

### PV Parameters (4 parameters)
- `pv_voltage` - PV Array Voltage (V)
- `pv_current` - PV Array Current (A)  
- `pv_power_low/high` - PV Power (W)

### Battery Parameters (11 parameters)
- `battery_voltage` - Battery Voltage (V)
- `battery_current` - Battery Charging Current (A)
- `battery_soc` - Battery State of Charge (%)
- `battery_temp` - Battery Temperature (°C)
- `battery_status` - Battery Status (bitfield)
- And more...

### Load Parameters (9 parameters)
- `load_voltage` - Load Voltage (V)
- `load_current` - Load Current (A)
- `load_power_combined` - Load Power (W)
- `load_status` - Load Status
- And more...

### System Parameters (12 parameters)
- `device_temp` - Device Temperature (°C)
- `charging_equipment_status` - Charging Status (bitfield)
- `discharging_equipment_status` - Discharging Status (bitfield)
- `fault_status` - Fault Status
- And more...

### Statistics Parameters (21 parameters)
- `generated_energy_today_*` - Daily Energy Generation (kWh)
- `consumed_energy_today_*` - Daily Energy Consumption (kWh)
- `max_battery_voltage_today` - Daily Max Battery Voltage (V)
- `operating_days_total` - Total Operating Days
- And more...

### Configuration Parameters (22 parameters)
- `battery_type` - Battery Type (enum)
- `battery_capacity` - Battery Capacity (Ah)
- `float_voltage` - Float Voltage (V)
- `low_voltage_disconnect` - Low Voltage Disconnect (V)
- And more...


## Writable Parameters (19 total)

### Battery Configuration (3 parameters)
- `battery_type` - Battery Type (User Defined, Sealed, GEL, Flooded, LiFePO4)
- `battery_capacity` - Battery Capacity (10-1000 Ah)
- `temperature_compensation` - Temperature Compensation (0-500 mV/°C/2V)

### Voltage Protection (3 parameters)
- `high_voltage_disconnect` - High Voltage Disconnect (12.0-17.0V) ⚠️ CRITICAL
- `charging_limit_voltage` - Charging Limit Voltage (12.0-17.0V)
- `over_voltage_reconnect` - Over Voltage Reconnect (12.0-17.0V)

### Charging Voltages (4 parameters)
- `equalization_voltage` - Equalization Voltage (12.0-17.0V)
- `boost_voltage` - Boost Voltage (12.0-17.0V)
- `float_voltage` - Float Voltage (12.0-16.0V)
- `boost_reconnect_voltage` - Boost Reconnect Voltage (10.0-15.0V)

### Load Protection (5 parameters)
- `low_voltage_reconnect` - Low Voltage Reconnect (10.0-15.0V)
- `under_voltage_recover` - Under Voltage Recover (10.0-15.0V)
- `under_voltage_warning` - Under Voltage Warning (10.0-15.0V)
- `low_voltage_disconnect` - Low Voltage Disconnect (9.0-14.0V) ⚠️ CRITICAL
- `discharging_limit_voltage` - Discharging Limit Voltage (9.0-14.0V)

### Charging Timing (2 parameters)
- `equalization_duration` - Equalization Duration (0-300 min)
- `boost_duration` - Boost Duration (10-300 min)

### Load Control (2 parameters)
- `discharge_percentage` - Discharge Percentage (20-100%)
- `charging_percentage` - Charging Percentage (0-100%)


### RJ45 to RS485 wiring diagram

Source: https://manuals.plus/epever/tcp-rj45-a-tcp-serial-device-server-manual
| Pin | Definition | Break out cable |
|-----|------------|-----------------|
| 1 | +5v | Green Stripe |
| 2 | +5v | Green |
| 3 | RS485-B | Orange Stripe |
| 4 | RS485-B | Blue |
| 5 | RS485-A | Blue Stripe |
| 6 | RS485-A | Orange |
| 7 | GND | Brown Stripe
| 8 | GND | Brown |

### Ethernet cable at charger end - This is T-568A standard

| Pin | Colour |
|-----|--------|
| 1 | Green Stripe |
| 2 | Green |
| 3 | Orange Stripe |
| 4 | Blue |
| 5 | Blue Stripe |
| 6 | Orange |
| 7 | Brown Stripe |
| 8 | Brown |




## Installation

### CLI Installation

1. **Clone or download the project**
2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Make the CLI executable**:
   ```bash
   chmod +x solar-charger
   ```

### Home Assistant Installation

Run the installation script:
```bash
./install_homeassistant.sh /path/to/homeassistant/config
```

Or manually copy files:
```bash
# Copy integration to Home Assistant
cp -r homeassistant_integration /config/custom_components/tracer_solar_charger
cp -r tracer_solar_charger /config/custom_components/tracer_solar_charger/
```

## Usage

### CLI Commands

#### Device Discovery
```bash
./solar-charger --device /dev/ttyUSB0 discover
```

#### List Available Parameters
```bash
./solar-charger list-parameters
./solar-charger list-parameters --category pv --detailed
```

#### Read Parameters
```bash
# Read specific parameters
./solar-charger --device /dev/ttyUSB0 read battery_voltage pv_voltage

# Read all parameters
./solar-charger --device /dev/ttyUSB0 read-all

# Read by category
./solar-charger --device /dev/ttyUSB0 read-all --category battery
```

#### Output Formats
```bash
# JSON output
./solar-charger --device /dev/ttyUSB0 --format json read-all

# CSV output
./solar-charger --device /dev/ttyUSB0 --format csv read-all --output data.csv
```

### Home Assistant Setup

1. Restart Home Assistant after installation
2. Go to Settings → Devices & Services
3. Click "Add Integration"
4. Search for "Tracer Solar Charger"
5. Configure your device path and settings

## Key Improvements

### Code Sharing
- **Single Modbus Client**: Both CLI and HA use the same `ModbusRTUClient`
- **Shared Parameters**: Single source of truth in `parameter_definitions.py`
- **Common Data Models**: Unified `DeviceData` class for formatting

### Simplified Structure
- **Flat Layout**: No deeply nested folders
- **Clear Separation**: Core library, CLI, and HA integration are distinct
- **Easy Maintenance**: Changes to core functionality automatically benefit both interfaces

### Reduced Duplication
- **Eliminated**: Duplicate modbus clients, parameter definitions, and data handling
- **Unified**: Single codebase for device communication
- **Consistent**: Same scaling, formatting, and error handling everywhere

## Migration from Old Structure

The old structure had:
- `src/` folder with nested modules
- Duplicate modbus clients in CLI and HA
- Separate parameter definitions
- Complex folder hierarchy

The new structure provides:
- Shared `tracer_solar_charger/` library
- Single modbus client implementation
- Unified parameter definitions
- Flat, maintainable structure

## Hardware Requirements

- Tracer3210AN Solar Charge Controller
- USB-to-RS485 converter (or direct serial connection)
- RJ45 cable connected according to the pinout specification

## Connection Settings

- **Protocol**: Modbus RTU
- **Baud Rate**: 115200 (default)
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Slave ID**: 1 (default)

## Development

### Adding New Parameters

1. Add parameter definition to `tracer_solar_charger/parameter_definitions.py`
2. Parameters automatically available in both CLI and Home Assistant

### Extending Functionality

1. Add methods to `ModbusRTUClient` for new communication features
2. Extend `DeviceData` for new formatting options
3. Both CLI and HA integration benefit automatically

