#!/bin/bash

# Script to manage log files for the converter app

case "$1" in
    "view"|"show")
        if [ "$2" = "prod" ] || [ "$2" = "production" ]; then
            echo "📋 Showing production logs..."
            sudo tail -f /var/log/converter-app/converter.log
        else
            echo "📋 Showing development logs..."
            if [ -f "converter.log" ]; then
                tail -f converter.log
            else
                echo "No log file found. Run the app first to generate logs."
            fi
        fi
        ;;
    "clear"|"clean")
        if [ "$2" = "prod" ] || [ "$2" = "production" ]; then
            echo "🧹 Clearing production logs..."
            sudo truncate -s 0 /var/log/converter-app/converter.log
            echo "✅ Production logs cleared"
        else
            echo "🧹 Clearing development logs..."
            if [ -f "converter.log" ]; then
                truncate -s 0 converter.log
                echo "✅ Development logs cleared"
            else
                echo "No log file to clear"
            fi
        fi
        ;;
    "info")
        echo "📊 Log file information:"
        echo ""
        echo "Development log:"
        if [ -f "converter.log" ]; then
            echo "  📁 Location: $(pwd)/converter.log"
            echo "  📏 Size: $(du -h converter.log | cut -f1)"
            echo "  📅 Modified: $(stat -c %y converter.log)"
        else
            echo "  ❌ Not found"
        fi
        echo ""
        echo "Production log:"
        if [ -f "/var/log/converter-app/converter.log" ]; then
            echo "  📁 Location: /var/log/converter-app/converter.log"
            echo "  📏 Size: $(sudo du -h /var/log/converter-app/converter.log | cut -f1)"
            echo "  📅 Modified: $(sudo stat -c %y /var/log/converter-app/converter.log)"
        else
            echo "  ❌ Not found"
        fi
        ;;
    *)
        echo "Usage: $0 {view|show|clear|clean|info} [prod|production]"
        echo ""
        echo "Commands:"
        echo "  view/show [prod]    # View logs (development or production)"
        echo "  clear/clean [prod]  # Clear logs (development or production)"
        echo "  info               # Show log file information"
        echo ""
        echo "Examples:"
        echo "  $0 view           # View development logs"
        echo "  $0 view prod      # View production logs"
        echo "  $0 clear          # Clear development logs"
        echo "  $0 info           # Show log file info"
        exit 1
        ;;
esac
