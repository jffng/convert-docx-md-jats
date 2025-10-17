#!/usr/bin/env python3
"""
Version management utility for the DOCX to JATS XML Converter.

This script helps manage semantic versioning for the application.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

def get_current_version():
    """Get the current version from version.py"""
    try:
        from version import get_version
        return get_version()
    except ImportError:
        return None

def update_version(new_version):
    """Update the version in version.py"""
    version_file = Path("version.py")
    
    if not version_file.exists():
        print("Error: version.py not found")
        return False
    
    # Read current content
    content = version_file.read_text()
    
    # Update version string
    content = re.sub(
        r'__version__ = "[^"]*"',
        f'__version__ = "{new_version}"',
        content
    )
    
    # Update version info tuple
    major, minor, patch = new_version.split('.')
    content = re.sub(
        r'__version_info__ = \([^)]*\)',
        f'__version_info__ = ({major}, {minor}, {patch})',
        content
    )
    
    # Write updated content
    version_file.write_text(content)
    print(f"Updated version to {new_version}")
    return True

def update_changelog(new_version, change_type="patch"):
    """Add a new version entry to CHANGELOG.md"""
    changelog_file = Path("CHANGELOG.md")
    
    if not changelog_file.exists():
        print("Error: CHANGELOG.md not found")
        return False
    
    content = changelog_file.read_text()
    
    # Generate date
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Create new version entry
    if change_type == "major":
        description = "Major version update with breaking changes"
        section_title = "### Changed"
    elif change_type == "minor":
        description = "Minor version update with new features"
        section_title = "### Added"
    else:
        description = "Patch version update with bug fixes"
        section_title = "### Fixed"
    
    new_entry = f"""## [{new_version}] - {date}

{section_title}
- {description}

"""
    
    # Insert after the first line (after the title)
    lines = content.split('\n')
    insert_index = 1
    for i, line in enumerate(lines):
        if line.startswith('## ['):
            insert_index = i
            break
    
    lines.insert(insert_index, new_entry)
    
    # Write updated content
    changelog_file.write_text('\n'.join(lines))
    print(f"Updated CHANGELOG.md with version {new_version}")
    return True

def bump_version(current_version, bump_type):
    """Bump version according to semantic versioning"""
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"Error: Invalid bump type '{bump_type}'. Use 'major', 'minor', or 'patch'")
        return None
    
    return f"{major}.{minor}.{patch}"

def main():
    """Main function for version management"""
    if len(sys.argv) < 2:
        print("Usage: python version_manager.py <command> [args]")
        print("Commands:")
        print("  current                    - Show current version")
        print("  bump <type>                - Bump version (major|minor|patch)")
        print("  set <version>              - Set specific version")
        print("  update <version> <type>    - Update version and changelog")
        return
    
    command = sys.argv[1]
    
    if command == "current":
        version = get_current_version()
        if version:
            print(f"Current version: {version}")
        else:
            print("Could not determine current version")
    
    elif command == "bump":
        if len(sys.argv) < 3:
            print("Usage: python version_manager.py bump <major|minor|patch>")
            return
        
        bump_type = sys.argv[2]
        current_version = get_current_version()
        
        if not current_version:
            print("Could not determine current version")
            return
        
        new_version = bump_version(current_version, bump_type)
        if new_version:
            if update_version(new_version) and update_changelog(new_version, bump_type):
                print(f"Version bumped from {current_version} to {new_version}")
                print("Changelog updated automatically")
    
    elif command == "set":
        if len(sys.argv) < 3:
            print("Usage: python version_manager.py set <version>")
            return
        
        new_version = sys.argv[2]
        if update_version(new_version):
            print(f"Version set to {new_version}")
    
    elif command == "update":
        if len(sys.argv) < 4:
            print("Usage: python version_manager.py update <version> <major|minor|patch>")
            return
        
        new_version = sys.argv[2]
        change_type = sys.argv[3]
        
        if update_version(new_version) and update_changelog(new_version, change_type):
            print(f"Updated version to {new_version} and changelog")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
