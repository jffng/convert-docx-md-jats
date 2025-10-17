import os
import tempfile
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask, request, send_file, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from version import get_version, get_version_display

def get_changelog_content():
    """Read and return the changelog content for display."""
    try:
        changelog_path = Path("CHANGELOG.md")
        if changelog_path.exists():
            content = changelog_path.read_text(encoding='utf-8')
            # Extract just the version entries (skip the header and metadata)
            lines = content.split('\n')
            start_index = 0
            for i, line in enumerate(lines):
                if line.startswith('## ['):
                    start_index = i
                    break
            
            # Get content from first version entry onwards
            changelog_content = '\n'.join(lines[start_index:])
            return changelog_content
        return "Changelog not available"
    except Exception as e:
        logger.error(f"Error reading changelog: {str(e)}")
        return "Error loading changelog"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create file handler which logs even debug messages
file_handler = RotatingFileHandler(
    Config.get_log_file(),
    maxBytes=1024*1024,
    backupCount=10
)
file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))

# Add the handlers to the logger
logger.addHandler(file_handler)

app = Flask(__name__)

# Apply configuration
app.config.update(Config.get_app_config())

# Configure for reverse proxy only in production
if Config.is_production():
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
        x_prefix=1
    )
    logger.info("🌐 Running in PRODUCTION mode with proxy configuration")
else:
    logger.info("🔧 Running in DEVELOPMENT mode")

def _run_conversion(cmd):
    """Helper function to run conversion commands with detailed logging."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Command succeeded: {' '.join(cmd)}")
        logger.debug(f"Command stdout: {result.stdout}")
        if result.stderr:
            logger.debug(f"Command stderr: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        logger.error(f"Command output: {e.stdout}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running command: {str(e)}")
        return False

# Template configuration - now handled by Config class

@app.route('/')
def index():
    """Handle requests to /docx-converter/"""
    return render_template('index.html', 
                         form_action=Config.get_form_action(),
                         app_version=get_version_display(),
                         changelog_content=get_changelog_content())

@app.route('/convert', methods=['POST'])
def convert():
    """Handle document conversion."""
    try:
        # Check if file was uploaded
        if 'document' not in request.files:
            return render_template('index.html', 
                                form_action=Config.get_form_action(),
                                app_version=get_version_display(),
                                changelog_content=get_changelog_content(),
                                message="No file uploaded", error=True)

        file = request.files['document']
        if file.filename == '':
            return render_template('index.html', 
                                form_action=Config.get_form_action(),
                                app_version=get_version_display(),
                                changelog_content=get_changelog_content(),
                                message="No file selected", error=True)

        # Determine conversion type based on file extension
        input_file = Path(file.filename)
        file_extension = input_file.suffix.lower()

        # Check if user wants JATS conversion (for DOCX files)
        convert_to_jats = request.form.get('convert-to-jats') == 'on'

        if file_extension == '.docx':
            if convert_to_jats:
                format_type = 'docx-to-jats'
            else:
                format_type = 'markdown'
        elif file_extension == '.md':
            format_type = 'jats'
        else:
            return render_template('index.html', 
                                form_action=Config.get_form_action(),
                                app_version=get_version_display(),
                                changelog_content=get_changelog_content(),
                                message="Unsupported file type. Please upload a .docx or .md file.", error=True)

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            input_path = os.path.join(temp_dir, file.filename)
            file.save(input_path)

            # Determine output filename and extension
            if format_type == 'markdown':
                output_filename = input_file.stem + '.md'
                output_path = os.path.join(temp_dir, output_filename)
                # Use convert-to-md.py for DOCX to Markdown
                cmd = ['python', Config.CONVERTER_SCRIPT, input_path, '-o', output_path]
                success = _run_conversion(cmd)

            elif format_type == 'jats':
                output_filename = input_file.stem + '.xml'
                output_path = os.path.join(temp_dir, output_filename)
                # Use convert-to-md.py for Markdown to JATS XML
                cmd = ['python', Config.CONVERTER_SCRIPT, input_path, '-o', output_path]
                success = _run_conversion(cmd)

            elif format_type == 'docx-to-jats':
                # Two-step conversion: DOCX → Markdown → JATS XML
                output_filename = input_file.stem + '.xml'
                output_path = os.path.join(temp_dir, output_filename)

                # Step 1: Convert DOCX to Markdown
                temp_md_path = os.path.join(temp_dir, input_file.stem + '_temp.md')
                cmd1 = ['python', Config.CONVERTER_SCRIPT, input_path, '-o', temp_md_path]
                success = _run_conversion(cmd1)

                if success:
                    # Step 2: Convert Markdown to JATS XML
                    cmd2 = ['python', Config.CONVERTER_SCRIPT, temp_md_path, '-o', output_path]
                    success = _run_conversion(cmd2)

                    # Clean up temporary markdown file
                    if os.path.exists(temp_md_path):
                        os.remove(temp_md_path)
            else:
                return render_template('index.html', 
                                    form_action=Config.get_form_action(),
                                    app_version=get_version_display(),
                                    changelog_content=get_changelog_content(),
                                    message="Invalid format selected", error=True)

            if not success:
                return render_template('index.html', 
                                    form_action=Config.get_form_action(),
                                    app_version=get_version_display(),
                                    changelog_content=get_changelog_content(),
                                    message="Conversion failed", error=True)

            # Check if output file exists
            if not os.path.exists(output_path):
                return render_template('index.html', 
                                    form_action=Config.get_form_action(),
                                    app_version=get_version_display(),
                                    changelog_content=get_changelog_content(),
                                    message="Output file not created", error=True)

            # Return the converted file
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='text/plain'
            )

    except Exception as e:
        return render_template('index.html', 
                            form_action=Config.get_form_action(),
                            app_version=get_version_display(),
                            changelog_content=get_changelog_content(),
                            message=f"Error: {str(e)}", error=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)