"""
Version information for the DOCX to JATS XML Converter application.
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

def get_version():
    """Return the current version string."""
    return __version__

def get_version_info():
    """Return the current version as a tuple."""
    return __version_info__

def get_version_display():
    """Return a formatted version string for display."""
    return f"v{__version__}"
