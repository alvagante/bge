# Queue System - Quick Reference Card

## Add to Queue

```bash
# Basic (default schedule)
bge-quote-gen --episode N --queue

# Custom schedule
bge-quote-gen --episode N --queue --schedule "2025-10-13 09:00"

# Relative schedule
bge-quote-gen --episode N --queue --schedule "+2d"    # 2 days from now
bge-quote-gen --episode N --queue --schedule "+6h"    # 6 hours from now

# Staggered (6h between platforms)
bge-quote-gen --episode N --queue --stagger "6h"

# Specific platform
bge-quote-gen --episode N --platform twitter --queue

# Multiple episodes
bge-quote-gen --episodes 95,96,97,98 --queue --stagger "6h"
```

## View Queue

```bash
# List pending items
bge-quote-gen --queue-list

# View published history
bge-quote-gen --queue-history

# View last 20 published
bge-quote-gen --queue-history --history-limit 20

# View failed items
bge-quote-gen --queue-failed
```

## Manage Queue

```bash
# Remove item
bge-quote-gen --queue-remove ITEM_ID

# Edit queue file manually
nano social-quote-generator/output/publish_queue.json
```

## Publish

```bash
# Publish pending items (for cron)
bge-quote-gen --queue-publish

# Dry run (test)
bge-quote-gen --queue-publish --dry-run

# Publish specific item now
bge-quote-gen --queue-publish-now ITEM_ID

# Verbose logging
bge-quote-gen --queue-publish --verbose
```

## Cron Setup

```bash
# Edit crontab
crontab -e

# Run every 15 minutes
*/15 * * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/publish.log 2>&1

# Run at specific times (9 AM, 3 PM, 9 PM)
0 9,15,21 * * * cd /path/to/bge.github.io && /path/to/venv/bin/bge-quote-gen --queue-publish >> /path/to/logs/publish.log 2>&1
```

## Queue Files

```
social-quote-generator/output/
├── publish_queue.json        # Pending items
├── published_history.json    # Published & failed items
└── .publish.lock            # Lock file (auto-managed)
```

## Editable Fields in Queue

Edit `publish_queue.json` to customize:

- `scheduled_time` - When to publish
- `texts.caption` - Post caption
- `texts.hashtags` - Hashtag list
- `texts.hook` - Hook/teaser text
- `texts.link` - Episode URL

## Template Variables

Available in caption templates:

- `{episode_number}` - Episode number
- `{title}` - Episode title
- `{quote}` - Quote text
- `{guests}` - Guest names
- `{link}` - Episode URL
- `{hashtags}` - Hashtags
- `{youtube_url}` - YouTube URL
- `{topics}` - Episode topics

## Troubleshooting

```bash
# Check pending items
bge-quote-gen --queue-list

# Check failed items
bge-quote-gen --queue-failed

# Test with dry run
bge-quote-gen --queue-publish --dry-run --verbose

# Remove stale lock file
rm social-quote-generator/output/.publish.lock

# View logs
tail -f /path/to/logs/publish.log
```

## Workflow

1. **Generate & Queue**
   ```bash
   bge-quote-gen --episode 98 --queue --stagger "6h"
   ```

2. **Review**
   ```bash
   bge-quote-gen --queue-list
   ```

3. **Edit (optional)**
   ```bash
   nano social-quote-generator/output/publish_queue.json
   ```

4. **Test**
   ```bash
   bge-quote-gen --queue-publish --dry-run
   ```

5. **Publish** (automated via cron or manual)
   ```bash
   bge-quote-gen --queue-publish
   ```

6. **Monitor**
   ```bash
   bge-quote-gen --queue-history
   ```

---

**Full Documentation:** See `QUEUE_GUIDE.md`
