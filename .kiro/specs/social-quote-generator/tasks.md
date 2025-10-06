# Implementation Plan

- [x] 1. Set up project structure and core configuration
  - Create directory structure with src/, config/, templates/, output/, and tests/ folders
  - Create requirements.txt with all necessary dependencies (Pillow, PyYAML, python-frontmatter, tweepy, instagrapi, python-dotenv, tenacity)
  - Create setup.py for package installation
  - Create .gitignore to exclude .env, output/, and __pycache__
  - _Requirements: 7.1, 7.2, 7.5_

- [x] 2. Implement configuration management system
  - Create config/config.example.yaml with all configuration options (general, quotes, images, social_media sections)
  - Implement Config class in src/config.py to load and parse YAML configuration
  - Add environment variable substitution for API credentials using python-dotenv
  - Implement configuration validation to check required fields and valid values
  - Create dataclasses for ImageSettings, SocialMediaSettings, and QuoteSettings
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 3. Implement quote extraction module
  - Create EpisodeQuote dataclass in src/extractors/base.py with all episode metadata fields
  - Implement QuoteExtractor class in src/extractors/quote_extractor.py
  - Add method to parse YAML frontmatter from episode markdown files using python-frontmatter
  - Implement quote source selection logic based on configuration preferences (claude, openai, deepseek, llama, random)
  - Add fallback mechanism to load quotes from separate text files in assets/texts/
  - Implement error handling for missing or malformed episode files
  - Add methods to extract single episode or all episodes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 4. Implement image generation module
  - Create GeneratedImage dataclass in src/generators/base.py
  - Implement ImageGenerator class in src/generators/image_generator.py using Pillow
  - Add method to load or create background templates for different platforms
  - Implement text wrapping algorithm to fit quotes within max width
  - Add method to render centered quote text with proper font and color
  - Implement logo overlay with transparency and configurable positioning
  - Add method to render episode metadata (episode number, guests) at bottom
  - Implement image saving with naming convention: bge_{episode_number}_{platform}_{timestamp}.png
  - Add support for Italian characters and special symbols
  - Implement dynamic font size adjustment for long quotes
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ] 5. Implement base publisher interface and Twitter publisher
  - Create BasePublisher abstract class in src/publishers/base.py with authenticate() and publish() methods
  - Create PublishResult dataclass for publish operation results
  - Implement caption generation from template with episode data substitution
  - Implement hashtag generation from episode tags
  - Implement TwitterPublisher class using tweepy library
  - Add Twitter authentication using API credentials from configuration
  - Implement image upload and tweet creation with caption
  - Add error handling for authentication failures and API errors
  - Implement retry logic with exponential backoff using tenacity
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [ ] 6. Implement additional social media publishers
  - Implement InstagramPublisher class using instagrapi library
  - Add Instagram authentication and photo upload with caption
  - Implement FacebookPublisher class using facebook-sdk library
  - Add Facebook authentication and photo posting
  - Implement LinkedInPublisher class for LinkedIn posting
  - Add platform-specific error handling and retry logic for each publisher
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.8_

- [ ] 7. Implement pipeline orchestrator
  - Create PipelineResult dataclass in src/orchestrator.py
  - Implement PipelineOrchestrator class to coordinate extraction, generation, and publishing
  - Add method to initialize enabled publishers based on configuration
  - Implement episode processing logic: extract → generate → publish
  - Add support for processing single episode, multiple episodes, or all episodes
  - Implement platform filtering to generate images only for specified platforms
  - Add dry-run mode that generates images without publishing
  - Implement error collection and summary reporting
  - Add logging for each pipeline stage
  - _Requirements: 6.1, 6.2, 6.3, 6.6_

- [ ] 8. Implement logging and error handling utilities
  - Create logger configuration in src/utils/logger.py with console and file handlers
  - Implement log level support (DEBUG, INFO, WARNING, ERROR)
  - Create ErrorHandler class to collect and categorize errors
  - Add error handling for configuration, extraction, generation, and publishing errors
  - Implement graceful error recovery to continue processing after non-fatal errors
  - Add summary reporting for processed episodes, generated images, and published posts
  - Implement early validation for API credentials with clear error messages
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ] 9. Implement CLI interface
  - Create main.py with argparse-based CLI
  - Add --episode/-e argument for single episode processing
  - Add --episodes argument for multiple episodes (comma-separated)
  - Add --all/-a flag to process all episodes
  - Add --platform/-p argument to specify target platform
  - Add --publish flag to enable social media publishing
  - Add --dry-run flag to generate images without publishing
  - Add --config/-c argument for custom configuration file path
  - Add --output-dir/-o argument to override output directory
  - Add --quote-source argument to specify preferred quote source
  - Add --verbose/-v flag for detailed logging
  - Implement help documentation for all arguments
  - Add configuration loading and orchestrator initialization
  - Implement results display with summary statistics
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_

- [ ] 10. Create default templates and assets
  - Create default square template (1080x1080) for Instagram in templates/default_square.png
  - Create default landscape template (1200x675) for Twitter in templates/default_landscape.png
  - Download and include Open Sans font or similar open-source font in templates/fonts/
  - Create sample .env.example file with placeholder API credentials
  - _Requirements: 2.7, 4.7_

- [ ] 11. Write comprehensive README documentation
  - Write installation instructions with virtual environment setup
  - Document API credential setup for each platform (Twitter, Instagram, Facebook, LinkedIn)
  - Provide configuration guide with explanation of all config options
  - Add usage examples for common scenarios (single episode, all episodes, specific platform, dry-run)
  - Document template customization process
  - Add troubleshooting section for common issues
  - Include automation examples (cron jobs, scheduled tasks)
  - Add security best practices for credential management
  - _Requirements: 7.4_

- [ ] 12. Implement input validation and security measures
  - Create validators.py with input validation functions
  - Add episode number validation (numeric, positive, exists)
  - Implement file path validation to prevent directory traversal
  - Add configuration value validation (dimensions, colors, file paths)
  - Implement text sanitization before rendering to images
  - Add API credential validation on startup
  - Implement rate limiting checks before publishing
  - _Requirements: 6.7_

- [ ]* 13. Write unit tests for core components
  - Write tests for Config class (loading, validation, environment variables)
  - Write tests for QuoteExtractor (parsing, quote selection, fallback logic)
  - Write tests for ImageGenerator (text wrapping, image creation, logo placement)
  - Write tests for caption and hashtag generation
  - Mock API calls and write tests for publisher error handling
  - Write tests for retry logic and exponential backoff
  - Write tests for CLI argument parsing
  - _Requirements: 6.1, 6.2_

- [ ]* 14. Write integration tests
  - Create test fixtures with sample episode files and expected outputs
  - Write end-to-end pipeline test with sample episode
  - Test dry-run mode execution
  - Test error recovery with malformed episode data
  - Test file system operations (reading episodes, writing images, creating logs)
  - Test configuration override via CLI arguments
  - _Requirements: 6.3_

- [ ] 15. Final integration and polish
  - Test complete workflow: extract → generate → publish for sample episode
  - Verify all CLI arguments work correctly
  - Test with actual BGE episode data
  - Verify image quality and text rendering for different quote lengths
  - Test error handling with missing files and invalid credentials
  - Verify logging output is clear and helpful
  - Test on different platforms (macOS, Linux, Windows if possible)
  - Create example output images for documentation
  - _Requirements: All_
