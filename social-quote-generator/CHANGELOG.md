# Changelog

All notable changes to the BGE Social Quote Generator project.

## [1.1.0] - 2025-10-10

### Added
- **Queue-Based Publishing System**: Complete queue management for scheduled social media posts
  - Add episodes to queue with customizable schedules
  - Manually editable metadata (captions, hashtags, links, schedule times)
  - Automated publishing via cron jobs
  - Staggered scheduling across multiple platforms
  - Retry logic for failed posts
  - Published and failed history tracking
  - File locking to prevent concurrent access
  
- **New CLI Commands**:
  - `--queue` - Add generated images to publishing queue
  - `--schedule` - Set custom schedule time
  - `--stagger` - Stagger posts across platforms
  - `--queue-list` - List pending queue items
  - `--queue-history` - View published items
  - `--queue-failed` - View failed items
  - `--queue-remove` - Remove item from queue
  - `--queue-publish` - Publish pending items (for cron)
  - `--queue-publish-now` - Publish specific item immediately
  - `--history-limit` - Limit history results

- **New Components**:
  - `QueueManager` - Queue and history file management
  - `TextGenerator` - Platform-specific caption generation
  - `Scheduler` - Scheduling logic and time parsing
  - `QueuePublisher` - Automated publishing from queue
  - `QueueCommands` - CLI command handlers

- **Configuration**:
  - Queue settings in `config.yaml`
  - Default schedule times per platform
  - Stagger interval and order
  - Max retries and look-ahead window
  - Platform-specific text templates
  - Episode URL template

- **Documentation**:
  - `QUEUE_GUIDE.md` - Comprehensive queue system guide
  - `QUEUE_QUICK_REFERENCE.md` - Quick reference card
  - Updated `QUICK_START.md` with queue examples

- **Scripts**:
  - `scripts/publish_from_queue.py` - Standalone publisher for cron
  - `scripts/setup_cron.sh` - Interactive cron setup helper

### Changed
- Added `filelock>=3.12.0` dependency for queue file locking
- Updated CLI to support queue management commands
- Enhanced configuration with queue-specific settings

### Technical Details
- Queue files stored as human-readable JSON
- File locking prevents concurrent publishing
- Retry logic with configurable max attempts
- Template-based caption generation with variable substitution
- Platform-specific character limit handling
- Relative and absolute time parsing for schedules

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
