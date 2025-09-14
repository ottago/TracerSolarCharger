# Solar Charger Interface for Tracer3210AN

A command-line interface and Home Assistant Plugin for monitoring and managing the Tracer3210AN solar
charge controller via Modbus RTU protocol.

## Hardware Details

| Model: Tracer3210AN |
| Voltage 12/24v / Li |
| Current 30A |
| Max PV Voltage 100v |
| Max PV Input Power 390w@12v / 780w@24v |
| HUIZHOU EPERVER TECHNOLOGY CO LTD |

## Features

- **Complete Parameter Access**: Read all 131 available parameters (79 unique parameters across 6 categories)
- **Configuration Writing**: Write 19 configuration parameters with validation and safety checks
- **Real-time Monitoring**: Continuous monitoring with configurable intervals
- **Multiple Output Formats**: Human-readable, JSON, and CSV output
- **Efficient Communication**: Multi-register reads for optimal performance
- **Parameter Categories**: PV, Battery, Load, System, Statistics, and Configuration
- **Device Discovery**: Automatic device detection and connection testing
- **Safety Features**: Parameter validation, dry-run mode, and confirmation prompts
- **Backup/Restore**: Configuration backup and restore functionality
- **Home Assistant Integration**: Complete Home Assistant custom component with 27+ sensors

## Hardware Requirements

- Tracer3210AN Solar Charge Controller
- USB-to-RS485 converter (or direct serial connection)
- RJ45 cable connected according to the pinout specification

## Installation

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

## Usage

### Basic Commands

#### Device Discovery
Test connection and verify device communication:
```bash
./solar-charger --device /dev/ttyUSB0 discover
```

#### List Available Parameters
View all 79 available parameters organized by category:
```bash
./solar-charger list-parameters
./solar-charger list-parameters --category pv --detailed
```

#### Read All Parameters
Get complete device status:
```bash
./solar-charger --device /dev/ttyUSB0 read-all
./solar-charger --device /dev/ttyUSB0 read-all --efficient
./solar-charger --device /dev/ttyUSB0 read-all --category battery
```

#### Read Specific Parameters
Read individual parameters by name:
```bash
./solar-charger --device /dev/ttyUSB0 read battery_voltage load_current pv_voltage
./solar-charger --device /dev/ttyUSB0 read 0x3104 0x3109  # By address
```

#### Real-time Monitoring
Continuous monitoring with live updates:
```bash
./solar-charger --device /dev/ttyUSB0 monitor --interval 5
./solar-charger --device /dev/ttyUSB0 monitor --category battery --interval 2
./solar-charger --device /dev/ttyUSB0 monitor --count 10  # Limited readings
```

### Output Formats

#### Human-readable (default)
```bash
./solar-charger --device /dev/ttyUSB0 read-all
```

#### JSON Output
```bash
./solar-charger --device /dev/ttyUSB0 --format json read-all
./solar-charger --device /dev/ttyUSB0 --format json read battery_voltage
```

#### CSV Output
```bash
./solar-charger --device /dev/ttyUSB0 --format csv read-all --output data.csv
```

#### Export Data
```bash
./solar-charger --device /dev/ttyUSB0 export --include-config
```

### Configuration Management

#### List Writable Parameters
View all parameters that can be modified:
```bash
./solar-charger list-writable
./solar-charger list-writable --detailed --category voltage_protection
```

#### Write Single Parameter
Modify individual configuration parameters:
```bash
./solar-charger --device /dev/ttyUSB0 write battery_capacity 200
./solar-charger --device /dev/ttyUSB0 write float_voltage 13.8
./solar-charger --device /dev/ttyUSB0 write battery_type LiFePO4
```

#### Dry Run Mode
Test parameter changes without writing:
```bash
./solar-charger --device /dev/ttyUSB0 write float_voltage 13.8 --dry-run
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
| 1 | Green Stripe |
| 2 | Green |
| 3 | Orange Stripe |
| 4 | Blue |
| 5 | Blue Stripe |
| 6 | Orange |
| 7 | Brown Stripe |
| 8 | Brown |






## Home Assistant Integration

A complete Home Assistant custom component is included for seamless smart home integration.

### Features
- **27+ Sensor Entities**: Complete monitoring of all solar charger parameters
- **Energy Dashboard**: Integration with Home Assistant's energy tracking
- **Real-time Updates**: Live data every 30 seconds
- **Professional UI**: Proper device classes, icons, and units
- **Easy Setup**: Configuration flow with automatic device discovery

### Installation
```bash
# Copy integration to Home Assistant
cp -r homeassistant/custom_components/tracer_solar_charger /config/custom_components/

