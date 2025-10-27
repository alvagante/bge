# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BGE Social Quote Generator is a Python tool that automates the creation and publishing of quote images from podcast episodes to social media platforms. It extracts quotes from episode markdown files, generates branded images for different social platforms, and publishes them using various social media APIs.

## Installation and Setup

```bash
# Install the package in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
bge-quote-gen --version
```

## Common Commands

### Development and Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test files
pytest tests/test_extractors.py
pytest scripts/test_orchestrator.py

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run integration tests
./scripts/test_cli_integration.py
./scripts/test_utils_integration.py
```

### Using the CLI Tool

```bash
# Generate images for a single episode (dry-run mode)
bge-quote-gen --episode 1 --dry-run

# Generate for specific platform
bge-quote-gen --episode 1 --platform instagram --dry-run

# Generate for specific quote source
bge-quote-gen --episode 1 --quote-source claude --dry-run

# Process multiple episodes
bge-quote-gen --episodes 1,5,10 --dry-run

# Test with verbose logging
bge-quote-gen --episode 1 --dry-run --verbose

# Run test scripts
./test_all_quotes.sh 13
./test_landscape_layout.sh
```

### Queue-Based Publishing

```bash
# Add episode to publishing queue
bge-quote-gen --episode 1 --queue

# List pending queue items
bge-quote-gen --queue-list

# Publish from queue (for automated jobs)
bge-quote-gen --queue-publish
```

## Architecture Overview

### Core Components

1. **CLI Interface** (`cli.py`) - Command-line entry point with argument parsing
2. **Pipeline Orchestrator** (`orchestrator.py`) - Coordinates the entire workflow
3. **Quote Extractor** (`extractors/`) - Extracts quotes from episode files and text sources
4. **Image Generator** (`generators/`) - Creates branded images using Pillow/PIL
5. **Publishers** (`publishers/`) - Publishes to social media platforms (Twitter, Instagram, Facebook, LinkedIn)
6. **Queue System** (`queue/`) - Manages scheduled publishing with file-based queue
7. **Configuration** (`config.py`) - Handles YAML config and environment variables
8. **Utilities** (`utils/`) - Validation, logging, error handling, and helpers

### Data Flow

1. Episode metadata is loaded from `_episodes/*.md` files (YAML frontmatter at repository root)
2. Quotes are extracted from `assets/texts/` directory (4 AI sources: Claude, OpenAI, DeepSeek, Llama)
3. Images are generated for each platform using templates from `social-quote-generator/templates/`
4. Images are saved to `social-quote-generator/output/images/` with naming pattern: `bge_{episode}_{source}_{platform}_{timestamp}.png`
5. Optionally published to social media or queued for later publishing

### Platform Support

- **Instagram**: 1080x1080 (square format)
- **Twitter**: 1200x675 (16:9 landscape)
- **Facebook**: 1200x630 (1.91:1 landscape)
- **LinkedIn**: 1200x627 (1.91:1 landscape)

## Key Configuration Files

- `config/config.yaml` - Main configuration (platforms, branding, templates)
- `.env` - API credentials and secrets (not committed to git)
- `setup.py` - Package definition and dependencies
- `requirements.txt` - Production dependencies

## Important File Paths

The tool expects this directory structure (paths relative to repository root):
- `_episodes/` - Episode markdown files with YAML frontmatter (at repository root)
- `assets/texts/` - Quote text files organized by AI source (at repository root)
- `assets/covers/` - Episode cover images (at repository root)
- `assets/fonts/` - Custom fonts for text rendering (at repository root)
- `social-quote-generator/templates/` - Image templates
- `social-quote-generator/output/images/` - Generated images
- `social-quote-generator/output/logs/` - Application logs

## Development Guidelines

### Running Tests
Always run the test suite before making changes:
```bash
pytest  # Run all tests
pytest -v  # Verbose output
pytest --cov=src  # With coverage
```

### Code Quality
The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing

### Common Tasks

**Add a new social media platform:**
1. Create new publisher class in `publishers/`
2. Inherit from `BasePublisher`
3. Update platform configurations in `config.yaml`
4. Add platform dimensions to image generator

**Add new quote source:**
1. Update quote extractor to handle new source format
2. Add source configuration options
3. Update CLI arguments and validation

**Modify image generation:**
1. Update `ImageGenerator` class in `generators/image_generator.py`
2. Modify templates in `social-quote-generator/templates/` directory
3. Test with `./test_landscape_layout.sh`

## Troubleshooting

### Common Issues

**Import errors after installation:**
```bash
pip install -e .  # Reinstall in development mode
```

**Missing episodes or quotes:**
- Verify `_episodes/` directory (at repository root) contains episode markdown files
- Check `assets/texts/` (at repository root) for quote text files
- Run with `--verbose` for detailed logging

**Font rendering issues:**
- Install fonts in `assets/fonts/` directory (at repository root)
- Update `config.yaml` with correct font filename
- The tool falls back to system fonts if custom fonts are missing

**API authentication failures:**
- Verify credentials in `.env` file
- Check API key permissions and expiry
- Use `--dry-run` to test without publishing

### Debug Mode
Enable verbose logging for troubleshooting:
```bash
bge-quote-gen --episode 1 --dry-run --verbose
```

## Security Notes

- Never commit `.env` file or API credentials
- Use environment variables for all secrets
- API credentials are loaded via `${VARIABLE_NAME}` syntax in config files
- Input validation prevents path traversal and injection attacks

## Queue System

The tool includes a sophisticated queue-based publishing system for automation:
- File-based queue with JSON storage
- Scheduled publishing with cron integration
- Automatic retry logic with exponential backoff
- Conflict resolution and duplicate prevention

See `QUEUE_GUIDE.md` for detailed queue system documentation.