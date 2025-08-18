#!/bin/bash

# Quick fix for pandoc PATH issue in systemd service

echo "🔧 Fixing pandoc PATH issue..."

# Update the systemd service file
echo "📝 Updating systemd service configuration..."
sudo sed -i 's|Environment=PATH=/var/www/html/converter-app/venv/bin|Environment=PATH=/var/www/html/converter-app/venv/bin:/usr/local/bin:/usr/bin:/bin|' /etc/systemd/system/converter-app.service

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Restart the service
echo "🔄 Restarting converter app..."
sudo systemctl restart converter-app

# Check status
echo "📊 Checking app status..."
sudo systemctl status converter-app --no-pager

echo "✅ Fix applied! The converter app should now be able to find pandoc."
