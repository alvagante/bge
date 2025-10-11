# BGE Quote Generator - Command Reference

Quick reference for the `bge-quote-gen` command.

## Installation

```bash
pip install -e social-quote-generator/
```

## Basic Commands

```bash
# Single episode, all platforms
bge-quote-gen --episode 1 --dry-run

# Single episode, specific platform
bge-quote-gen --episode 1 --platform instagram --dry-run

# Multiple episodes
bge-quote-gen --episodes 1,5,10 --dry-run

# All episodes
bge-quote-gen --all --dry-run
```

## Platforms

- `instagram` - 1080x1080 (square)
- `twitter` - 1200x675 (16:9)
- `facebook` - 1200x630 (1.91:1)
- `linkedin` - 1200x627 (1.91:1)

## Quote Sources

```bash
bge-quote-gen --episode 1 --quote-source claude --dry-run
bge-quote-gen --episode 1 --quote-source openai --dry-run
bge-quote-gen --episode 1 --quote-source deepseek --dry-run
bge-quote-gen --episode 1 --quote-source llama --dry-run
bge-quote-gen --episode 1 --quote-source random --dry-run
```

## Publishing

```bash
# Dry run (default) - generate images only
bge-quote-gen --episode 1 --dry-run

# Publish to social media (requires API credentials)
bge-quote-gen --episode 1 --publish
```

## Configuration

```bash
# Use custom config file
bge-quote-gen --episode 1 --config /path/to/config.yaml --dry-run

# Override output directory
bge-quote-gen --episode 1 --output-dir /tmp/images --dry-run
```

## Debugging

```bash
# Verbose logging
bge-quote-gen --episode 1 --verbose --dry-run

# Show help
bge-quote-gen --help

# Show version
bge-quote-gen --version
```

## Common Workflows

### Test a Single Episode

```bash
bge-quote-gen --episode 98 --platform instagram --dry-run
```

### Generate for All Platforms

```bash
bge-quote-gen --episode 98 --dry-run
```

### Compare Quote Sources

```bash
bge-quote-gen --episode 1 --quote-source claude --platform instagram --dry-run
bge-quote-gen --episode 1 --quote-source openai --platform instagram --dry-run
bge-quote-gen --episode 1 --quote-source deepseek --platform instagram --dry-run
bge-quote-gen --episode 1 --quote-source llama --platform instagram --dry-run
```

### Batch Process Multiple Episodes

```bash
bge-quote-gen --episodes 95,96,97,98 --platform twitter --dry-run
```

### Publish to Twitter

```bash
# 1. Configure credentials in .env
# 2. Generate and publish
bge-quote-gen --episode 98 --platform twitter --publish
```

## Output

Generated images are saved to:
```
social-quote-generator/output/images/
```

Naming format:
```
bge_{episode}_{platform}_{timestamp}.png
```

Example:
```
bge_1_instagram_20251010_081320.png
```

## Config File Locations

The tool automatically searches for config files in:
1. Current working directory
2. `social-quote-generator/config/config.yaml`
3. Package installation directory

Default: `config/config.yaml`

## Exit Codes

- `0` - Success
- `1` - Error (invalid arguments, config error, processing failure)
- `130` - Cancelled by user (Ctrl+C)

## Tips

1. Always test with `--dry-run` first
2. Use `--verbose` for troubleshooting
3. Check output directory to verify images
4. Run from any directory - config is found automatically
5. Use `--platform` to target specific social media
6. Customize templates in `templates/` directory
7. Review config.yaml for branding and layout options
