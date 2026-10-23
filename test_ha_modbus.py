#!/usr/bin/env python3
"""Test script to debug Home Assistant modbus issues"""

from tracer_solar_charger import ModbusRTUClient, PARAMETERS

# Test the same parameters that HA tries to read
SENSOR_PARAMETERS = [
    "pv_voltage",
    "pv_current", 
    "battery_voltage",
    "battery_current",
    "load_voltage",
    "load_current"
]

def test_modbus(port):
    print(f"Testing modbus connection to {port}")
    
    with ModbusRTUClient(port, 115200, 1, timeout=1.0) as client:
        if not client.connect():
            print("❌ Failed to connect")
            return False
            
        print("✅ Connected successfully")
        
        for param_name in SENSOR_PARAMETERS:
            if param_name not in PARAMETERS:
                print(f"⚠️  Parameter {param_name} not found")
                continue
                
            param = PARAMETERS[param_name]
            address = param['address']
            
            try:
                if param.get('function_code') == 4:
                    result = client.read_input_registers(address, 1)
                else:
                    result = client.read_holding_registers(address, 1)
                    
                if result:
                    raw_value = result[0]
                    scaled_value = raw_value * param.get('scale', 1)
                    print(f"✅ {param_name}: {raw_value} -> {scaled_value} {param.get('unit', '')}")
                else:
                    print(f"❌ {param_name}: No data returned")
                    
            except Exception as e:
                print(f"❌ {param_name}: Error - {e}")
                
        return True

if __name__ == "__main__":
    import sys
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
    test_modbus(port)
