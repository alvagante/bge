# BGE Social Quote Generator

Automated Python tool that generates visually appealing images from BGE (Brigata dei Geek Estinti) episode quotes and publishes them to social media platforms.

## Features

- 📝 Extract quotes from BGE episode files (supports multiple AI sources: Claude, OpenAI, DeepSeek, Llama)
- 🎨 Generate branded quote images for different social media platforms
- 🚀 Automated publishing to Twitter, Instagram, Facebook, and LinkedIn
- ⚙️ Configurable templates, fonts, and branding
- 🧪 Dry-run mode for testing without publishing
- 📊 Comprehensive error handling and logging
- 🔄 Retry logic with exponential backoff for API failures
- 🎯 Platform-specific image dimensions and templates

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [API Credential Setup](#api-credential-setup)
- [Configuration Guide](#configuration-guide)
- [Usage Examples](#usage-examples)
- [Template Customization](#template-customization)
- [Automation](#automation)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Development](#development)

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- API credentials for desired social media platforms

## Installation

### Step 1: Navigate to Project Directory

```bash
cd social-quote-generator
```

### Step 2: Create Virtual Environment

Creating a virtual environment isolates the project dependencies from your system Python installation.

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- `Pillow` - Image manipulation
- `PyYAML` - Configuration parsing
- `python-frontmatter` - Episode metadata extraction
- `tweepy` - Twitter API
- `instagrapi` - Instagram API
- `facebook-sdk` - Facebook API
- `python-dotenv` - Environment variable management
- `tenacity` - Retry logic

### Step 4: Install Package in Development Mode

```bash
pip install -e .
```

This allows you to run the tool from anywhere while developing.

### Step 5: Set Up Configuration

```bash
# Copy example configuration
cp config/config.example.yaml config/config.yaml

# Copy example environment file
cp .env.example .env
```

Now edit `.env` with your actual API credentials (see [API Credential Setup](#api-credential-setup)).

## API Credential Setup

### Twitter/X

1. **Create a Twitter Developer Account**
   - Go to https://developer.twitter.com/
   - Apply for a developer account (may take 1-2 days for approval)

2. **Create a New App**
   - Navigate to the Developer Portal
   - Click "Create App" and fill in the required information
   - Note: You need "Elevated" access for posting tweets

3. **Generate API Keys**
   - In your app settings, go to "Keys and tokens"
   - Generate the following:
     - API Key (Consumer Key)
     - API Secret (Consumer Secret)
     - Access Token
     - Access Token Secret

4. **Add to .env File**
   ```bash
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
   ```

5. **Enable in Configuration**
   Edit `config/config.yaml`:
   ```yaml
   social_media:
     enabled_platforms: ["twitter"]
     twitter:
       enabled: true
   ```

### Instagram

⚠️ **Warning**: Instagram uses username/password authentication, which is less secure than OAuth. Use with caution.

1. **Prepare Instagram Account**
   - Use a dedicated account for automation (recommended)
   - Ensure the account is not using 2FA, or handle 2FA challenges
   - Be aware of Instagram's rate limits and terms of service

2. **Add to .env File**
   ```bash
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   ```

3. **Enable in Configuration**
   Edit `config/config.yaml`:
   ```yaml
   social_media:
     enabled_platforms: ["instagram"]
     instagram:
       enabled: true
   ```

### Facebook

1. **Create a Facebook App**
   - Go to https://developers.facebook.com/
   - Click "Create App" and select "Business" type
   - Complete the app setup

2. **Get Page Access Token**
   - In your app dashboard, go to "Tools" → "Graph API Explorer"
   - Select your page from the dropdown
   - Generate a token with `pages_manage_posts` and `pages_read_engagement` permissions
   - For long-lived tokens, exchange the short-lived token using the Access Token Tool

3. **Get Page ID**
   - Go to your Facebook page
   - Click "About"
   - Scroll down to find your Page ID

4. **Add to .env File**
   ```bash
   FACEBOOK_ACCESS_TOKEN=your_long_lived_access_token
   FACEBOOK_PAGE_ID=your_page_id
   ```

5. **Enable in Configuration**
   Edit `config/config.yaml`:
   ```yaml
   social_media:
     enabled_platforms: ["facebook"]
     facebook:
       enabled: true
   ```

### LinkedIn

1. **Create a LinkedIn App**
   - Go to https://www.linkedin.com/developers/
   - Click "Create app" and fill in the required information
   - Request access to "Share on LinkedIn" and "Sign In with LinkedIn" products

2. **Get Access Token**
   - Use OAuth 2.0 flow to get an access token
   - Scopes needed: `w_member_social`, `r_liteprofile`
   - Note: LinkedIn tokens expire after 60 days

3. **Get Person URN**
   - Make a GET request to `https://api.linkedin.com/v2/me` with your access token
   - Extract the `id` field (this is your Person URN)

4. **Add to .env File**
   ```bash
   LINKEDIN_ACCESS_TOKEN=your_access_token
   LINKEDIN_PERSON_URN=your_person_urn
   ```

5. **Enable in Configuration**
   Edit `config/config.yaml`:
   ```yaml
   social_media:
     enabled_platforms: ["linkedin"]
     linkedin:
       enabled: true
   ```

## Configuration Guide

The tool is configured via `config/config.yaml`. Here's a detailed explanation of all options:

### General Settings

```yaml
general:
  episodes_dir: "_episodes"        # Directory containing episode markdown files
  texts_dir: "assets/texts"        # Directory with quote text files
  output_dir: "output/images"      # Where generated images are saved
  log_dir: "output/logs"           # Where log files are saved
  log_level: "INFO"                # DEBUG, INFO, WARNING, ERROR
```

### Quote Settings

```yaml
quotes:
  preferred_source: "claude"       # claude, openai, deepseek, llama, random
  fallback_sources:                # Sources to try if preferred is unavailable
    - "openai"
    - "deepseek"
    - "llama"
  max_length: 280                  # Maximum quote length in characters
```

**Quote Sources:**
- `claude` - Use Claude-generated quotes
- `openai` - Use OpenAI-generated quotes
- `deepseek` - Use DeepSeek-generated quotes
- `llama` - Use Llama-generated quotes
- `random` - Randomly select from available sources

### Image Settings

```yaml
images:
  templates_dir: "templates"
  fonts_dir: "templates/fonts"
  default_font: "OpenSans-Regular.ttf"
  
  # Platform-specific dimensions and templates
  platforms:
    instagram:
      dimensions: [1080, 1080]     # Square format
      template: "default_square.png"
    twitter:
      dimensions: [1200, 675]      # 16:9 landscape
      template: "default_landscape.png"
    facebook:
      dimensions: [1200, 630]      # Facebook recommended
      template: "default_landscape.png"
    linkedin:
      dimensions: [1200, 627]      # LinkedIn recommended
      template: "default_landscape.png"
  
  # Branding elements
  branding:
    logo_path: "assets/images/logo white.png"
    logo_position: "top-right"     # top-left, top-right, bottom-left, bottom-right
    logo_size: [100, 100]          # [width, height] in pixels
    primary_color: "#FFFFFF"       # Main text color
    secondary_color: "#000000"     # Accent color
    background_color: "#1a1a1a"    # Background color (if no template)
  
  # Text rendering
  text:
    quote_font_size: 48            # Base font size for quotes
    quote_color: "#FFFFFF"         # Quote text color
    quote_max_width: 900           # Maximum width for text wrapping
    metadata_font_size: 24         # Font size for episode info
    metadata_color: "#CCCCCC"      # Episode info color
```

### Social Media Settings

```yaml
social_media:
  enabled_platforms: ["twitter"]   # List of platforms to publish to
  
  twitter:
    enabled: true
    # API credentials loaded from environment variables
    api_key: "${TWITTER_API_KEY}"
    api_secret: "${TWITTER_API_SECRET}"
    access_token: "${TWITTER_ACCESS_TOKEN}"
    access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"
    # Caption template with placeholders
    caption_template: "🎙️ BGE Episodio {episode_number}: {title}\n\n{quote}\n\n{hashtags}\n\n🔗 {youtube_url}"
    hashtags: ["#BGE", "#DevOps", "#IT", "#Tech"]
```

**Caption Template Placeholders:**
- `{episode_number}` - Episode number
- `{title}` - Episode title
- `{quote}` - The selected quote
- `{hashtags}` - Generated hashtags
- `{youtube_url}` - YouTube video URL
- `{guests}` - Comma-separated guest names
- `{date}` - Episode publication date

## Usage Examples

### Basic Usage

**Generate image for a single episode (dry-run):**
```bash
python src/main.py --episode 1 --dry-run
```

This generates the image without publishing to social media.

**Generate and publish to Twitter:**
```bash
python src/main.py --episode 1 --platform twitter --publish
```

**Process all episodes:**
```bash
python src/main.py --all --dry-run
```

### Platform-Specific Generation

**Generate Instagram-format image:**
```bash
python src/main.py --episode 5 --platform instagram --dry-run
```

**Generate for multiple platforms:**
```bash
# Generate for Instagram
python src/main.py --episode 5 --platform instagram --dry-run

# Generate for Twitter
python src/main.py --episode 5 --platform twitter --dry-run
```

### Multiple Episodes

**Process specific episodes:**
```bash
python src/main.py --episodes 1,5,10,15 --platform twitter --dry-run
```

**Process all episodes for Instagram:**
```bash
python src/main.py --all --platform instagram --dry-run
```

### Quote Source Selection

**Use specific AI source:**
```bash
python src/main.py --episode 1 --quote-source claude --dry-run
```

**Use random quote source:**
```bash
python src/main.py --episode 1 --quote-source random --dry-run
```

### Custom Configuration

**Use custom config file:**
```bash
python src/main.py --episode 1 --config /path/to/custom-config.yaml --dry-run
```

**Override output directory:**
```bash
python src/main.py --episode 1 --output-dir /path/to/output --dry-run
```

### Verbose Logging

**Enable detailed logging:**
```bash
python src/main.py --episode 1 --verbose --dry-run
```

### Publishing Workflow

**Recommended workflow for publishing:**

1. **Test with dry-run:**
   ```bash
   python src/main.py --episode 42 --platform twitter --dry-run
   ```

2. **Review generated image** in `output/images/`

3. **Publish if satisfied:**
   ```bash
   python src/main.py --episode 42 --platform twitter --publish
   ```

### Batch Processing

**Generate images for latest 5 episodes:**
```bash
python src/main.py --episodes 94,95,96,97,98 --platform instagram --dry-run
```

**Generate for all platforms:**
```bash
for platform in instagram twitter facebook linkedin; do
  python src/main.py --episode 1 --platform $platform --dry-run
done
```

## Template Customization

### Using Custom Background Templates

1. **Create your template image:**
   - Instagram: 1080x1080 pixels (square)
   - Twitter: 1200x675 pixels (landscape)
   - Facebook: 1200x630 pixels
   - LinkedIn: 1200x627 pixels

2. **Save template to templates directory:**
   ```bash
   cp my-custom-template.png templates/custom_instagram.png
   ```

3. **Update configuration:**
   ```yaml
   images:
     platforms:
       instagram:
         template: "custom_instagram.png"
   ```

### Using Custom Fonts

1. **Add font file to fonts directory:**
   ```bash
   cp MyCustomFont.ttf templates/fonts/
   ```

2. **Update configuration:**
   ```yaml
   images:
     default_font: "MyCustomFont.ttf"
   ```

**Supported font formats:** TTF, OTF

### Customizing Logo

1. **Prepare logo image:**
   - Use PNG format with transparency
   - Recommended size: 100x100 to 200x200 pixels

2. **Update configuration:**
   ```yaml
   images:
     branding:
       logo_path: "path/to/your/logo.png"
       logo_position: "top-right"  # or top-left, bottom-left, bottom-right
       logo_size: [150, 150]
   ```

### Customizing Colors

```yaml
images:
  branding:
    primary_color: "#FF6B6B"      # Quote text color
    secondary_color: "#4ECDC4"    # Accent color
    background_color: "#1A535C"   # Background (if no template)
  text:
    quote_color: "#FFFFFF"        # Override quote color
    metadata_color: "#E0E0E0"     # Episode info color
```

**Color formats supported:** Hex colors (#RRGGBB)

### Advanced Template Design

For more control over image design, create a template image with:
- Pre-designed background
- Decorative elements
- Color gradients
- Textures

The tool will overlay the quote text and logo on your template.

## Automation

### Cron Jobs (Linux/macOS)

**Post new episode quote every Monday at 10 AM:**

1. Open crontab editor:
   ```bash
   crontab -e
   ```

2. Add cron job:
   ```bash
   0 10 * * 1 cd /path/to/social-quote-generator && /path/to/venv/bin/python src/main.py --episode latest --platform twitter --publish >> /path/to/logs/cron.log 2>&1
   ```

**Post to Instagram daily at 3 PM:**
```bash
0 15 * * * cd /path/to/social-quote-generator && /path/to/venv/bin/python src/main.py --episode random --platform instagram --publish
```

**Generate images for all episodes weekly:**
```bash
0 2 * * 0 cd /path/to/social-quote-generator && /path/to/venv/bin/python src/main.py --all --dry-run
```

### Scheduled Tasks (Windows)

1. **Open Task Scheduler**

2. **Create Basic Task:**
   - Name: "BGE Quote Publisher"
   - Trigger: Daily at 10:00 AM
   - Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `src/main.py --episode latest --platform twitter --publish`
   - Start in: `C:\path\to\social-quote-generator`

### GitHub Actions

Create `.github/workflows/publish-quote.yml`:

```yaml
name: Publish Daily Quote

on:
  schedule:
    - cron: '0 10 * * *'  # Daily at 10 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd social-quote-generator
          pip install -r requirements.txt
      
      - name: Publish quote
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_TOKEN_SECRET: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
        run: |
          cd social-quote-generator
          python src/main.py --episode latest --platform twitter --publish
```

Add your API credentials to GitHub repository secrets.

### Docker Container

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py", "--episode", "latest", "--publish"]
```

Run with docker-compose:

```yaml
version: '3.8'
services:
  quote-generator:
    build: .
    env_file: .env
    volumes:
      - ./output:/app/output
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'PIL'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. API Authentication Failures

**Problem:** `Twitter API authentication failed`

**Solutions:**
- Verify credentials in `.env` file are correct
- Ensure no extra spaces or quotes around values
- Check that Twitter app has "Elevated" access
- Verify access tokens haven't expired

**Test authentication:**
```bash
python src/main.py --episode 1 --platform twitter --dry-run --verbose
```

#### 3. Missing Episode Files

**Problem:** `Episode file not found: _episodes/42.md`

**Solutions:**
- Verify episode file exists in `_episodes/` directory
- Check episode number is correct
- Ensure you're running from the correct directory (parent of `social-quote-generator/`)

#### 4. Font Rendering Issues

**Problem:** Text appears garbled or uses wrong font

**Solutions:**
- Verify font file exists in `templates/fonts/`
- Check font file is not corrupted
- Try using a different font
- Ensure font supports Italian characters

#### 5. Image Generation Fails

**Problem:** `Failed to generate image: Permission denied`

**Solutions:**
- Check write permissions on `output/images/` directory
- Ensure output directory exists:
  ```bash
  mkdir -p output/images output/logs
  ```
- Verify disk space is available

#### 6. Instagram Login Issues

**Problem:** `Instagram login failed: Challenge required`

**Solutions:**
- Instagram may require 2FA verification
- Try logging in manually from the same IP first
- Use a dedicated account without 2FA
- Be aware of Instagram's rate limits
- Consider using Instagram's official API (requires business account)

#### 7. Rate Limiting

**Problem:** `Rate limit exceeded`

**Solutions:**
- Wait before retrying (tool has automatic backoff)
- Reduce posting frequency
- Check platform-specific rate limits:
  - Twitter: 300 tweets per 3 hours
  - Instagram: ~100-150 posts per day
  - Facebook: Varies by page
  - LinkedIn: 100 posts per day

#### 8. Configuration Errors

**Problem:** `Invalid configuration: missing required field`

**Solutions:**
- Validate YAML syntax:
  ```bash
  python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
  ```
- Compare with `config/config.example.yaml`
- Check indentation (YAML is whitespace-sensitive)

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
python src/main.py --episode 1 --verbose --dry-run
```

Check log files in `output/logs/` for detailed error messages.

### Getting Help

If you encounter issues not covered here:

1. Check the log files in `output/logs/`
2. Run with `--verbose` flag for detailed output
3. Verify all dependencies are installed: `pip list`
4. Check Python version: `python --version` (should be 3.8+)
5. Review the [GitHub Issues](link-to-issues) for similar problems

## Security Best Practices

### Credential Management

1. **Never commit credentials to version control:**
   ```bash
   # Verify .gitignore includes:
   .env
   config/config.yaml  # If it contains secrets
   ```

2. **Use environment variables:**
   - Store all secrets in `.env` file
   - Use `${VARIABLE_NAME}` syntax in config files
   - Never hardcode credentials in configuration

3. **Rotate credentials regularly:**
   - Change API keys every 90 days
   - Regenerate tokens after any security incident
   - Use different credentials for development and production

4. **Use minimal permissions:**
   - Twitter: Request only "Read and Write" access, not "Read, Write, and Direct Messages"
   - Facebook: Use page-specific tokens, not user tokens
   - LinkedIn: Request only `w_member_social` scope

5. **Secure credential storage:**
   - Set restrictive file permissions:
     ```bash
     chmod 600 .env
     chmod 600 config/config.yaml
     ```
   - Use encrypted storage for production deployments
   - Consider using secret management services (AWS Secrets Manager, HashiCorp Vault)

### Instagram Security Considerations

⚠️ **Instagram requires username/password authentication, which has security implications:**

1. **Use a dedicated account:**
   - Create a separate Instagram account for automation
   - Don't use your personal account

2. **Limit account permissions:**
   - Don't link payment methods
   - Don't store sensitive information in the account

3. **Monitor for suspicious activity:**
   - Enable email notifications for login attempts
   - Regularly review account activity

4. **Be aware of risks:**
   - Instagram may flag automated activity
   - Account could be temporarily locked
   - Consider using Instagram's official Graph API (requires business account)

### Network Security

1. **Use HTTPS only:**
   - All API calls use encrypted connections
   - Never disable SSL verification

2. **Secure your deployment:**
   - Run on trusted servers
   - Use firewall rules to restrict access
   - Keep system and dependencies updated

3. **API rate limiting:**
   - Tool implements automatic backoff
   - Don't disable retry limits
   - Respect platform rate limits

### Input Validation

The tool validates all inputs to prevent security issues:

- **Path traversal prevention:** File paths are validated
- **SQL injection prevention:** No database queries (file-based)
- **Command injection prevention:** No shell command execution with user input

### Audit and Monitoring

1. **Review logs regularly:**
   ```bash
   tail -f output/logs/social-quote-generator.log
   ```

2. **Monitor API usage:**
   - Check platform analytics for unusual activity
   - Review published posts regularly

3. **Track credential usage:**
   - Log authentication attempts
   - Alert on repeated failures

### Production Deployment Checklist

- [ ] All credentials stored in environment variables
- [ ] `.env` file has restrictive permissions (600)
- [ ] `.env` is in `.gitignore`
- [ ] Using minimal API permissions
- [ ] Credentials rotated within last 90 days
- [ ] Logs are monitored
- [ ] Rate limiting is configured
- [ ] Backup credentials stored securely
- [ ] Error notifications configured
- [ ] Running on secure, updated system

## Development

### Project Structure

```
social-quote-generator/
├── src/
│   ├── main.py                 # CLI entry point
│   ├── config.py               # Configuration management
│   ├── orchestrator.py         # Pipeline orchestration
│   ├── extractors/
│   │   ├── base.py            # Base extractor interface
│   │   └── quote_extractor.py # Quote extraction logic
│   ├── generators/
│   │   ├── base.py            # Base generator interface
│   │   └── image_generator.py # Image creation
│   ├── publishers/
│   │   ├── base.py            # Base publisher interface
│   │   ├── twitter_publisher.py
│   │   ├── instagram_publisher.py
│   │   ├── facebook_publisher.py
│   │   └── linkedin_publisher.py
│   └── utils/
│       ├── logger.py          # Logging utilities
│       └── validators.py      # Input validation
├── tests/                     # Test suite
├── config/                    # Configuration files
├── templates/                 # Image templates and fonts
└── output/                    # Generated content
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_extractors.py

# Run with verbose output
pytest -v
```

### Code Quality

**Format code:**
```bash
black src/ tests/
```

**Lint code:**
```bash
flake8 src/ tests/
```

**Type checking:**
```bash
mypy src/
```

### Adding New Features

1. Create feature branch
2. Implement feature with tests
3. Run test suite
4. Format and lint code
5. Submit pull request

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Follow code style guidelines
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: [link-to-issues]
- Documentation: [link-to-docs]
- Email: [contact-email]

---

**Made with ❤️ for La Brigata dei Geek Estinti**
