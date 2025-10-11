#!/usr/bin/env python3
"""
Frontmatter Validator for La Brigata dei Geek Estinti
Validates episode markdown files for required fields and correct format.
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


class FrontmatterValidator:
    """Validates episode frontmatter structure and content."""
    
    REQUIRED_FIELDS = {
        'number': str,
        'layout': str,
        'title': str,
        'titolo': str,
        'description': str,
        'duration': int,
        'youtube': str,
        'tags': list,
        'date': str,
        'summary': list,
        'guests': list,
        'host': str,
        'quote_claude': str,
        'quote_openai': str,
        'quote_deepseek': str,
        'quote_llama': str,
        'quote_deepseek_reasoning': str,
        'claude_article': str,
    }
    
    OPTIONAL_FIELDS = {
        'links': str,
    }
    
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    YOUTUBE_PATTERN = re.compile(r'^[A-Za-z0-9_-]{11}$')
    
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors = []
        self.warnings = []
    
    def validate_file(self, filepath: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a single markdown file."""
        self.errors = []
        self.warnings = []
        
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"Failed to read file: {e}")
            return False, self.errors, self.warnings
        
        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)
        if frontmatter is None:
            self.errors.append("No valid frontmatter found")
            return False, self.errors, self.warnings
        
        # Validate structure
        self._validate_required_fields(frontmatter)
        self._validate_field_types(frontmatter)
        self._validate_field_values(frontmatter)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None
        
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return None
    
    def _validate_required_fields(self, frontmatter: Dict[str, Any]):
        """Check all required fields are present."""
        for field in self.REQUIRED_FIELDS:
            if field not in frontmatter:
                self.errors.append(f"Missing required field: '{field}'")
            elif frontmatter[field] is None or frontmatter[field] == '':
                self.errors.append(f"Required field '{field}' is empty")
    
    def _validate_field_types(self, frontmatter: Dict[str, Any]):
        """Validate field types match expected types."""
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in frontmatter:
                continue
            
            value = frontmatter[field]
            if value is None:
                continue
            
            if not isinstance(value, expected_type):
                self.errors.append(
                    f"Field '{field}' has wrong type: expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
    
    def _validate_field_values(self, frontmatter: Dict[str, Any]):
        """Validate specific field value formats."""
        # Validate layout
        if frontmatter.get('layout') != 'episode':
            self.errors.append(f"Field 'layout' must be 'episode', got '{frontmatter.get('layout')}'")
        
        # Validate date format
        date_value = frontmatter.get('date')
        if date_value and not self.DATE_PATTERN.match(str(date_value)):
            self.errors.append(f"Field 'date' must be in YYYY-MM-DD format, got '{date_value}'")
        
        # Validate YouTube ID format
        youtube_id = frontmatter.get('youtube')
        if youtube_id and not self.YOUTUBE_PATTERN.match(str(youtube_id)):
            self.warnings.append(f"Field 'youtube' doesn't match standard format: '{youtube_id}'")
        
        # Validate duration is positive
        duration = frontmatter.get('duration')
        if duration is not None and duration <= 0:
            self.errors.append(f"Field 'duration' must be positive, got {duration}")
        
        # Validate arrays are not empty
        for field in ['tags', 'summary', 'guests']:
            value = frontmatter.get(field)
            if value is not None and isinstance(value, list) and len(value) == 0:
                self.warnings.append(f"Field '{field}' is an empty array")
        
        # Validate number matches filename
        number = frontmatter.get('number')
        if number and not str(number).isdigit():
            self.warnings.append(f"Field 'number' should be numeric, got '{number}'")


def validate_directory(directory: Path, strict: bool = False) -> Tuple[int, int]:
    """Validate all markdown files in a directory."""
    validator = FrontmatterValidator(strict=strict)
    passed = 0
    failed = 0
    
    md_files = sorted(directory.glob('*.md'))
    
    if not md_files:
        print(f"No markdown files found in {directory}")
        return 0, 0
    
    print(f"Validating {len(md_files)} files in {directory}\n")
    
    for filepath in md_files:
        is_valid, errors, warnings = validator.validate_file(filepath)
        
        if is_valid:
            passed += 1
            print(f"✓ {filepath.name}")
        else:
            failed += 1
            print(f"✗ {filepath.name}")
            for error in errors:
                print(f"  ERROR: {error}")
        
        if warnings:
            for warning in warnings:
                print(f"  WARNING: {warning}")
    
    return passed, failed


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate frontmatter in episode markdown files'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='_episodes',
        help='Path to episode file or directory (default: _episodes)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation mode'
    )
    
    args = parser.parse_args()
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        sys.exit(1)
    
    if path.is_file():
        validator = FrontmatterValidator(strict=args.strict)
        is_valid, errors, warnings = validator.validate_file(path)
        
        print(f"Validating {path.name}\n")
        
        if is_valid:
            print("✓ Valid")
        else:
            print("✗ Invalid")
            for error in errors:
                print(f"  ERROR: {error}")
        
        if warnings:
            for warning in warnings:
                print(f"  WARNING: {warning}")
        
        sys.exit(0 if is_valid else 1)
    
    elif path.is_dir():
        passed, failed = validate_directory(path, strict=args.strict)
        
        print(f"\n{'='*50}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'='*50}")
        
        sys.exit(0 if failed == 0 else 1)
    
    else:
        print(f"Error: '{path}' is neither a file nor a directory")
        sys.exit(1)


if __name__ == '__main__':
    main()
