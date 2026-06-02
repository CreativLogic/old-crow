#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/raven-ui.service"

if [ ! -f "$SERVICE_FILE" ]; then
  echo "Error: raven-ui.service not found in $SCRIPT_DIR"
  exit 1
fi

echo "Installing RAVEN UI service..."
echo "Make sure you've edited raven-ui.service with your username and paths first!"
echo ""

sudo cp "$SERVICE_FILE" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable raven-ui
sudo systemctl start raven-ui
sudo systemctl status raven-ui
