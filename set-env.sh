#!/bin/bash

# Script to set environment variables for the converter app

case "$1" in
    "dev"|"development")
        echo "🔧 Setting environment to DEVELOPMENT"
        export FLASK_ENV=development
        export ENVIRONMENT=development
        echo "✅ Environment set to development"
        echo "   - Form action will be: /convert"
        echo "   - Debug mode: enabled"
        echo "   - Proxy configuration: disabled"
        ;;
    "prod"|"production")
        echo "🌐 Setting environment to PRODUCTION"
        export FLASK_ENV=production
        export ENVIRONMENT=production
        echo "✅ Environment set to production"
        echo "   - Form action will be: /docx-converter/convert"
        echo "   - Debug mode: disabled"
        echo "   - Proxy configuration: enabled"
        ;;
    *)
        echo "Usage: $0 {dev|development|prod|production}"
        echo ""
        echo "Examples:"
        echo "  $0 dev      # Set to development mode"
        echo "  $0 prod     # Set to production mode"
        echo ""
        echo "Current environment:"
        echo "  FLASK_ENV: ${FLASK_ENV:-not set}"
        echo "  ENVIRONMENT: ${ENVIRONMENT:-not set}"
        exit 1
        ;;
esac

echo ""
echo "To apply these settings, run:"
echo "  source $0 $1"
echo ""
echo "Or to run the app with these settings:"
echo "  FLASK_ENV=$FLASK_ENV ENVIRONMENT=$ENVIRONMENT python server.py"
