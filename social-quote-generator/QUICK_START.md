# BGE Social Quote Generator - Quick Start Guide

## Installation

```bash
# Navigate to the project root directory
cd /path/to/bge.github.io

# Install the package in development mode
pip install -e social-quote-generator/

# Install additional dependencies if needed
pip install facebook-sdk
```

## Basic Usage

### Generate Images for a Single Episode

```bash
# Generate images for all platforms (dry-run mode)
python -m social-quote-generator.src.main --episode 1 --dry-run

# Generate image for specific platform
python -m social-quote-generator.src.main --episode 1 --platform instagram --dry-run
```

### Generate Images for Multiple Episodes

```bash
# Process multiple episodes
python -m social-quote-generator.src.main --episodes 1,5,10 --platform twitter --dry-run

# Process all episodes (use with caution!)
python -m social-quote-generator.src.main --all --platform instagram --dry-run
```

### Choose Quote Source

```bash
# Use specific AI quote source
python -m social-quote-generator.src.main --episode 1 --quote-source claude --dry-run
python -m social-quote-generator.src.main --episode 1 --quote-source openai --dry-run
python -m social-quote-generator.src.main --episode 1 --quote-source deepseek --dry-run
python -m social-quote-generator.src.main --episode 1 --quote-source llama --dry-run
python -m social-quote-generator.src.main --episode 1 --quote-source random --dry-run
```

### Verbose Output

```bash
# Enable detailed logging
python -m social-quote-generator.src.main --episode 1 --dry-run --verbose
```

## Configuration

### Using Custom Configuration

```bash
# Specify custom config file
python -m social-quote-generator.src.main --episode 1 --config path/to/config.yaml --dry-run
```

### Configuration File Location

Default: `social-quote-generator/config/config.yaml`

Key settings:
- `general.episodes_dir`: Path to episode markdown files
- `general.texts_dir`: Path to quote text files
- `quotes.preferred_source`: Default quote source (claude, openai, deepseek, llama)
- `images.platforms`: Platform-specific dimensions and templates
- `social_media.enabled_platforms`: Platforms to publish to

## Output

Generated images are saved to: `output/images/`

Naming convention: `bge_{episode_number}_{platform}_{timestamp}.png`

Examples:
- `bge_1_instagram_20251007_161411.png`
- `bge_1_twitter_20251007_161411.png`
- `bge_1_facebook_20251007_161411.png`
- `bge_1_linkedin_20251007_161411.png`

## Platform Dimensions

| Platform  | Dimensions  | Aspect Ratio |
|-----------|-------------|--------------|
| Instagram | 1080x1080   | 1:1 (Square) |
| Twitter   | 1200x675    | 16:9         |
| Facebook  | 1200x630    | 1.91:1       |
| LinkedIn  | 1200x627    | 1.91:1       |

## Publishing to Social Media

⚠️ **Important:** Publishing requires API credentials configured in `.env` file

```bash
# Publish to configured platforms (removes --dry-run flag)
python -m social-quote-generator.src.main --episode 1 --publish

# Publish to specific platform
python -m social-quote-generator.src.main --episode 1 --platform twitter --publish
```

### Setting Up API Credentials

1. Copy the example environment file:
   ```bash
   cp social-quote-generator/.env.example social-quote-generator/.env
   ```

2. Edit `.env` and add your API credentials:
   ```
   TWITTER_API_KEY=your_key_here
   TWITTER_API_SECRET=your_secret_here
   TWITTER_ACCESS_TOKEN=your_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
   ```

3. See `PUBLISHERS.md` for detailed setup instructions for each platform

## Common Issues

### Font Warnings

If you see warnings about missing fonts:
```
WARNING - Font not found at templates/fonts/OpenSans-Regular.ttf
```

**Solution:** The tool will use system default fonts. To use custom fonts:
1. Download OpenSans or your preferred font
2. Place TTF files in `social-quote-generator/templates/fonts/`
3. Update `config.yaml` with font filename

### Episode Not Found

```
ERROR - Episode file not found: _episodes/999.md
```

**Solution:** Verify the episode number exists in the `_episodes/` directory

### Path Validation Errors

```
ERROR - Invalid episodes_dir: ../_episodes (contains '..' - directory traversal not allowed)
```

**Solution:** Run the command from the project root directory, not from inside `social-quote-generator/`

## Help

```bash
# Display all available options
python -m social-quote-generator.src.main --help

# Display version
python -m social-quote-generator.src.main --version
```

## Examples

### Example 1: Generate Instagram Post for Latest Episode

```bash
python -m social-quote-generator.src.main --episode 98 --platform instagram --dry-run
```

### Example 2: Generate Twitter Images for Multiple Episodes

```bash
python -m social-quote-generator.src.main --episodes 95,96,97,98 --platform twitter --dry-run
```

### Example 3: Test Different Quote Sources

```bash
# Generate 4 versions of the same episode with different AI quotes
python -m social-quote-generator.src.main --episode 1 --quote-source claude --platform instagram --dry-run
python -m social-quote-generator.src.main --episode 1 --quote-source openai --platform instagram --dry-run
python -m social-quote-generator.src.main --episode 1 --quote-source deepseek --platform instagram --dry-run
python -m social-quote-generator.src.main --episode 1 --quote-source llama --platform instagram --dry-run
```

### Example 4: Batch Generate for All Platforms

```bash
# Generate images for all platforms for a specific episode
python -m social-quote-generator.src.main --episode 50 --dry-run
```

## Tips

1. **Always test with --dry-run first** before publishing to social media
2. **Use --verbose** for troubleshooting
3. **Check output/images/** directory to verify generated images
4. **Customize templates** in `templates/` directory for your brand
5. **Review config.yaml** to adjust colors, fonts, and layout

## Support

For more detailed information:
- See `README.md` for comprehensive documentation
- See `PUBLISHERS.md` for social media setup
- See `UTILITIES_GUIDE.md` for advanced features
- Check `.kiro/summaries/` for test results and examples

## License

This tool is part of the BGE (Brigata dei Geek Estinti) project.
