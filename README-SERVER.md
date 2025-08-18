# DOCX to JATS Converter - Server Configuration

This document explains the server configuration and environment setup for the Flask application.

## 📁 File Structure

```
convert-docx-md-jats/
├── server.py              # Main Flask application
├── config.py              # Configuration settings
├── templates/
│   └── index.html         # HTML template (extracted from server.py)
├── converter-app.service  # Systemd service configuration
├── gunicorn.conf.py       # Gunicorn configuration
├── set-env.sh            # Environment setup script
└── requirements-production.txt
```

## 🔧 Environment Configuration

The application automatically detects whether it's running in development or production mode based on environment variables.

### Environment Variables

- `FLASK_ENV`: Set to `production` or `development`
- `ENVIRONMENT`: Set to `production` or `development`

### Configuration Differences

| Setting | Development | Production |
|---------|-------------|------------|
| **Form Action** | `/convert` | `/docx-converter/convert` |
| **Debug Mode** | ✅ Enabled | ❌ Disabled |
| **Proxy Config** | ❌ Disabled | ✅ Enabled |
| **Log Level** | INFO | INFO |
| **Log File** | `converter.log` (local) | `/var/log/converter-app/converter.log` |

## 🚀 Running the Application

### Development Mode

```bash
# Set environment to development
source set-env.sh dev

# Run the application
python server.py
```

### Production Mode

```bash
# Set environment to production
source set-env.sh prod

# Run with Gunicorn
gunicorn -c gunicorn.conf.py server:app
```

### Using Systemd Service

```bash
# Start the service (automatically runs in production mode)
sudo systemctl start converter-app

# Check status
sudo systemctl status converter-app

# View logs
sudo journalctl -u converter-app -f
```

## 🔄 Recent Changes

### 1. Template Extraction
- **Before**: HTML template was embedded in `server.py`
- **After**: Template moved to `templates/index.html`
- **Benefit**: Easier maintenance and editing

### 2. Environment-Based Configuration
- **Before**: Hardcoded form action paths
- **After**: Dynamic form action based on environment
- **Benefit**: Works in both development and production without code changes

### 3. Configuration Management
- **Before**: Settings scattered throughout code
- **After**: Centralized in `config.py`
- **Benefit**: Easier to modify settings and add new configurations

## 🛠️ Configuration Options

Edit `config.py` to modify:

- **File upload limits**: `MAX_CONTENT_LENGTH`
- **Logging settings**: `LOG_FILE`, `LOG_LEVEL`
- **Converter script**: `CONVERTER_SCRIPT`
- **Security**: `SECRET_KEY`

## 🔍 Troubleshooting

### Form Action Issues
If the form isn't submitting correctly:

1. **Check environment**:
   ```bash
   echo $FLASK_ENV
   echo $ENVIRONMENT
   ```

2. **Verify form action**:
   - Development: Should be `/convert`
   - Production: Should be `/docx-converter/convert`

### Template Issues
If templates aren't loading:

1. **Check template directory**:
   ```bash
   ls -la templates/
   ```

2. **Verify Flask template path**:
   ```bash
   python -c "from flask import Flask; app = Flask(__name__); print(app.template_folder)"
   ```

### Environment Detection
To test environment detection:

```bash
python -c "from config import Config; print('Production:', Config.is_production()); print('Form action:', Config.get_form_action()); print('Log file:', Config.get_log_file())"
```

### Log File Location
To check where logs are being written:

```bash
# Development
ls -la converter.log

# Production
sudo tail -f /var/log/converter-app/converter.log
```

## 📝 Deployment Notes

When deploying to production:

1. **Run the deployment script**:
   ```bash
   sudo ./deploy.sh
   ```

2. **The script will automatically**:
   - ✅ Install latest pandoc
   - ✅ Copy all application files (including templates)
   - ✅ Verify critical files are present
   - ✅ Set up Python virtual environment
   - ✅ Configure systemd service with production environment
   - ✅ Test environment configuration
   - ✅ Start the application

3. **Manual steps required**:
   - Add Apache proxy configuration to your VirtualHost files
   - Get SSL certificate for subdomain (if using subdomain approach)

The application will automatically:
- Enable proxy configuration
- Use production form actions
- Disable debug mode
- Apply production settings
- Use production log file location
