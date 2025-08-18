"""
Configuration settings for the DOCX to JATS converter app.
"""

import os

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    
    # Conversion settings
    CONVERTER_SCRIPT = 'convert-to-md.py'
    
    # Logging settings
    @staticmethod
    def get_log_file():
        """Get the appropriate log file path based on environment."""
        if Config.is_production():
            return '/var/log/converter-app/converter.log'
        else:
            return 'converter.log'  # Local file in main directory
    
    LOG_LEVEL = 'INFO'
    
    @staticmethod
    def is_production():
        """Check if running in production environment."""
        return os.environ.get('FLASK_ENV') == 'production' or os.environ.get('ENVIRONMENT') == 'production'
    
    @staticmethod
    def get_form_action():
        """Get the appropriate form action based on environment."""
        if Config.is_production():
            return "/docx-converter/convert"
        else:
            return "/convert"
    
    @staticmethod
    def get_app_config():
        """Get Flask app configuration."""
        config = {
            'SECRET_KEY': Config.SECRET_KEY,
            'MAX_CONTENT_LENGTH': Config.MAX_CONTENT_LENGTH,
        }
        
        if Config.is_production():
            config['DEBUG'] = False
            config['TESTING'] = False
        else:
            config['DEBUG'] = True
            config['TESTING'] = False
            
        return config
