# BGE Social Quote Generator - Quick Start Guide

## Installation

```bash
# Navigate to the project root directory
cd /path/to/bge.github.io

# Install the package in development mode
pip install -e social-quote-generator/

# Verify installation
bge-quote-gen --version
```

## Basic Usage

After installation, you can use the `bge-quote-gen` command from anywhere:

### Generate Images for a Single Episode

```bash
# Generate images for all platforms (dry-run mode)
bge-quote-gen --episode 1 --dry-run

# Generate image for specific platform
bge-quote-gen --episode 1 --platform instagram --dry-run
```

### Generate Images for Multiple Episodes

```bash
# Process multiple episodes
bge-quote-gen --episodes 1,5,10 --platform twitter --dry-run

# Process all episodes (use with caution!)
bge-quote-gen --all --platform instagram --dry-run
```

### Choose Quote Source

```bash
# Use specific AI quote source
bge-quote-gen --episode 1 --quote-source claude --dry-run
bge-quote-gen --episode 1 --quote-source openai --dry-run
bge-quote-gen --episode 1 --quote-source deepseek --dry-run
bge-quote-gen --episode 1 --quote-source llama --dry-run
bge-quote-gen --episode 1 --quote-source random --dry-run
```

### Verbose Output

```bash
# Enable detailed logging
bge-quote-gen --episode 1 --dry-run --verbose
```

## Configuration

### Using Custom Configuration

```bash
# Specify custom config file (absolute or relative path)
bge-quote-gen --episode 1 --config /absolute/path/to/config.yaml --dry-run

# Or use relative path (searches multiple locations automatically)
bge-quote-gen --episode 1 --config config/config.yaml --dry-run
```

### Configuration File Location

The tool automatically searches for config files in multiple locations:
1. Relative to current working directory
2. In `social-quote-generator/config/config.yaml` (project structure)
3. Relative to package installation directory

Default: `config/config.yaml` (searches automatically)

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

## Queue-Based Publishing (Recommended)

Schedule posts for automated publishing:

```bash
# Add to queue with default schedule
bge-quote-gen --episode 1 --queue

# Add with custom schedule
bge-quote-gen --episode 1 --queue --schedule "2025-10-13 09:00"

# Add with staggered schedule (6 hours between platforms)
bge-quote-gen --episode 1 --queue --stagger "6h"

# List pending items
bge-quote-gen --queue-list

# Publish from queue (for cron jobs)
bge-quote-gen --queue-publish
```

**See `QUEUE_GUIDE.md` for complete queue system documentation.**

## Direct Publishing to Social Media

⚠️ **Important:** Publishing requires API credentials configured in `.env` file

```bash
# Publish to configured platforms (removes --dry-run flag)
bge-quote-gen --episode 1 --publish

# Publish to specific platform
bge-quote-gen --episode 1 --platform twitter --publish
```

### Setting Up API Credentials

Publishing to social media requires API credentials for each platform.

1. **Create `.env` file:**
   ```bash
   cd social-quote-generator
   touch .env
   chmod 600 .env
   ```

2. **Add credentials to `.env`:**
   ```bash
   # Twitter/X (requires Developer Account + Elevated Access)
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

   # Instagram (simple username/password)
   INSTAGRAM_USERNAME=your_username
   INSTAGRAM_PASSWORD=your_password

   # Facebook (requires Developer App + Page Token)
   FACEBOOK_ACCESS_TOKEN=your_page_access_token
   FACEBOOK_PAGE_ID=your_page_id

   # LinkedIn (requires Developer App + OAuth)
   LINKEDIN_ACCESS_TOKEN=your_access_token
   LINKEDIN_PERSON_URN=urn:li:person:your_id
   ```

3. **Get API tokens:**

   See **[PUBLISHERS.md](PUBLISHERS.md)** for comprehensive step-by-step instructions for obtaining tokens for each platform.

   **Quick summary:**
   - **Twitter/X:** 30-60 min setup, requires Developer account + Elevated Access approval
   - **Instagram:** 5 min setup, just username/password (unofficial method)
   - **Facebook:** 30-45 min setup, requires Facebook Developer app + Page
   - **LinkedIn:** 30-45 min setup, requires LinkedIn Developer app + Page

4. **Test your credentials:**
   ```bash
   # Test without publishing (dry-run mode)
   bge-quote-gen --episode 1 --platform twitter --dry-run --verbose
   ```

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
bge-quote-gen --help

# Display version
bge-quote-gen --version
```

## Examples

### Example 1: Generate Instagram Post for Latest Episode

```bash
bge-quote-gen --episode 98 --platform instagram --dry-run
```

### Example 2: Generate Twitter Images for Multiple Episodes

```bash
bge-quote-gen --episodes 95,96,97,98 --platform twitter --dry-run
```

### Example 3: Test Different Quote Sources

```bash
# Generate 4 versions of the same episode with different AI quotes
bge-quote-gen --episode 1 --quote-source claude --platform instagram --dry-run
bge-quote-gen --episode 1 --quote-source openai --platform instagram --dry-run
bge-quote-gen --episode 1 --quote-source deepseek --platform instagram --dry-run
bge-quote-gen --episode 1 --quote-source llama --platform instagram --dry-run
```

### Example 4: Batch Generate for All Platforms

```bash
# Generate images for all platforms for a specific episode
bge-quote-gen --episode 50 --dry-run
```

### Example 5: Run from Any Directory

```bash
# The command works from anywhere after installation
cd /tmp
bge-quote-gen --episode 1 --platform instagram --dry-run
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
