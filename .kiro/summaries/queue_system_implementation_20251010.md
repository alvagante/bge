# Queue-Based Publishing System Implementation

**Date:** 2025-10-10  
**Task:** Implement queue-based publishing system for automated social media posts

## Overview

Implemented a comprehensive queue-based publishing system that allows pre-generation of social media posts with manually editable metadata and automated publishing via cron jobs.

## Components Created

### 1. Core Queue Management (`queue/queue_manager.py`)
- `QueueManager` class for managing queue and history files
- `QueueItem` dataclass for queue item structure
- `QueueStatus` enum for item states (pending, published, failed, cancelled)
- File locking with `filelock` to prevent concurrent access
- Methods for adding, removing, and updating queue items
- Separate tracking for published and failed items

### 2. Text Generation (`queue/text_generator.py`)
- `TextGenerator` class for platform-specific caption generation
- Template-based caption formatting with variable substitution
- Platform-specific character limit handling
- Hashtag generation from episode tags and platform defaults
- Hook/teaser text generation
- Episode URL generation from template

### 3. Scheduling (`queue/scheduler.py`)
- `Scheduler` class for managing scheduled times
- Default schedule times per platform (configurable)
- Staggered scheduling across multiple platforms
- Relative time parsing (+2d, +6h, etc.)
- Multiple datetime format support
- Queue item creation with all metadata

### 4. Publishing (`queue/publisher.py`)
- `QueuePublisher` class for automated publishing
- Publishes items within look-ahead window (default 5 minutes)
- Retry logic with configurable max retries
- Publisher initialization and authentication
- Success/failure tracking
- Automatic history management

### 5. CLI Commands (`queue/cli_commands.py`)
- `QueueCommands` class for CLI integration
- Commands for adding, listing, removing queue items
- History viewing (published and failed)
- Immediate publishing of specific items
- Human-readable time formatting

### 6. CLI Integration
Extended main CLI (`cli.py`) with new arguments:
- `--queue` - Add to queue instead of publishing immediately
- `--schedule` - Custom schedule time
- `--stagger` - Stagger posts across platforms
- `--queue-list` - List pending items
- `--queue-history` - View published history
- `--queue-failed` - View failed items
- `--queue-remove` - Remove item from queue
- `--queue-publish` - Publish pending items (for cron)
- `--queue-publish-now` - Publish specific item immediately
- `--history-limit` - Limit history results

### 7. Standalone Publisher Script
Created `scripts/publish_from_queue.py` for cron jobs:
- Minimal dependencies
- Proper logging
- Exit codes for cron monitoring
- Dry-run support

### 8. Configuration
Added queue settings to `config/config.yaml`:
- File paths (queue, history, lock)
- Default schedule times per platform
- Stagger settings
- Publishing behavior (retries, look-ahead)
- Text templates per platform
- Episode URL template

### 9. Documentation
Created comprehensive `QUEUE_GUIDE.md` covering:
- Quick start guide
- Command reference
- Queue file structure
- Configuration options
- Workflow examples
- Cron job setup
- Troubleshooting
- Best practices

## File Structure

```
social-quote-generator/
├── src/bge_social_quote_generator/
│   └── queue/
│       ├── __init__.py
│       ├── queue_manager.py      # Queue and history management
│       ├── text_generator.py     # Caption and text generation
│       ├── scheduler.py          # Scheduling logic
│       ├── publisher.py          # Automated publishing
│       └── cli_commands.py       # CLI command handlers
├── scripts/
│   └── publish_from_queue.py     # Standalone cron script
├── config/
│   └── config.yaml               # Updated with queue settings
├── output/
│   ├── publish_queue.json        # Queue file (auto-created)
│   ├── published_history.json    # History file (auto-created)
│   └── .publish.lock             # Lock file (auto-created)
├── QUEUE_GUIDE.md                # Comprehensive documentation
└── requirements.txt              # Added filelock dependency
```

## Key Features

### 1. Manually Editable Metadata
- Queue file is human-readable JSON
- All fields can be edited: caption, hashtags, schedule, hook, link
- Changes take effect on next publish run

### 2. Flexible Scheduling
- Default times per platform (configurable)
- Custom schedule times (absolute or relative)
- Staggered publishing across platforms
- Look-ahead window for publishing

### 3. Platform-Specific Content
- Different caption templates per platform
- Platform-specific hashtags
- Character limit handling
- Link formatting (e.g., "link in bio" for Instagram)

### 4. Robust Publishing
- File locking prevents concurrent access
- Retry logic with configurable max retries
- Separate tracking for published and failed items
- Detailed error messages

### 5. Automation Ready
- Designed for cron jobs
- Standalone script with minimal dependencies
- Proper exit codes
- Comprehensive logging

