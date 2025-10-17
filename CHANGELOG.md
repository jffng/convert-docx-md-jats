# Changelog

All notable changes to the DOCX to JATS XML Converter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-17

### Added
- Comprehensive workflow instructions for OJS article preparation
- Step-by-step guide with visual indicators and formatting examples
- Mobile-responsive design for workflow instructions
- Pure CSS framework integration (3.7KB gzipped)

## [1.0.0] - 2025-09-18

### Added
- Initial release of DOCX to JATS XML Converter web application
- DOCX to Markdown conversion with academic formatting support
- Markdown to JATS XML conversion with full JATS compliance
- Web interface with Flask backend
- Production deployment support with Gunicorn
- Semantic versioning implementation

### Technical Details
- Built with Python 3.12+ and Flask 2.0+
- Uses pandoc for high-quality document conversion
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
| 1.1.0 | 2025-10-17 | Added workflow instructions and enhanced UI |
| 1.0.0 | 2025-09-18 | Initial release with full conversion capabilities |

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/) principles:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

## Contributing

When contributing to this project, please update this changelog with your changes following the established format.