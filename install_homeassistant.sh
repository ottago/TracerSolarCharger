#!/bin/bash

# Installation script for Home Assistant integration

set -e

# Default Home Assistant config directory
HA_CONFIG_DIR="${1:-/config}"
CUSTOM_COMPONENTS_DIR="${HA_CONFIG_DIR}/custom_components"
INTEGRATION_DIR="${CUSTOM_COMPONENTS_DIR}/tracer_solar_charger"

echo "Installing Tracer Solar Charger integration to Home Assistant..."
echo "Target directory: ${INTEGRATION_DIR}"

# Create directories
mkdir -p "${INTEGRATION_DIR}"

# Copy integration files
cp homeassistant_integration/*.py "${INTEGRATION_DIR}/"
cp homeassistant_integration/*.json "${INTEGRATION_DIR}/"

# Copy shared library directly into integration folder
cp -r tracer_solar_charger "${INTEGRATION_DIR}/"

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Restart Home Assistant"
echo "2. Go to Settings → Devices & Services"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Tracer Solar Charger'"
echo "5. Configure your device path and settings"
