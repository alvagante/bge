#!/usr/bin/env python3
"""
Fix encoding issues in episode markdown files.
Converts hex escape sequences to proper UTF-8 characters and fixes double apostrophes.
"""

import os
import re
from pathlib import Path

# Mapping of hex escape sequences to proper characters
HEX_MAPPINGS = {
    r'\xE8': 'è',
    r'\xE9': 'é',
    r'\xE0': 'à',
    r'\xF2': 'ò',
    r'\xF9': 'ù',
    r'\xEC': 'ì',
    r'\xF3': 'ó',
    r'\xFA': 'ú',
    r'\xC8': 'È',
    r'\xC9': 'É',
    r'\xC0': 'À',
    r'\xD2': 'Ò',
    r'\xD9': 'Ù',
    r'\xCC': 'Ì',
}

def fix_file(filepath):
    """Fix encoding issues in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace hex escape sequences
    for hex_seq, char in HEX_MAPPINGS.items():
        content = content.replace(hex_seq, char)
    
    # Fix double apostrophes in quote fields (but not in YAML strings that need escaping)
    # This regex targets double apostrophes within quote values
    content = re.sub(r"(quote_[a-z_]+:\s*['\"].*?)''(.*?['\"])", r"\1'\2", content)
    
    # Check if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Process all episode files."""
    episodes_dir = Path('_episodes')
    fixed_count = 0
    
    for filepath in sorted(episodes_dir.glob('*.md')):
        if fix_file(filepath):
            print(f"Fixed: {filepath.name}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
