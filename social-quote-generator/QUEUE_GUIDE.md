# Queue-Based Publishing Guide

This guide explains how to use the queue-based publishing system for scheduling social media posts.

## Overview

The queue system allows you to:
- Pre-generate images and metadata for social media posts
- Schedule posts for specific times
- Manually edit captions, hashtags, and other text before publishing
- Automate publishing via cron jobs
- Track published and failed posts

## Quick Start

### 1. Generate and Add to Queue

```bash
# Add episode 98 to queue with default schedule (tomorrow at platform-specific times)
bge-quote-gen --episode 98 --queue

# Add with custom schedule
bge-quote-gen --episode 98 --queue --schedule "2025-10-13 09:00"

# Add with staggered schedule (6 hours between each platform)
bge-quote-gen --episode 98 --queue --stagger "6h"

# Add specific platform only
bge-quote-gen --episode 98 --platform twitter --queue --schedule "2025-10-13 09:00"
```

### 2. Review Queue

```bash
# List all pending items
bge-quote-gen --queue-list
```

### 3. Edit Metadata (Optional)

The queue file is human-readable JSON. You can edit it directly:

```bash
# Edit queue file
nano social-quote-generator/output/publish_queue.json
```

Edit any field:
- `scheduled_time`: Change publish time
- `texts.caption`: Modify caption text
- `texts.hashtags`: Add/remove hashtags
- `texts.hook`: Change hook text
- `texts.link`: Modify episode link

### 4. Automated Publishing

Set up a cron job to publish automatically:

```bash
# Edit crontab
crontab -e

# Add entry to run every 15 minutes
*/15 * * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/publish.log 2>&1

# Or use the standalone script
*/15 * * * * cd /path/to/bge.github.io && /path/to/venv/bin/python social-quote-generator/scripts/publish_from_queue.py >> /path/to/logs/publish.log 2>&1
```

### 5. Monitor Results

```bash
# View published history
bge-quote-gen --queue-history

# View last 20 published items
bge-quote-gen --queue-history --history-limit 20

# View failed items
bge-quote-gen --queue-failed
```

## Command Reference

### Queue Management

#### Add to Queue

```bash
# Basic usage
bge-quote-gen --episode N --queue

# With custom schedule
bge-quote-gen --episode N --queue --schedule "YYYY-MM-DD HH:MM"

# With relative schedule
bge-quote-gen --episode N --queue --schedule "+2d"  # 2 days from now
bge-quote-gen --episode N --queue --schedule "+6h"  # 6 hours from now

# With staggered schedule
bge-quote-gen --episode N --queue --stagger "6h"    # 6 hours between platforms
bge-quote-gen --episode N --queue --stagger "30m"   # 30 minutes between platforms
bge-quote-gen --episode N --queue --stagger "1d"    # 1 day between platforms

# Specific platform
bge-quote-gen --episode N --platform twitter --queue --schedule "2025-10-13 09:00"

# Multiple episodes
bge-quote-gen --episodes 95,96,97,98 --queue --stagger "6h"
```

#### List Queue

```bash
# List all pending items
bge-quote-gen --queue-list
```

Output shows:
- Item ID
- Episode number and platform
- Scheduled time
- Time until scheduled
- Image path
- Caption preview
- Status and retry count

#### View History

```bash
# View published items (last 10)
bge-quote-gen --queue-history

# View more items
bge-quote-gen --queue-history --history-limit 50

# View failed items
bge-queue-gen --queue-failed
```

#### Remove from Queue

```bash
# Remove specific item
bge-quote-gen --queue-remove ITEM_ID

# Example
bge-quote-gen --queue-remove ep98_twitter_20251010_001
```

#### Publish from Queue

```bash
# Publish pending items (for cron jobs)
bge-quote-gen --queue-publish

# Dry run (test without publishing)
bge-quote-gen --queue-publish --dry-run

# Publish specific item immediately
bge-quote-gen --queue-publish-now ITEM_ID

# Example
bge-quote-gen --queue-publish-now ep98_twitter_20251010_001
```

## Queue File Structure

### Queue File (`publish_queue.json`)

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

### History File (`published_history.json`)

```json
{
  "version": "1.0",
  "published": [
    {
      "id": "ep97_twitter_20251009_001",
      "episode_number": "97",
      "platform": "twitter",
      "scheduled_time": "2025-10-10T09:00:00",
      "published_at": "2025-10-10T09:00:15",
      "status": "published",
      "post_url": "https://twitter.com/username/status/1234567890",
      "image_path": "...",
      "texts": {...},
      "metadata": {...}
    }
  ],
  "failed": [
    {
      "id": "ep96_instagram_20251008_002",
      "episode_number": "96",
      "platform": "instagram",
      "scheduled_time": "2025-10-09T15:00:00",
      "status": "failed",
      "error": "Authentication failed",
      "retry_count": 3,
      "image_path": "...",
      "texts": {...},
      "metadata": {...}
    }
  ]
}
```

## Configuration

Queue settings in `config/config.yaml`:

