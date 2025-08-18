#!/bin/bash

# Helper script to set up Apache proxy configuration for the converter app
# Run this after the main deploy.sh script

echo "🔧 Setting up Apache proxy configuration..."

# Check if Apache config files exist
HTTP_CONFIG="/etc/apache2/sites-available/romchip.org.conf"
HTTPS_CONFIG="/etc/apache2/sites-available/romchip.org-le-ssl.conf"

# Function to add proxy config to a file
add_proxy_config() {
    local config_file="$1"
    local is_https="$2"
    
    if [ ! -f "$config_file" ]; then
        echo "⚠️  Config file not found: $config_file"
        return 1
    fi
    
    echo "📝 Adding proxy configuration to: $config_file"
    
    # Backup the original file
    sudo cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Add proxy configuration
    if [ "$is_https" = "true" ]; then
        # For HTTPS, add rewrite rule and proxy config
        sudo sed -i '/DocumentRoot/a\
    # Converter app proxy configuration\
    RewriteEngine On\
    RewriteRule ^/docx-converter$ /docx-converter/ [R=301,L]\
    ProxyPreserveHost On\
    ProxyPass /docx-converter/ http://localhost:5001/\
    ProxyPassReverse /docx-converter/ http://localhost:5001/' "$config_file"
    else
        # For HTTP, just add proxy config
        sudo sed -i '/DocumentRoot/a\
    # Converter app proxy configuration\
    ProxyPreserveHost On\
    ProxyPass /docx-converter/ http://localhost:5001/\
    ProxyPassReverse /docx-converter/ http://localhost:5001/' "$config_file"
    fi
    
    echo "✅ Proxy configuration added to $config_file"
}

# Add to HTTP config
if [ -f "$HTTP_CONFIG" ]; then
    add_proxy_config "$HTTP_CONFIG" "false"
else
    echo "⚠️  HTTP config file not found: $HTTP_CONFIG"
fi

# Add to HTTPS config
if [ -f "$HTTPS_CONFIG" ]; then
    add_proxy_config "$HTTPS_CONFIG" "true"
else
    echo "⚠️  HTTPS config file not found: $HTTPS_CONFIG"
fi

# Test Apache configuration
echo "🧪 Testing Apache configuration..."
sudo apache2ctl configtest

if [ $? -eq 0 ]; then
    echo "✅ Apache configuration test passed"
    echo "🔄 Reloading Apache..."
    sudo systemctl reload apache2
    echo "✅ Apache reloaded successfully"
else
    echo "❌ Apache configuration test failed"
    echo "Please check the configuration files manually"
    exit 1
fi

echo ""
echo "🎉 Apache proxy configuration complete!"
echo "🌐 Your converter app should now be available at:"
echo "   https://romchip.org/docx-converter/"
echo ""
echo "🔧 To test:"
echo "   curl -k https://romchip.org/docx-converter/"
