# Changelog

All notable changes to the DOCX to JATS XML Converter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-27

### Added
- Initial release of the DOCX to JATS XML Converter web application
- **DOCX to Markdown conversion** with academic formatting support
  - Footnotes preservation using pandoc's footnote syntax
  - Citation support for academic references
  - Table formatting with multiline structure preservation
  - Image handling with dimension removal
  - Content structure preservation
  - Formatting fixes for split bold segments
  - Italics consolidation and underscore format conversion
- **Markdown to JATS XML conversion** with full compliance
  - JATS archiving XML format generation
  - Figure parsing with proper JATS XML elements
  - Section wrapping with unique ID generation
  - Academic document hierarchy maintenance
  - Cross-reference preservation
- **Web interface** with Flask backend
  - File upload functionality for .docx and .md files
  - Conversion type selection (DOCX→Markdown, Markdown→JATS, DOCX→JATS)
  - Real-time conversion options based on file type
  - Error handling and user feedback
  - File download functionality
- **Production deployment support**
  - Gunicorn WSGI server configuration
  - Reverse proxy support with ProxyFix
  - Logging with rotating file handlers
  - Environment-based configuration
  - Systemd service configuration
- **Semantic versioning** implementation
  - Version tracking with `version.py` module
  - Version display in web interface
  - Changelog documentation

### Technical Details
- Built with Python 3.12+ and Flask 2.0+
- Uses pandoc for high-quality document conversion
- Supports academic publishing standards
- Modular architecture with separate converter modules
- Comprehensive error handling and logging
- Cross-platform compatibility (macOS, Linux, Windows)

### Dependencies
- Flask >= 2.0.0
- Gunicorn >= 20.0.0
- Werkzeug >= 2.0.0
- pandoc (system dependency)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-01-27 | Initial release with full DOCX/Markdown/JATS conversion capabilities |

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/) principles:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

## Contributing

When contributing to this project, please update this changelog with your changes following the established format.
