# Social Quote Generator Command Setup

**Date:** 2025-10-10  
**Task:** Create command for social-quote-generator

## Changes Made

### 1. Created Proper Package Structure

Reorganized the source code into a proper Python package:
- Created `src/bge_social_quote_generator/` package directory
- Moved all modules into the package (config, orchestrator, extractors, generators, publishers, utils)
- Created new `cli.py` as the command-line entry point

### 2. Fixed setup.py Entry Point

Updated `social-quote-generator/setup.py` to properly define the console script entry point:

```python
entry_points={
    "console_scripts": [
        "bge-quote-gen=bge_social_quote_generator.cli:main",
    ],
}
```

Also added `include_package_data=True` and `package_data` to ensure templates and config files are included.

### 3. Smart Config Path Resolution

Implemented intelligent config file discovery in `cli.py` that searches multiple locations:
1. Relative to current working directory
2. In `social-quote-generator/config/config.yaml` (project structure)
3. Relative to package installation directory
4. Default config location

This means you can run the command from anywhere without worrying about the config path!

### 4. Created MANIFEST.in

Added `MANIFEST.in` to ensure non-Python files (config, templates) are included in the package distribution.

### 5. Updated Documentation

Updated `QUICK_START.md` to use the new `bge-quote-gen` command instead of `python -m` invocations.

## Installation

From the project root directory:

```bash
# Install in development mode
pip install -e social-quote-generator/

# Or install normally
pip install social-quote-generator/
```

## Usage

After installation, you can use the `bge-quote-gen` command from anywhere:

```bash
# Generate images for a single episode (dry-run)
bge-quote-gen --episode 1 --dry-run

# Generate for specific platform
bge-quote-gen --episode 1 --platform instagram --dry-run

# Generate for multiple episodes
bge-quote-gen --episodes 1,5,10 --platform twitter --dry-run

# Use specific quote source
bge-quote-gen --episode 1 --quote-source claude --dry-run

# Publish to social media (requires API credentials)
bge-quote-gen --episode 1 --publish

# Show help
bge-quote-gen --help

# Show version
bge-quote-gen --version
```

## Running from Any Directory

The command works from anywhere after installation - no need to be in the project directory:

```bash
cd /tmp
bge-quote-gen --episode 1 --platform instagram --dry-run
```

The tool automatically finds the config file by searching multiple locations.

## Key Features

- **Episode Selection:** Single (`--episode`), multiple (`--episodes`), or all (`--all`)
- **Platform Targeting:** Instagram, Twitter, Facebook, LinkedIn
- **Quote Sources:** Claude, OpenAI, DeepSeek, Llama, or random
- **Dry Run Mode:** Test without publishing (`--dry-run`)
- **Publishing:** Post directly to social media (`--publish`)
- **Verbose Logging:** Debug mode (`--verbose`)
- **Custom Config:** Override default config (`--config path/to/config.yaml`)

## Configuration

Default config: `social-quote-generator/config/config.yaml`

Key settings:
- Episode and text directories
- Platform dimensions and templates
- Quote source preferences
- Social media API credentials
- Branding (logo, colors, fonts)

## Output

Generated images saved to: `social-quote-generator/output/images/`

Naming: `bge_{episode}_{platform}_{timestamp}.png`

## Next Steps

1. Install the package: `pip install -e social-quote-generator/`
2. Test with dry-run: `bge-quote-gen --episode 1 --dry-run`
3. Check output in `social-quote-generator/output/images/`
4. Configure API credentials in `.env` for publishing
5. Publish: `bge-quote-gen --episode 1 --publish`
