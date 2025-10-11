# Frontmatter Validator Script

**Date:** 2025-01-11  
**Task:** Create validation script for episode frontmatter format

## Summary

Created a comprehensive Python validation script (`bin/validate_frontmatter.py`) that validates the YAML frontmatter structure in episode markdown files for La Brigata dei Geek Estinti podcast.

## What was created

1. **bin/validate_frontmatter.py** - Main validation script
   - Validates all required fields (18 fields)
   - Checks field types (string, int, list)
   - Validates specific formats (date, YouTube ID)
   - Provides detailed error and warning messages
   - Supports single file or directory validation
   - Command-line interface with options

2. **bin/README_VALIDATOR.md** - Documentation
   - Usage instructions
   - Field requirements
   - Validation rules
   - Examples

## Features

- Validates 18 required frontmatter fields
- Type checking (string, integer, list)
- Format validation (YYYY-MM-DD dates, YouTube IDs)
- YAML syntax validation
- Batch validation for entire directories
- Clear error and warning messages
- Exit codes for CI/CD integration

## Test Results

Tested on episode files and found several YAML syntax errors in episodes 19, 20, 23, 25 (quote fields with unescaped apostrophes).

## Usage

```bash
# Single file
python3 bin/validate_frontmatter.py _episodes/1.md

# All episodes
python3 bin/validate_frontmatter.py _episodes

# Strict mode
python3 bin/validate_frontmatter.py _episodes --strict
```

## Dependencies

- Python 3.6+
- PyYAML library
