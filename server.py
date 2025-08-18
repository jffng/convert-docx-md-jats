import os
import tempfile
import subprocess
from pathlib import Path
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

def _run_conversion(cmd):
    """Helper function to run conversion commands."""
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

# HTML template for the upload form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DOCX to JATS Converter</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="file"], select { width: 100%; padding: 8px; margin-bottom: 10px; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #005a87; }
        .result { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; }
        .error { background: #ffebee; color: #c62828; }
        .success { background: #e8f5e8; color: #2e7d32; }
    </style>
</head>
<body>
    <h1>DOCX to JATS XML Converter</h1>
    <p>Upload a DOCX file to convert to Markdown, or a Markdown file to convert to JATS XML.</p>
    
    <form action="/convert" method="post" enctype="multipart/form-data">
        <div class="form-group">
            <label for="document">Select Document:</label>
            <input type="file" id="document" name="document" accept=".docx,.md" required onchange="updateConversionOptions()">
        </div>
        
        <div class="form-group" id="conversion-options" style="display: none;">
            <label for="convert-to-jats">
                <input type="checkbox" id="convert-to-jats" name="convert-to-jats">
                Convert to JATS XML (for DOCX files only)
            </label>
            <p id="conversion-info" style="font-size: 0.9em; color: #666; margin-top: 5px;"></p>
        </div>
        
        <button type="submit">Convert Document</button>
    </form>
    
    <script>
    function updateConversionOptions() {
        const fileInput = document.getElementById('document');
        const conversionOptions = document.getElementById('conversion-options');
        const convertToJats = document.getElementById('convert-to-jats');
        const conversionInfo = document.getElementById('conversion-info');
        
        if (fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name.toLowerCase();
            
            if (fileName.endsWith('.docx')) {
                conversionOptions.style.display = 'block';
                convertToJats.disabled = false;
                conversionInfo.textContent = 'DOCX will be converted to Markdown. Check the box to also convert to JATS XML.';
            } else if (fileName.endsWith('.md')) {
                conversionOptions.style.display = 'block';
                convertToJats.disabled = true;
                convertToJats.checked = true;
                conversionInfo.textContent = 'Markdown will be converted to JATS XML.';
            } else {
                conversionOptions.style.display = 'none';
            }
        } else {
            conversionOptions.style.display = 'none';
        }
    }
    </script>
    
    {% if message %}
    <div class="result {% if error %}error{% else %}success{% endif %}">
        {{ message }}
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/convert', methods=['POST'])
def convert():
    """Handle document conversion."""
    try:
        # Check if file was uploaded
        if 'document' not in request.files:
            return render_template_string(HTML_TEMPLATE, 
                                        message="No file uploaded", error=True)
        
        file = request.files['document']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, 
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
            return render_template_string(HTML_TEMPLATE, 
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
                cmd = ['python', 'convert-to-md.py', input_path, '-o', output_path]
                success = _run_conversion(cmd)
                
            elif format_type == 'jats':
                output_filename = input_file.stem + '.xml'
                output_path = os.path.join(temp_dir, output_filename)
                # Use convert-to-md.py for Markdown to JATS XML
                cmd = ['python', 'convert-to-md.py', input_path, '-o', output_path]
                success = _run_conversion(cmd)
                
            elif format_type == 'docx-to-jats':
                # Two-step conversion: DOCX → Markdown → JATS XML
                output_filename = input_file.stem + '.xml'
                output_path = os.path.join(temp_dir, output_filename)
                
                # Step 1: Convert DOCX to Markdown
                temp_md_path = os.path.join(temp_dir, input_file.stem + '_temp.md')
                cmd1 = ['python', 'convert-to-md.py', input_path, '-o', temp_md_path]
                success = _run_conversion(cmd1)
                
                if success:
                    # Step 2: Convert Markdown to JATS XML
                    cmd2 = ['python', 'convert-to-md.py', temp_md_path, '-o', output_path]
                    success = _run_conversion(cmd2)
                    
                    # Clean up temporary markdown file
                    if os.path.exists(temp_md_path):
                        os.remove(temp_md_path)
            else:
                return render_template_string(HTML_TEMPLATE, 
                                            message="Invalid format selected", error=True)
            
            if not success:
                return render_template_string(HTML_TEMPLATE, 
                                            message="Conversion failed", error=True)
            
            # Check if output file exists
            if not os.path.exists(output_path):
                return render_template_string(HTML_TEMPLATE, 
                                            message="Output file not created", error=True)
            
            # Return the converted file
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='text/plain'
            )
    
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, 
                                    message=f"Error: {str(e)}", error=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)