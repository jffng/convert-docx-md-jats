#!/bin/bash

# DOCX to JATS Converter App Deployment Script
# For Ubuntu 22.04 LTS

set -e

echo "🚀 Deploying DOCX to JATS Converter App..."

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx pandoc

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/html/converter-app
sudo mkdir -p /var/log/converter-app
sudo chown www-data:www-data /var/www/html/converter-app
sudo chown www-data:www-data /var/log/converter-app

# Copy application files (assuming this script is run from the app directory)
echo "📋 Copying application files..."
sudo cp -r . /var/www/html/converter-app/
sudo chown -R www-data:www-data /var/www/html/converter-app

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd /var/www/html/converter-app
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install --upgrade pip
sudo -u www-data ./venv/bin/pip install -r requirements-production.txt

# Set up systemd service
echo "⚙️ Setting up systemd service..."
sudo cp converter-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable converter-app

# Create nginx configuration
echo "🌐 Setting up nginx configuration..."
sudo tee /etc/nginx/sites-available/converter-app << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # OJS configuration (adjust path as needed)
    location / {
        proxy_pass http://localhost:8080;  # Adjust OJS port
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Converter app configuration
    location /converter/ {
        proxy_pass http://localhost:5001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # File upload limits
        client_max_body_size 50M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/converter-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start the application
echo "🚀 Starting the application..."
sudo systemctl start converter-app

# Check status
echo "📊 Checking application status..."
sudo systemctl status converter-app --no-pager

echo "✅ Deployment complete!"
echo "🌐 Converter app available at: http://your-domain.com/converter/"
echo "📝 Logs available at: /var/log/converter-app/"
echo ""
echo "🔧 Useful commands:"
echo "  sudo systemctl status converter-app"
echo "  sudo systemctl restart converter-app"
echo "  sudo journalctl -u converter-app -f"
echo "  sudo tail -f /var/log/converter-app/error.log"
