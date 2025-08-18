#!/bin/bash

# Script to update pandoc to the latest version
# Run this on your server to fix the outdated pandoc issue

set -e

echo "🔄 Updating pandoc to latest version..."

# Check current version
echo "📊 Current pandoc version:"
if command -v pandoc &> /dev/null; then
    pandoc --version | head -1
else
    echo "Pandoc not found"
fi

# Install latest pandoc
echo "📦 Installing latest pandoc..."
PANDOC_VERSION="3.1.4"
PANDOC_ARCH="amd64"
PANDOC_URL="https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-${PANDOC_ARCH}.tar.gz"

# Download and install pandoc
cd /tmp
echo "⬇️  Downloading pandoc ${PANDOC_VERSION}..."
curl -L -O "$PANDOC_URL"

echo "📦 Extracting pandoc..."
tar -xzf "pandoc-${PANDOC_VERSION}-linux-${PANDOC_ARCH}.tar.gz"

echo "🔧 Installing pandoc..."
sudo cp "pandoc-${PANDOC_VERSION}/bin/pandoc" /usr/local/bin/
sudo chmod +x /usr/local/bin/pandoc

# Clean up
echo "🧹 Cleaning up..."
rm -rf "pandoc-${PANDOC_VERSION}" "pandoc-${PANDOC_VERSION}-linux-${PANDOC_ARCH}.tar.gz"

# Verify installation
echo "✅ New pandoc version:"
pandoc --version | head -1

echo "🎉 Pandoc update complete!"
echo "🔄 Restarting converter app..."
sudo systemctl restart converter-app

echo "📊 Checking app status..."
sudo systemctl status converter-app --no-pager

echo "✅ Update complete! Your converter app should now work with the latest pandoc."