## Usage Examples

### Add to Queue
```bash
# Basic
bge-quote-gen --episode 98 --queue

# With custom schedule
bge-quote-gen --episode 98 --queue --schedule "2025-10-13 09:00"

# Staggered across platforms
bge-quote-gen --episode 98 --queue --stagger "6h"
```

### Manage Queue
```bash
# List pending
bge-quote-gen --queue-list

# View history
bge-quote-gen --queue-history

# Remove item
bge-quote-gen --queue-remove ep98_twitter_20251010_001
```

### Publish
```bash
# Automated (for cron)
bge-quote-gen --queue-publish

# Specific item
bge-quote-gen --queue-publish-now ep98_twitter_20251010_001

# Dry run
bge-quote-gen --queue-publish --dry-run
```

### Cron Setup
```bash
# Every 15 minutes
*/15 * * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/publish.log 2>&1
```

## Queue File Format

```json
{
  "version": "1.0",
  "queue": [
    {
      "id": "ep98_twitter_20251010_001",
      "episode_number": "98",
      "platform": "twitter",
      "scheduled_time": "2025-10-13T09:00:00",
      "status": "pending",
      "image_path": "social-quote-generator/output/images/bge_98_twitter_20251010_161411.png",
      "texts": {
        "caption": "🎙️ BGE Episodio 98: Titolo\n\n\"Quote...\"\n\n#BGE #DevOps\n\n🔗 https://labrigatadeigeekestinti.com/ep/98/",
        "hook": "Nuovo episodio disponibile!",
        "link": "https://labrigatadeigeekestinti.com/ep/98/",
        "hashtags": ["#BGE", "#DevOps", "#IT"]
      },
      "metadata": {
        "quote_source": "claude",
        "generated_at": "2025-10-10T16:14:11",
        "episode_title": "Titolo dell'episodio",
        "guests": ["Guest 1", "Guest 2"],
        "duration": 3600,
        "youtube_id": "abc123"
      },
      "retry_count": 0
    }
  ]
}
```

## Configuration

```yaml
queue:
  queue_file: "social-quote-generator/output/publish_queue.json"
  history_file: "social-quote-generator/output/published_history.json"
  lock_file: "social-quote-generator/output/.publish.lock"
  
  default_schedule:
    twitter: "09:00"
    instagram: "15:00"
    linkedin: "10:00"
    facebook: "12:00"
  
  stagger_interval: "6h"
  stagger_order: ["twitter", "instagram", "linkedin", "facebook"]
  
  max_retries: 3
  retry_delay: 3600
  look_ahead_minutes: 5
  
  text_templates:
    twitter:
      caption: "🎙️ BGE Episodio {episode_number}: {title}\n\n\"{quote}\"\n\n{hashtags}\n\n🔗 {link}"
      hook: "Nuovo episodio disponibile!"
    # ... more platforms
  
  episode_url_template: "https://labrigatadeigeekestinti.com/ep/{episode_number}/"
```

## Template Variables

Available in caption templates:
- `{episode_number}` - Episode number
- `{title}` - Episode title
- `{quote}` - Selected quote
- `{guests}` - Guest names
- `{date}` - Publication date
- `{youtube_url}` - YouTube URL
- `{youtube_id}` - YouTube video ID
- `{host}` - Host name
- `{link}` - Episode page URL
- `{topics}` - Episode topics
- `{hashtags}` - Generated hashtags

## Testing

To test the system:

1. **Add to queue:**
   ```bash
   bge-quote-gen --episode 1 --queue --schedule "+5m"
   ```

2. **List queue:**
   ```bash
   bge-quote-gen --queue-list
   ```

3. **Test publishing (dry run):**
   ```bash
   bge-quote-gen --queue-publish --dry-run --verbose
   ```

4. **Edit queue file:**
   ```bash
   nano social-quote-generator/output/publish_queue.json
   ```

5. **Publish:**
   ```bash
   bge-quote-gen --queue-publish
   ```

6. **Check history:**
   ```bash
   bge-quote-gen --queue-history
   ```

## Dependencies Added

- `filelock>=3.12.0` - For queue file locking

## Next Steps

1. Test with actual episodes
2. Set up cron job on production server
3. Monitor logs for first few days
4. Adjust scheduling based on engagement metrics
5. Consider adding:
   - Email notifications for failures
   - Web UI for queue management
   - Analytics integration
   - Scheduled post preview

## Notes

- Queue files are created automatically on first use
- Lock file prevents concurrent publishing
- Failed items are retried up to max_retries times
- Published items are moved to history
- All files are human-readable JSON for easy debugging
- System is designed to be robust and recoverable

