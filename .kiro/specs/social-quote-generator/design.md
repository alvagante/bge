# Design Document

## Overview

The Social Quote Generator is a Python-based CLI tool that automates the creation and distribution of quote images from BGE podcast episodes to social media platforms. The tool follows a modular architecture with clear separation of concerns: data extraction, image generation, and social media publishing.

The system will be designed as a pipeline where episode data flows through extraction, transformation (image generation), and loading (social media publishing) stages. Each stage can operate independently, allowing for flexible usage patterns (e.g., generate images without publishing, or publish pre-generated images).

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Entry Point                          │
│                  (main.py / cli.py)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Configuration Manager                       │
│              (config.py / config.yaml)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Pipeline Orchestrator                      │
│                   (orchestrator.py)                         │
└──────┬──────────────────┬──────────────────┬───────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
│   Quote     │   │    Image     │   │    Social       │
│  Extractor  │──▶│  Generator   │──▶│    Media        │
│             │   │              │   │   Publisher     │
└─────────────┘   └──────────────┘   └─────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
│  Episode    │   │   Template   │   │   Platform      │
│   Files     │   │   Engine     │   │   Adapters      │
│             │   │              │   │  (Twitter, IG)  │
└─────────────┘   └──────────────┘   └─────────────────┘
```

### Directory Structure

```
social-quote-generator/
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── config.py               # Configuration management
│   ├── orchestrator.py         # Pipeline orchestration
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py            # Base extractor interface
│   │   ├── episode_extractor.py  # Episode data extraction
│   │   └── quote_extractor.py    # Quote extraction logic
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── base.py            # Base generator interface
│   │   ├── image_generator.py # Image creation logic
│   │   └── template_engine.py # Template rendering
│   ├── publishers/
│   │   ├── __init__.py
│   │   ├── base.py            # Base publisher interface
│   │   ├── twitter_publisher.py
│   │   ├── instagram_publisher.py
│   │   ├── facebook_publisher.py
│   │   └── linkedin_publisher.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Logging utilities
│       ├── validators.py      # Input validation
│       └── helpers.py         # Common utilities
├── templates/
│   ├── default_square.png     # 1080x1080 template
│   ├── default_landscape.png  # 1200x675 template
│   └── fonts/
│       └── OpenSans-Regular.ttf
├── config/
│   ├── config.yaml            # Main configuration
│   └── config.example.yaml    # Example configuration
├── output/
│   ├── images/                # Generated images
│   └── logs/                  # Log files
├── tests/
│   ├── __init__.py
│   ├── test_extractors.py
│   ├── test_generators.py
│   └── test_publishers.py
├── requirements.txt
├── setup.py
└── README.md
```

## Components and Interfaces

### 1. Configuration Manager (`config.py`)

**Responsibility:** Load, validate, and provide access to configuration settings.

**Interface:**
```python
class Config:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Load configuration from file"""
        
    @property
    def image_settings(self) -> ImageSettings:
        """Get image generation settings"""
        
    @property
    def social_media_settings(self) -> SocialMediaSettings:
        """Get social media platform settings"""
        
    @property
    def quote_settings(self) -> QuoteSettings:
        """Get quote extraction settings"""
        
    def validate(self) -> bool:
        """Validate configuration completeness"""
```

**Configuration Schema:**
```yaml
# config.yaml
general:
  episodes_dir: "_episodes"
  texts_dir: "assets/texts"
  output_dir: "output/images"
  log_dir: "output/logs"
  log_level: "INFO"

quotes:
  preferred_source: "claude"  # claude, openai, deepseek, llama, random
  fallback_sources: ["openai", "deepseek", "llama"]
  max_length: 280

images:
  templates_dir: "templates"
  fonts_dir: "templates/fonts"
  default_font: "OpenSans-Regular.ttf"
  
  platforms:
    instagram:
      dimensions: [1080, 1080]
      template: "default_square.png"
    twitter:
      dimensions: [1200, 675]
      template: "default_landscape.png"
    facebook:
      dimensions: [1200, 630]
      template: "default_landscape.png"
    linkedin:
      dimensions: [1200, 627]
      template: "default_landscape.png"
  
  branding:
    logo_path: "assets/images/logo white.png"
    logo_position: "top-right"  # top-left, top-right, bottom-left, bottom-right
    logo_size: [100, 100]
    primary_color: "#FFFFFF"
    secondary_color: "#000000"
    background_color: "#1a1a1a"
  
  text:
    quote_font_size: 48
    quote_color: "#FFFFFF"
    quote_max_width: 900
    metadata_font_size: 24
    metadata_color: "#CCCCCC"

social_media:
  enabled_platforms: ["twitter"]  # twitter, instagram, facebook, linkedin
  
  twitter:
    enabled: true
    api_key: "${TWITTER_API_KEY}"
    api_secret: "${TWITTER_API_SECRET}"
    access_token: "${TWITTER_ACCESS_TOKEN}"
    access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"
    caption_template: "🎙️ BGE Episodio {episode_number}: {title}\n\n{quote}\n\n{hashtags}\n\n🔗 {youtube_url}"
    hashtags: ["#BGE", "#DevOps", "#IT", "#Tech"]
  
  instagram:
    enabled: false
    username: "${INSTAGRAM_USERNAME}"
    password: "${INSTAGRAM_PASSWORD}"
    caption_template: "🎙️ BGE Episodio {episode_number}\n\n{quote}\n\n{hashtags}"
    hashtags: ["#BGE", "#DevOps", "#IT", "#Tech", "#Podcast"]
```

### 2. Quote Extractor (`extractors/quote_extractor.py`)

**Responsibility:** Extract quotes and metadata from episode files.

**Interface:**
```python
@dataclass
class EpisodeQuote:
    episode_number: str
    title: str
    quote: str
    quote_source: str  # claude, openai, deepseek, llama
    guests: List[str]
    date: str
    youtube_id: str
    tags: List[str]

class QuoteExtractor:
    def __init__(self, config: Config):
        """Initialize with configuration"""
        
    def extract_episode(self, episode_number: str) -> Optional[EpisodeQuote]:
        """Extract quote data for a specific episode"""
        
    def extract_all_episodes(self) -> List[EpisodeQuote]:
        """Extract quote data for all episodes"""
        
    def _parse_episode_file(self, file_path: str) -> Dict:
        """Parse YAML frontmatter from episode markdown file"""
        
    def _select_quote(self, episode_data: Dict) -> Tuple[str, str]:
        """Select best quote based on configuration preferences"""
        
    def _load_quote_from_file(self, episode_number: str, source: str) -> Optional[str]:
        """Load quote from separate text file"""
```

**Key Logic:**
- Parse YAML frontmatter from `_episodes/*.md` files
- Extract quotes from frontmatter fields (quote_claude, quote_openai, etc.)
- Fall back to separate text files in `assets/texts/` if needed
- Select quote based on configured preference or randomly
- Handle missing or malformed data gracefully

### 3. Image Generator (`generators/image_generator.py`)

**Responsibility:** Create branded quote images for different platforms.

**Interface:**
```python
@dataclass
class GeneratedImage:
    file_path: str
    platform: str
    episode_number: str
    dimensions: Tuple[int, int]
    timestamp: datetime

class ImageGenerator:
    def __init__(self, config: Config):
        """Initialize with configuration"""
        
    def generate(
        self, 
        quote_data: EpisodeQuote, 
        platform: str = "instagram"
    ) -> GeneratedImage:
        """Generate image for specified platform"""
        
    def _load_template(self, platform: str) -> Image:
        """Load background template for platform"""
        
    def _render_quote(self, image: Image, quote: str) -> Image:
        """Render quote text on image"""
        
    def _render_metadata(self, image: Image, metadata: Dict) -> Image:
        """Render episode metadata on image"""
        
    def _add_logo(self, image: Image) -> Image:
        """Add BGE logo to image"""
        
    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within max width"""
        
    def _save_image(self, image: Image, episode_number: str, platform: str) -> str:
        """Save image with proper naming convention"""