```yaml
queue:
  # File paths
  queue_file: "social-quote-generator/output/publish_queue.json"
  history_file: "social-quote-generator/output/published_history.json"
  lock_file: "social-quote-generator/output/.publish.lock"
  
  # Default scheduling (time of day for each platform)
  default_schedule:
    twitter: "09:00"      # 9 AM
    instagram: "15:00"    # 3 PM
    linkedin: "10:00"     # 10 AM
    facebook: "12:00"     # 12 PM
  
  # Stagger settings
  stagger_interval: "6h"
  stagger_order: ["twitter", "instagram", "linkedin", "facebook"]
  
  # Publishing behavior
  max_retries: 3
  retry_delay: 3600  # 1 hour
  look_ahead_minutes: 5  # Publish if within 5 minutes of scheduled time
  
  # Text templates (per platform)
  text_templates:
    twitter:
      caption: "🎙️ BGE Episodio {episode_number}: {title}\n\n\"{quote}\"\n\n{hashtags}\n\n🔗 {link}"
      hook: "Nuovo episodio disponibile!"
    instagram:
      caption: "🎙️ BGE Episodio {episode_number}\n\n\"{quote}\"\n\nLink in bio!\n\n{hashtags}"
      hook: "Nuovo episodio del podcast!"
    # ... more platforms
  
  # Episode URL template
  episode_url_template: "https://labrigatadeigeekestinti.com/ep/{episode_number}/"
```

## Workflow Examples

### Example 1: Weekly Batch Publishing

```bash
# Monday: Generate posts for episodes 95-98
bge-quote-gen --episodes 95,96,97,98 --queue --stagger "1d"

# Review and edit queue
bge-quote-gen --queue-list
nano social-quote-generator/output/publish_queue.json

# Cron job publishes automatically throughout the week
```

### Example 2: Platform-Specific Timing

```bash
# Twitter at 9 AM
bge-quote-gen --episode 98 --platform twitter --queue --schedule "2025-10-13 09:00"

# Instagram at 3 PM same day
bge-quote-gen --episode 98 --platform instagram --queue --schedule "2025-10-13 15:00"

# LinkedIn next day at 10 AM
bge-quote-gen --episode 98 --platform linkedin --queue --schedule "2025-10-14 10:00"
```

### Example 3: Test Before Publishing

```bash
# Add to queue
bge-quote-gen --episode 98 --queue

# Test publishing (dry run)
bge-quote-gen --queue-publish --dry-run

# Actually publish
bge-quote-gen --queue-publish
```

## Cron Job Setup

### Basic Setup

```bash
# Edit crontab
crontab -e

# Run every 15 minutes
*/15 * * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/publish.log 2>&1
```

### Advanced Setup with Logging

```bash
# Create log directory
mkdir -p /path/to/logs

# Crontab entry with date-stamped logs
*/15 * * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/publish_$(date +\%Y\%m\%d).log 2>&1
```

### Multiple Times Per Day

```bash
# Run at 9 AM, 3 PM, and 9 PM
0 9,15,21 * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/publish.log 2>&1
```

### Platform-Specific Cron Jobs

```bash
# Twitter at 9 AM daily
0 9 * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/twitter_publish.log 2>&1

# Instagram at 3 PM daily
0 15 * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/instagram_publish.log 2>&1
```

## Troubleshooting

### Queue Not Publishing

1. Check pending items:
   ```bash
   bge-quote-gen --queue-list
   ```

2. Verify scheduled times are in the past or within look-ahead window

3. Check failed items:
   ```bash
   bge-quote-gen --queue-failed
   ```

4. Test with dry run:
   ```bash
   bge-quote-gen --queue-publish --dry-run --verbose
   ```

### Items Stuck in Queue

Items may fail to publish due to:
- Invalid credentials
- Network issues
- API rate limits
- Invalid image paths

Check error messages in failed history:
```bash
bge-quote-gen --queue-failed
```

Remove problematic items:
```bash
bge-quote-gen --queue-remove ITEM_ID
```

### Cron Job Not Running

1. Check cron is running:
   ```bash
   ps aux | grep cron
   ```

2. Check cron logs:
   ```bash
   tail -f /var/log/syslog | grep CRON  # Linux
   tail -f /var/log/system.log | grep cron  # macOS
   ```

3. Verify paths in crontab are absolute

4. Test command manually:
   ```bash
   cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish --verbose
   ```

### Lock File Issues

If publishing seems stuck, check for stale lock file:

```bash
# Check lock file
ls -la social-quote-generator/output/.publish.lock

# Remove if stale (no process running)
rm social-quote-generator/output/.publish.lock
```

## Best Practices

1. **Always test with dry-run first**
   ```bash
   bge-quote-gen --episode 98 --queue
   bge-quote-gen --queue-publish --dry-run
   ```

2. **Review queue before publishing**
   ```bash
   bge-quote-gen --queue-list
   ```

3. **Edit captions for platform-specific optimization**
   - Twitter: Keep under 280 characters
   - Instagram: Use more hashtags, mention "link in bio"
   - LinkedIn: More professional tone
   - Facebook: Longer descriptions work well

4. **Monitor published history regularly**
   ```bash
   bge-quote-gen --queue-history
   ```

5. **Set up cron job logging**
   - Helps debug issues
   - Track publishing activity
   - Monitor for failures

6. **Use staggered scheduling**
   - Avoids overwhelming followers
   - Maximizes reach across time zones
   - Platform-specific optimal times

7. **Backup queue files**
   ```bash
   cp social-quote-generator/output/publish_queue.json social-quote-generator/output/publish_queue.backup.json
   ```

## Template Variables

Available variables for caption templates:

- `{episode_number}` - Episode number
- `{title}` - Episode title (titolo)
- `{quote}` - Selected quote
- `{guests}` - Comma-separated guest names
- `{date}` - Publication date
- `{youtube_url}` - Full YouTube URL
- `{youtube_id}` - YouTube video ID
- `{host}` - Host name
- `{link}` - Episode page URL
- `{topics}` - First 3 topics from summary
- `{hashtags}` - Generated hashtags

## Support

For issues or questions:
1. Check this guide
2. Review `QUICK_START.md` for basic usage
3. Check `PUBLISHERS.md` for platform-specific setup
4. Review logs with `--verbose` flag