# Or use the automated installer
cd homeassistant && ./install.sh
```

### Configuration
1. Restart Home Assistant
2. Go to Settings → Devices & Services
3. Click "Add Integration"
4. Search for "Tracer Solar Charger"
5. Configure your device path and settings

### Available Sensors
- **PV Monitoring**: Solar voltage, current, and power
- **Battery Status**: Voltage, current, SOC, temperature, and status
- **Load Monitoring**: Voltage, current, and power consumption
- **Energy Statistics**: Daily and total energy generation/consumption
- **System Status**: Device temperature, charging status, and alerts
- **Configuration**: Battery type, capacity, and voltage settings

See `homeassistant/README.md` for complete installation and configuration guide.

## Connection Settings

- **Protocol**: Modbus RTU
- **Baud Rate**: 115200 (default)
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Slave ID**: 1 (default)

## Command Line Options

```
--device, -d DEVICE     Serial device path (required for most commands)
--speed, -s SPEED       Serial speed (default: 115200)
--slave-id SLAVE_ID     Modbus slave ID (default: 1)
--timeout TIMEOUT       Communication timeout (default: 2.0s)
--format, -f FORMAT     Output format: human, json, csv (default: human)
--output, -o OUTPUT     Output file (default: stdout)
```

## Examples

### Monitor Battery Status
```bash
./solar-charger --device /dev/ttyUSB0 monitor --category battery --interval 10
```

### Export Daily Statistics
```bash
./solar-charger --device /dev/ttyUSB0 --format json read-all --category statistics --output daily_stats.json
```

### Check System Health
```bash
./solar-charger --device /dev/ttyUSB0 read battery_voltage battery_status charging_equipment_status fault_status
```

### Log Data Continuously
```bash
./solar-charger --device /dev/ttyUSB0 --format csv monitor --interval 60 --output solar_log.csv
```

### Configure Battery Settings
```bash
# Set battery type and capacity
./solar-charger --device /dev/ttyUSB0 write battery_type LiFePO4
./solar-charger --device /dev/ttyUSB0 write battery_capacity 200

# Adjust voltage thresholds
./solar-charger --device /dev/ttyUSB0 write float_voltage 13.8
./solar-charger --device /dev/ttyUSB0 write low_voltage_disconnect 11.1
```

### Backup and Restore Configuration
```bash
# Create backup before making changes
./solar-charger --device /dev/ttyUSB0 backup-config --output my_config_backup.json

# Test changes with dry-run first
./solar-charger --device /dev/ttyUSB0 write float_voltage 13.6 --dry-run

# Apply the change
./solar-charger --device /dev/ttyUSB0 write float_voltage 13.6
```

## Device Information

**Current Device Status** (as of last scan):
- Battery: 13.10V (LiFePO4, 200Ah capacity)
- Load: 1.20A draw (~15W)
- PV: 0.01V (nighttime/no sun)
- Total Generation: 256.88 kWh lifetime
- Operating Days: 21,989 (counter may have overflowed)
- Battery Cycles: 47 full charges

## Troubleshooting

### Power Sensor Values

If power sensors show values that are 100x too large (e.g., 1500W instead of 15W), this indicates a scaling issue. Both the CLI and Home Assistant integration have been updated with the correct scaling (0.01 instead of 1). See `POWER_SCALING_FIX_COMPLETE.md` for details.

### Decimal Formatting

The CLI now formats all floating-point values to 2 decimal places for clean, professional output. If you see excessive decimal places, ensure you have the latest version. See `DECIMAL_FORMATTING_FIX.md` for details.

### Connection Issues
1. Verify device path: `ls /dev/tty*` or `ls /dev/ttyUSB*`
2. Check permissions: `sudo chmod 666 /dev/ttyUSB0`
3. Test with discovery: `./solar-charger --device /dev/ttyUSB0 discover`

### Communication Errors
- **"Illegal Data Address"**: Some registers may not be available on all firmware versions
- **Timeout errors**: Try increasing `--timeout` value
- **No response**: Check baud rate and slave ID settings

### Parameter Issues
- Use `list-parameters` to see all available parameters
- Some parameters may return 0 or invalid values depending on device state
- Multi-word values (power, energy) use separate high/low registers

## Technical Details

- **Total Registers Mapped**: 131 (57 input + 74 holding registers)
- **Function Codes**: FC04 (Input Registers), FC03 (Holding Registers)
- **Multi-register Support**: Up to 16 registers per read (FC04), 8 registers per read (FC03)
- **Efficient Reading**: Optimized register blocks for fast data collection
- **Error Handling**: Comprehensive Modbus error detection and reporting

## Files Structure

```
TracerSolarCharger/
├── solar-charger              # Main CLI executable
├── src/
│   ├── main.py               # CLI application
│   ├── communication/
│   │   └── modbus_client.py  # Modbus RTU client
│   └── models/
│       └── device_data.py    # Data models and formatting
├── parameter_definitions.py   # Complete parameter mapping
├── register_map.json        # Discovered register data
├── register_map.md          # Human-readable register documentation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```


## Contributing

Feel free to submit issues, improvements, or additional device support.