```

**Key Logic:**
- Use Pillow (PIL) for image manipulation
- Load platform-specific templates or create solid color backgrounds
- Calculate text positioning for centered, readable quotes
- Implement text wrapping algorithm for long quotes
- Add logo overlay with transparency
- Support custom fonts with fallback to system fonts
- Generate filename: `bge_{episode_number}_{platform}_{timestamp}.png`

**Text Rendering Algorithm:**
```python
def render_centered_text(image, text, font, max_width, y_position):
    """
    1. Split text into words
    2. Build lines that fit within max_width
    3. Calculate total text block height
    4. Center text block vertically if y_position is None
    5. Render each line centered horizontally
    """
```

### 4. Social Media Publishers (`publishers/`)

**Responsibility:** Publish images to social media platforms with appropriate captions.

**Base Interface:**
```python
class BasePublisher(ABC):
    def __init__(self, config: Config):
        """Initialize with configuration"""
        
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with platform API"""
        
    @abstractmethod
    def publish(
        self, 
        image_path: str, 
        quote_data: EpisodeQuote,
        dry_run: bool = False
    ) -> PublishResult:
        """Publish image with caption"""
        
    def _generate_caption(self, quote_data: EpisodeQuote) -> str:
        """Generate caption from template"""
        
    def _generate_hashtags(self, quote_data: EpisodeQuote) -> str:
        """Generate hashtags from episode tags"""

@dataclass
class PublishResult:
    success: bool
    platform: str
    post_url: Optional[str]
    error: Optional[str]
    timestamp: datetime
```

**Twitter Publisher:**
```python
class TwitterPublisher(BasePublisher):
    def __init__(self, config: Config):
        self.api = tweepy.Client(
            consumer_key=config.twitter_api_key,
            consumer_secret=config.twitter_api_secret,
            access_token=config.twitter_access_token,
            access_token_secret=config.twitter_access_token_secret
        )
        
    def publish(self, image_path: str, quote_data: EpisodeQuote, dry_run: bool = False):
        """
        1. Upload image using media upload API
        2. Generate caption with episode info and hashtags
        3. Create tweet with image
        4. Return post URL or error
        """
```

**Instagram Publisher:**
```python
class InstagramPublisher(BasePublisher):
    def __init__(self, config: Config):
        self.client = Client()
        self.client.login(config.instagram_username, config.instagram_password)
        
    def publish(self, image_path: str, quote_data: EpisodeQuote, dry_run: bool = False):
        """
        1. Generate caption with hashtags
        2. Upload photo with caption
        3. Return post URL or error
        """
```

### 5. Pipeline Orchestrator (`orchestrator.py`)

**Responsibility:** Coordinate the entire workflow from extraction to publishing.

**Interface:**
```python
@dataclass
class PipelineResult:
    total_episodes: int
    successful_images: int
    failed_images: int
    successful_posts: int
    failed_posts: int
    results: List[Dict]

class PipelineOrchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.extractor = QuoteExtractor(config)
        self.generator = ImageGenerator(config)
        self.publishers = self._init_publishers()
        
    def run(
        self,
        episode_numbers: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        publish: bool = False,
        dry_run: bool = False
    ) -> PipelineResult:
        """
        Execute the full pipeline:
        1. Extract quotes for specified episodes
        2. Generate images for specified platforms
        3. Optionally publish to social media
        4. Return summary results
        """
        
    def _init_publishers(self) -> Dict[str, BasePublisher]:
        """Initialize enabled publishers"""
        
    def _process_episode(
        self, 
        quote_data: EpisodeQuote,
        platforms: List[str],
        publish: bool,
        dry_run: bool
    ) -> Dict:
        """Process single episode through pipeline"""
```

### 6. CLI Entry Point (`main.py`)

**Responsibility:** Provide command-line interface using argparse or click.

**Interface:**
```python
def main():
    parser = argparse.ArgumentParser(
        description="BGE Social Quote Generator"
    )
    parser.add_argument(
        "--episode", "-e",
        help="Process specific episode number"
    )
    parser.add_argument(
        "--episodes",
        help="Process multiple episodes (comma-separated)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Process all episodes"
    )
    parser.add_argument(
        "--platform", "-p",
        choices=["instagram", "twitter", "facebook", "linkedin"],
        help="Generate images for specific platform"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish to social media"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate images without publishing"
    )
    parser.add_argument(
        "--config", "-c",
        default="config/config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for images"
    )
    parser.add_argument(
        "--quote-source",
        choices=["claude", "openai", "deepseek", "llama", "random"],
        help="Preferred quote source"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    # Initialize orchestrator
    # Execute pipeline
    # Display results
```

## Data Models

### Episode Quote Data Model
```python
@dataclass
class EpisodeQuote:
    episode_number: str
    title: str
    quote: str
    quote_source: str
    guests: List[str]
    date: str
    youtube_id: str
    tags: List[str]
    duration: int
    description: str
    
    @property
    def youtube_url(self) -> str:
        return f"https://youtube.com/watch?v={self.youtube_id}"
    
    @property
    def formatted_guests(self) -> str:
        return ", ".join(self.guests)
```

### Image Settings Data Model
```python
@dataclass
class ImageSettings:
    dimensions: Tuple[int, int]
    template_path: Optional[str]
    font_path: str
    quote_font_size: int
    quote_color: str
    quote_max_width: int
    metadata_font_size: int
    metadata_color: str
    logo_path: str
    logo_position: str
    logo_size: Tuple[int, int]
    background_color: str
```

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Missing configuration file → Create default and exit with instructions
   - Invalid configuration values → Log error and use defaults where possible
   - Missing API credentials → Warn and disable affected platforms

2. **Data Extraction Errors**
   - Episode file not found → Log warning and skip
   - Malformed YAML → Log error with file path and skip
   - Missing quote data → Try fallback sources, log if all fail

3. **Image Generation Errors**
   - Template file not found → Use solid color background
   - Font file not found → Use PIL default font
   - Image save failure → Log error with path and permissions info

4. **Publishing Errors**
   - Authentication failure → Log error and disable platform
   - API rate limit → Implement exponential backoff (1s, 2s, 4s, 8s)
   - Network errors → Retry up to 3 times with backoff
   - Invalid image format → Log error and skip

### Error Handling Strategy

```python
class ErrorHandler:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.errors = []
        
    def handle_extraction_error(self, episode: str, error: Exception):
        """Log and record extraction errors"""
        self.logger.warning(f"Failed to extract episode {episode}: {error}")
        self.errors.append({"type": "extraction", "episode": episode, "error": str(error)})
        
    def handle_generation_error(self, episode: str, platform: str, error: Exception):
        """Log and record generation errors"""
        self.logger.error(f"Failed to generate image for episode {episode} ({platform}): {error}")
        self.errors.append({"type": "generation", "episode": episode, "platform": platform, "error": str(error)})
        
    def handle_publishing_error(self, episode: str, platform: str, error: Exception):
        """Log and record publishing errors"""
        self.logger.error(f"Failed to publish episode {episode} to {platform}: {error}")
        self.errors.append({"type": "publishing", "episode": episode, "platform": platform, "error": str(error)})
        
    def get_summary(self) -> Dict:
        """Get error summary"""
        return {
            "total_errors": len(self.errors),
            "by_type": self._group_by_type(),
            "details": self.errors
        }
```

## Testing Strategy

### Unit Tests

1. **Configuration Tests**
   - Test loading valid configuration
   - Test handling missing configuration
   - Test environment variable substitution
   - Test validation logic

2. **Extractor Tests**
   - Test parsing valid episode files
   - Test handling malformed YAML
   - Test quote source selection logic
   - Test fallback mechanisms

3. **Generator Tests**
   - Test image creation with various quote lengths
   - Test text wrapping algorithm
   - Test logo placement
   - Test platform-specific dimensions

4. **Publisher Tests**
   - Test caption generation
   - Test hashtag generation
   - Mock API calls to test error handling
   - Test retry logic

### Integration Tests

1. **End-to-End Pipeline**
   - Test full pipeline with sample episode
   - Test dry-run mode
   - Test error recovery

2. **File System Operations**
   - Test reading episode files
   - Test writing images
   - Test log file creation

### Test Data

Create sample episode files and expected outputs:
```
tests/fixtures/
├── episodes/
│   ├── 1.md
│   └── 2.md
├── texts/
│   ├── 1_quote_claude.txt
│   └── 2_quote_openai.txt
├── expected_images/
│   ├── bge_1_instagram.png
│   └── bge_1_twitter.png
└── config/
    └── test_config.yaml
```

## Dependencies

### Core Dependencies
```
# requirements.txt
Pillow>=10.0.0              # Image manipulation
PyYAML>=6.0                 # Configuration parsing
python-frontmatter>=1.0.0   # YAML frontmatter parsing
tweepy>=4.14.0              # Twitter API
instagrapi>=2.0.0           # Instagram API
facebook-sdk>=3.1.0         # Facebook API
linkedin-api>=2.0.0         # LinkedIn API (unofficial)
python-dotenv>=1.0.0        # Environment variable management
requests>=2.31.0            # HTTP requests
tenacity>=8.2.0             # Retry logic
click>=8.1.0                # CLI framework (alternative to argparse)
```

### Development Dependencies
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.0
```

## Deployment and Usage

### Installation

```bash
# Clone repository
git clone <repo-url>
cd social-quote-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy example configuration
cp config/config.example.yaml config/config.yaml

# Edit configuration with your settings
nano config/config.yaml
```

### Configuration Setup

1. **Set up API credentials:**
   ```bash
   # Create .env file
   echo "TWITTER_API_KEY=your_key" >> .env
   echo "TWITTER_API_SECRET=your_secret" >> .env
   echo "TWITTER_ACCESS_TOKEN=your_token" >> .env
   echo "TWITTER_ACCESS_TOKEN_SECRET=your_token_secret" >> .env
   ```

2. **Customize templates:**
   - Place custom background images in `templates/`
   - Add custom fonts to `templates/fonts/`
   - Update paths in `config/config.yaml`

### Usage Examples

```bash
# Generate image for episode 1 (dry-run)
python src/main.py --episode 1 --dry-run

# Generate images for all episodes for Instagram
python src/main.py --all --platform instagram

# Generate and publish episode 42 to Twitter
python src/main.py --episode 42 --platform twitter --publish

# Generate images for multiple episodes
python src/main.py --episodes 1,5,10,15 --platform instagram

# Use specific quote source
python src/main.py --episode 1 --quote-source claude

# Verbose output
python src/main.py --episode 1 --verbose
```

### Automation

Set up cron job or scheduled task for automatic posting:

```bash
# crontab -e
# Post new episode quote every Monday at 10 AM
0 10 * * 1 cd /path/to/social-quote-generator && ./venv/bin/python src/main.py --episode latest --publish
```

## Security Considerations

1. **API Credentials**
   - Store in environment variables or `.env` file
   - Never commit credentials to version control
   - Add `.env` to `.gitignore`
   - Use read-only API permissions where possible

2. **File System Access**
   - Validate all file paths to prevent directory traversal
   - Use absolute paths internally
   - Restrict write access to output directories only

3. **Input Validation**
   - Validate episode numbers (numeric, positive)
   - Sanitize text input before rendering
   - Validate image dimensions (reasonable limits)
   - Validate configuration values

4. **Rate Limiting**
   - Respect platform API rate limits
   - Implement exponential backoff
   - Add delays between posts if processing multiple episodes

## Performance Considerations

1. **Image Generation**
   - Cache loaded templates and fonts
   - Reuse PIL Image objects where possible
   - Optimize image compression (PNG with reasonable quality)

2. **File I/O**
   - Batch read episode files if processing multiple
   - Use generators for large episode lists
   - Stream large images instead of loading entirely in memory

3. **API Calls**
   - Implement connection pooling for HTTP requests
   - Use async/await for concurrent publishing to multiple platforms
   - Cache authentication tokens

## Future Enhancements

1. **Advanced Features**
   - Video quote generation (animated text)
   - Multiple quote styles/themes
   - A/B testing different quote sources
   - Analytics integration (track engagement)

2. **Platform Support**
   - Mastodon
   - Threads
   - TikTok (video quotes)
   - YouTube Community posts

3. **Content Features**
   - Generate quote carousels (multiple images)
   - Add audio waveform visualization
   - Include guest photos
   - Generate episode highlight reels

4. **Automation**
   - Webhook integration for new episodes
   - Scheduled posting queue
   - Automatic hashtag optimization
   - Best time to post analysis
