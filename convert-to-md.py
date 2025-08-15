#!/usr/bin/env python3
"""
Simple DOCX/Markdown to Markdown/XML Converter

This script automatically detects input format and converts accordingly:
- DOCX → Markdown (with formatting fixes and table preservation)
- Markdown → JATS XML (with figure parsing)

Usage:
    python convert-to-md.py input.docx                    # DOCX → input.md
    python convert-to-md.py input.md                      # Markdown → input.xml
    python convert-to-md.py input.docx -o output.md       # DOCX → output.md
    python convert-to-md.py input.md -o output.xml        # Markdown → output.xml
"""

import argparse
import os
import sys
import subprocess
import re
import uuid
from pathlib import Path
from typing import Optional


def check_pandoc_installed() -> bool:
    """Check if pandoc is installed and available."""
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_pandoc_version() -> str:
    """Get pandoc version string."""
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.split('\n')[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Unknown"


def fix_split_bold_formatting(content: str) -> str:
    """
    Fix split bold formatting by merging adjacent bold segments that should be one sentence.
    
    This addresses the issue where pandoc splits a bold sentence into multiple bold segments
    due to mixed formatting (bold + italics + quotes).
    
    Args:
        content: The markdown content to process
        
    Returns:
        The content with fixed bold formatting
    """
    # Handle cases where we have ***text*** ***text*** (bold+italic adjacent)
    pattern1 = r'\*\*\*([^*]+?)\*\*\*\s*\*\*\*([^*]+?)\*\*\*'
    def merge_bold_italic(match):
        first_text = match.group(1).strip()
        second_text = match.group(2).strip()
        return f'***{first_text} {second_text}***'
    
    content = re.sub(pattern1, merge_bold_italic, content)
    
    # Handle cases where we have ***text*** **text** (bold+italic followed by bold)
    pattern2 = r'\*\*\*([^*]+?)\*\*\*\s*\*\*([^*]+?)\*\*'
    def merge_bold_italic_bold(match):
        first_text = match.group(1).strip()
        second_text = match.group(2).strip()
        return f'***{first_text} {second_text}***'
    
    content = re.sub(pattern2, merge_bold_italic_bold, content)
    
    # Handle cases where we have **text** ***text*** (bold followed by bold+italic)
    pattern3 = r'\*\*([^*]+?)\*\*\s*\*\*\*([^*]+?)\*\*\*'
    def merge_bold_bold_italic(match):
        first_text = match.group(1).strip()
        second_text = match.group(2).strip()
        return f'***{first_text} {second_text}***'
    
    content = re.sub(pattern3, merge_bold_bold_italic, content)
    
    # Handle cases where we have **text** **text** (bold adjacent)
    pattern4 = r'\*\*([^*]+?)\*\*\s*\*\*([^*]+?)\*\*'
    def merge_bold_bold(match):
        first_text = match.group(1).strip()
        second_text = match.group(2).strip()
        return f'**{first_text} {second_text}**'
    
    content = re.sub(pattern4, merge_bold_bold, content)
    
    # Handle cases where we have ***text*** ***text* (bold+italic followed by partial bold+italic)
    pattern5 = r'\*\*\*([^*]+?)\*\*\*\s*\*\*\*([^*]+?)\*'
    def merge_bold_italic_partial(match):
        first_text = match.group(1).strip()
        second_text = match.group(2).strip()
        return f'***{first_text} {second_text}***'
    
    content = re.sub(pattern5, merge_bold_italic_partial, content)
    
    return content


def consolidate_adjacent_italics(content: str) -> str:
    """
    Consolidate adjacent italicized words into single italic blocks.
    
    This addresses the issue where pandoc creates separate italic blocks for each word
    in a phrase that should be italicized as a whole.
    
    Args:
        content: The markdown content to process
        
    Returns:
        The content with consolidated italics
    """
    # Handle both underscore and asterisk italics
    # Pattern to match adjacent italicized words: _word_ _word_ _word_ or *word* *word* *word*
    
    # First, handle underscore italics: _word_ _word_ _word_
    underscore_pattern = r'_([^_]+)_\s+_([^_]+)_'
    
    def merge_underscore_italics(match):
        first_text = match.group(1).strip()
        second_text = match.group(2).strip()
        return f'_{first_text} {second_text}_'
    
    # Apply the consolidation repeatedly until no more changes
    # This handles cases with more than 2 adjacent italicized words
    previous_content = None
    while previous_content != content:
        previous_content = content
        content = re.sub(underscore_pattern, merge_underscore_italics, content)
    
    # Then, handle asterisk italics: *word* *word* *word*
    # But only if they're not part of bold formatting (**text** or ***text***)
    asterisk_pattern = r'(?<!\*)\*([^*]+?)\*(?!\*)\s+(?<!\*)\*([^*]+?)\*(?!\*)'
    
    def merge_asterisk_italics(match):
        first_text = match.group(1).strip()
        second_text = match.group(2).strip()
        return f'*{first_text} {second_text}*'
    
    # Apply the consolidation repeatedly until no more changes
    previous_content = None
    while previous_content != content:
        previous_content = content
        content = re.sub(asterisk_pattern, merge_asterisk_italics, content)
    
    return content


def remove_image_dimensions(content: str) -> str:
    """
    Remove image dimensions from markdown content.
    
    This removes pandoc-generated dimension attributes like {width="6.268055555555556in" height="4.076388888888889in"}
    from image references in markdown.
    
    Args:
        content: The markdown content to process
        
    Returns:
        The content with image dimensions removed
    """
    # Pattern to match image dimensions: {width="..." height="..."} or {width="..."} or {height="..."}
    # This handles various combinations of width and height attributes
    dimension_pattern = r'\s*\{[^}]*width\s*=\s*"[^"]*"[^}]*\}\s*'
    dimension_pattern2 = r'\s*\{[^}]*height\s*=\s*"[^"]*"[^}]*\}\s*'
    
    # Remove width-based dimensions
    content = re.sub(dimension_pattern, '', content)
    # Remove height-based dimensions (in case they appear without width)
    content = re.sub(dimension_pattern2, '', content)
    
    return content


def parse_figures_for_jats(content: str) -> str:
    """
    Parse figure patterns from JATS XML content and convert them to proper JATS XML figure elements.
    
    This function looks for patterns in the JATS XML where pandoc has converted:
    - Figure labels as bold text
    - Images as inline-graphic elements
    - Captions as text following the image
    
    And converts them to proper JATS XML figure elements.
    
    Args:
        content: The JATS XML content to process
        
    Returns:
        The content with figures converted to proper JATS XML format
    """
    # Pattern to match figure blocks in JATS XML:
    # 1. A paragraph with <bold>Figure X</bold> (the label)
    # 2. A paragraph with inline-graphic element and caption text
    figure_pattern = r'(<p[^>]*>\s*<bold[^>]*>Figure\s+\d+</bold>\s*</p>)\s*(<p[^>]*>\s*<inline-graphic[^>]*>.*?</inline-graphic>([^<]*)</p>)'
    
    def replace_figure(match):
        label_para = match.group(1)
        image_para = match.group(2)
        caption_text = match.group(3).strip()
        
        # Extract figure number from the label
        label_match = re.search(r'<bold[^>]*>(Figure\s+\d+)</bold>', label_para)
        label = label_match.group(1) if label_match else "Figure"
        
        # Extract image information from inline-graphic element
        href_match = re.search(r'xlink:href="([^"]+)"', image_para)
        mime_subtype_match = re.search(r'mime-subtype="([^"]+)"', image_para)
        
        image_filename = href_match.group(1) if href_match else "image.png"
        mime_subtype = mime_subtype_match.group(1) if mime_subtype_match else "png"
        
        # Generate unique IDs
        fig_id = f"fig-{uuid.uuid4().hex[:24]}"
        object_id = f"object-id-{uuid.uuid4().hex[:24]}"
        caption_id = f"caption-{uuid.uuid4().hex[:24]}"
        title_id = f"title-{uuid.uuid4().hex[:24]}"
        p_id = f"p-{uuid.uuid4().hex[:24]}"
        graphic_id = f"graphic-{uuid.uuid4().hex[:24]}"
        
        # Build JATS XML figure element
        jats_figure = f'''<fig id="{fig_id}">
        <object-id id="{object_id}">{fig_id}</object-id>
        <label>{label}</label>
        <caption id="{caption_id}">
          <title id="{title_id}" />
          <p id="{p_id}">{caption_text}</p>
        </caption>
        <graphic id="{graphic_id}" mime-subtype="{mime_subtype}" mimetype="image" xlink:href="{image_filename}" />
      </fig>'''
        
        return jats_figure
    
    # Apply the figure conversion
    content = re.sub(figure_pattern, replace_figure, content, flags=re.MULTILINE | re.DOTALL)
    
    return content


def wrap_body_content_in_sections(content: str) -> str:
    """
    Ensure all content within the <body> tag is wrapped in <sec> tags.
    
    This function looks for content directly inside the <body> tag that is not already
    wrapped in <sec> tags and wraps it appropriately. Each section gets a unique ID.
    
    Args:
        content: The JATS XML content to process
        
    Returns:
        The content with body content properly wrapped in sec tags with unique IDs
    """
    # Pattern to match the <body> tag and its content
    body_pattern = r'(<body[^>]*>)(.*?)(</body>)'
    
    def wrap_body_content(match):
        body_open = match.group(1)
        body_content = match.group(2)
        body_close = match.group(3)
        
        # If body is empty or only contains whitespace, return as is
        if not body_content.strip():
            return f"{body_open}{body_content}{body_close}"
        
        # Split content into lines to process
        lines = body_content.split('\n')
        result_lines = []
        current_section = []
        in_section = False
        section_counter = 0
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                if current_section:
                    current_section.append(line)
                continue
            
            # Check if this line starts a new section
            if line_stripped.startswith('<sec'):
                # If we have content in current_section, wrap it in a section
                if current_section and not in_section:
                    section_id = f"heading-{uuid.uuid4().hex}"
                    result_lines.append(f'  <sec id="{section_id}">')
                    result_lines.extend(current_section)
                    result_lines.append('  </sec>')
                    current_section = []
                
                # Start new section - check if it already has an ID
                if 'id=' in line_stripped:
                    # Section already has an ID, keep it as is
                    result_lines.append(line)
                else:
                    # Add unique ID to existing section
                    section_id = f"heading-{uuid.uuid4().hex}"
                    # Replace <sec with <sec id="..."
                    new_line = line_stripped.replace('<sec', f'<sec id="{section_id}"')
                    result_lines.append(new_line)
                in_section = True
                current_section = []
                
            elif line_stripped.startswith('</sec>'):
                # End current section
                result_lines.append(line)
                in_section = False
                current_section = []
                
            else:
                # Regular content line
                if in_section:
                    # We're already in a section, just add the line
                    result_lines.append(line)
                else:
                    # We're not in a section, collect content
                    current_section.append(line)
        
        # Handle any remaining content that wasn't wrapped
        if current_section and not in_section:
            section_id = f"heading-{uuid.uuid4().hex}"
            result_lines.append(f'  <sec id="{section_id}">')
            result_lines.extend(current_section)
            result_lines.append('  </sec>')
        
        # Join the processed content
        processed_content = '\n'.join(result_lines)
        
        return f"{body_open}\n{processed_content}\n{body_close}"
    
    # Apply the section wrapping
    content = re.sub(body_pattern, wrap_body_content, content, flags=re.MULTILINE | re.DOTALL)
    
    return content





def convert_docx_to_markdown(input_file: str, output_file: str) -> bool:
    """
    Convert a DOCX file to Markdown using pandoc.
    
    Args:
        input_file: Path to input DOCX file
        output_file: Path to output Markdown file
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    # Build pandoc command
    cmd = ['pandoc', input_file, '-o', output_file]
    
    # Set output format to markdown with multiline tables (automatic table preservation)
    cmd.extend(['--to', 'markdown+multiline_tables'])
    
    # Add options for better academic document handling
    cmd.extend([
        '--wrap=none',  # Don't wrap lines
        '--markdown-headings=atx',  # Use # style headings
        '--reference-location=document',  # Put references at end
    ])
    
    try:
        print(f"Converting '{input_file}' to '{output_file}'...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Post-process the output
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert single asterisk italics to underscore italics
            # This regex matches *text* but not **text** (bold) or ***text*** (bold italic)
            content = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'_\1_', content)
            
            # Fix split bold formatting - merge adjacent bold segments that should be one sentence
            content = fix_split_bold_formatting(content)
            
            # Consolidate adjacent italicized words into single italic blocks
            content = consolidate_adjacent_italics(content)

            # Remove image dimensions
            content = remove_image_dimensions(content)
            
            # Write the processed content back
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✓ Successfully converted '{input_file}' to '{output_file}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error converting '{input_file}': {e}")
        if e.stderr:
            print(f"Pandoc error: {e.stderr}")
        return False


def convert_markdown_to_xml(input_file: str, output_file: str) -> bool:
    """
    Convert a Markdown file to JATS XML using pandoc.
    
    Args:
        input_file: Path to input Markdown file
        output_file: Path to output JATS XML file
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    # Build pandoc command
    cmd = ['pandoc', input_file, '-o', output_file]
    
    # Set output format to JATS archiving
    cmd.extend(['--to', 'jats_archiving'])
    
    # Add standalone option
    cmd.append('--standalone')
    
    # Add options for better academic document handling
    cmd.extend([
        '--wrap=none',  # Don't wrap lines
        '--reference-location=document',  # Put references at end
    ])
    
    try:
        print(f"Converting '{input_file}' to '{output_file}'...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Post-process the JATS XML to handle figure parsing
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse and convert figure patterns to proper JATS XML
            content = parse_figures_for_jats(content)
            
            # Wrap body content in sections
            content = wrap_body_content_in_sections(content)
            
            # Write the processed content back
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✓ Successfully converted '{input_file}' to '{output_file}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error converting '{input_file}' to JATS XML: {e}")
        if e.stderr:
            print(f"Pandoc error: {e.stderr}")
        return False


def main():
    """Main function to handle command line arguments and execute conversion."""
    parser = argparse.ArgumentParser(
        description="Convert DOCX to Markdown or Markdown to JATS XML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.docx                    # DOCX → input.md
  %(prog)s input.md                      # Markdown → input.xml
  %(prog)s input.docx -o output.md       # DOCX → output.md
  %(prog)s input.md -o output.xml        # Markdown → output.xml
        """
    )
    
    parser.add_argument('input', help='Input file (DOCX or Markdown)')
    parser.add_argument('-o', '--output', help='Output file (optional)')
    
    args = parser.parse_args()
    
    # Check if pandoc is installed
    if not check_pandoc_installed():
        print("Error: pandoc is not installed or not found in PATH.")
        print("Please install pandoc from https://pandoc.org/installing.html")
        sys.exit(1)
    
    print(f"Using {get_pandoc_version()}")
    
    # Determine input type and output file
    input_path = Path(args.input)
    input_ext = input_path.suffix.lower()
    
    if input_ext == '.docx':
        # DOCX → Markdown
        if args.output:
            output_file = args.output
        else:
            output_file = input_path.with_suffix('.md')
        
        success = convert_docx_to_markdown(args.input, str(output_file))
        
    elif input_ext == '.md':
        # Markdown → XML
        if args.output:
            output_file = args.output
        else:
            output_file = input_path.with_suffix('.xml')
        
        success = convert_markdown_to_xml(args.input, str(output_file))
        
    else:
        print(f"Error: Unsupported input format '{input_ext}'. Supported formats: .docx, .md")
        sys.exit(1)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
