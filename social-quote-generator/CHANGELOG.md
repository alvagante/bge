# Changelog

All notable changes to the BGE Social Quote Generator project.

## [1.0.0] - 2025-10-10

### Added
- Created `bge-quote-gen` command-line tool
- Smart config file discovery that searches multiple locations
- Proper Python package structure (`bge_social_quote_generator`)
- MANIFEST.in for including non-Python files in distribution
- COMMAND_REFERENCE.md for quick command reference

### Changed
- Reorganized source code into proper package structure
- Updated all documentation to use `bge-quote-gen` command
- Improved config path resolution - works from any directory
- Entry point now uses `bge_social_quote_generator.cli:main`

### Fixed
- Package import errors with relative imports
- Config file path issues when running from different directories
- Installation issues with setuptools

### Documentation
- Updated QUICK_START.md with new command syntax
- Added COMMAND_REFERENCE.md for quick reference
- Updated installation instructions
- Added examples for running from any directory

## [0.1.0] - Initial Release

### Added
- Initial implementation of quote image generator
- Support for Instagram, Twitter, Facebook, LinkedIn
- Multiple AI quote sources (Claude, OpenAI, DeepSeek, Llama)
- Dry-run and publish modes
- Template-based image generation
- Social media publishing capabilities
