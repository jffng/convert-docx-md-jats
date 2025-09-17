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
sudo apt install -y python3 python3-pip python3-venv apache2 curl

# Install latest pandoc
echo "📦 Installing latest pandoc..."
PANDOC_VERSION="3.7.0.2"
PANDOC_ARCH="amd64"
PANDOC_URL="https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-${PANDOC_ARCH}.tar.gz"

# Download and install pandoc
cd /tmp
curl -L -O "$PANDOC_URL"
tar -xzf "pandoc-${PANDOC_VERSION}-linux-${PANDOC_ARCH}.tar.gz"
sudo cp "pandoc-${PANDOC_VERSION}/bin/pandoc" /usr/local/bin/
sudo chmod +x /usr/local/bin/pandoc

# Clean up
rm -rf "pandoc-${PANDOC_VERSION}" "pandoc-${PANDOC_VERSION}-linux-${PANDOC_ARCH}.tar.gz"

# Verify installation
echo "✅ Pandoc version: $(pandoc --version | head -1)"

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/html/converter-app
sudo mkdir -p /var/log/converter-app
sudo chown www-data:www-data /var/www/html/converter-app
sudo chown www-data:www-data /var/log/converter-app

# Copy application files (assuming this script is run from the app directory)
echo "📋 Copying application files..."
sudo cp -Rf . /var/www/html/converter-app/
sudo chown -R www-data:www-data /var/www/html/converter-app

# Verify critical files and directories
echo "🔍 Verifying application files..."
if [ ! -f "/var/www/html/converter-app/server.py" ]; then
    echo "❌ server.py not found!"
    exit 1
fi
if [ ! -f "/var/www/html/converter-app/config.py" ]; then
    echo "❌ config.py not found!"
    exit 1
fi
if [ ! -d "/var/www/html/converter-app/templates" ]; then
    echo "❌ templates directory not found!"
    exit 1
fi
if [ ! -f "/var/www/html/converter-app/templates/index.html" ]; then
    echo "❌ templates/index.html not found!"
    exit 1
fi
echo "✅ All critical files verified"

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

# Enable Apache proxy modules
echo "🌐 Setting up Apache proxy modules..."
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod rewrite

# Create Apache configuration snippet
echo "🌐 Creating Apache configuration snippet..."
sudo tee /etc/apache2/conf-available/converter-app-proxy.conf << EOF
# Converter app proxy configuration for Apache
# Add these lines to your existing VirtualHost configuration

# For HTTP VirtualHost (port 80)
ProxyPreserveHost On
ProxyPass /docx-converter/ http://localhost:5001/
ProxyPassReverse /docx-converter/ http://localhost:5001/

# For HTTPS VirtualHost (port 443) - add these lines to your SSL VirtualHost
# RewriteEngine On
# RewriteRule ^/docx-converter$ /docx-converter/ [R=301,L]
# ProxyPreserveHost On
# ProxyPass /docx-converter/ http://localhost:5001/
# ProxyPassReverse /docx-converter/ http://localhost:5001/
EOF

echo "📝 Apache configuration snippet created at: /etc/apache2/conf-available/converter-app-proxy.conf"
echo "📝 You need to manually add the proxy configuration to your existing VirtualHost files:"
echo "   - HTTP: /etc/apache2/sites-available/romchip.org.conf"
echo "   - HTTPS: /etc/apache2/sites-available/romchip.org-ssl.conf"
echo ""
echo "📝 Add these lines to your VirtualHost configurations:"
echo "   ProxyPreserveHost On"
echo "   ProxyPass /docx-converter/ http://localhost:5001/"
echo "   ProxyPassReverse /docx-converter/ http://localhost:5001/"
echo ""
echo "📝 For HTTPS, also add:"
echo "   RewriteEngine On"
echo "   RewriteRule ^/docx-converter$ /docx-converter/ [R=301,L]"

# Set production environment
echo "🔧 Setting production environment..."
export FLASK_ENV=production
export ENVIRONMENT=production

# Test environment configuration
echo "🧪 Testing environment configuration..."
cd /var/www/html/converter-app
source venv/bin/activate
python -c "from config import Config; print('✅ Environment:', 'PRODUCTION' if Config.is_production() else 'DEVELOPMENT'); print('✅ Form action:', Config.get_form_action()); print('✅ Log file:', Config.get_log_file())"

# Start the application
echo "🚀 Starting the application..."
sudo systemctl start converter-app

# Check status
echo "📊 Checking application status..."
sudo systemctl status converter-app --no-pager

echo "✅ Deployment complete!"
echo "🌐 Converter app available at: https://romchip.org/docx-converter/"
echo "📝 Logs available at: /var/log/converter-app/"
echo ""
echo "🔧 Useful commands:"
echo "  sudo systemctl status converter-app"
echo "  sudo systemctl restart converter-app"
echo "  sudo journalctl -u converter-app -f"
echo "  sudo tail -f /var/log/converter-app/error.log"
echo ""
echo "⚠️  IMPORTANT: You still need to manually add the proxy configuration to your Apache VirtualHost files!"
echo "   See the configuration snippet at: /etc/apache2/conf-available/converter-app-proxy.conf"
