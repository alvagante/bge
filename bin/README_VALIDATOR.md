# Frontmatter Validator

Python script to validate the YAML frontmatter structure in episode markdown files.

## Usage

### Validate a single file
```bash
python3 bin/validate_frontmatter.py _episodes/1.md
```

### Validate all episodes
```bash
python3 bin/validate_frontmatter.py _episodes
```

### Strict mode (more rigorous checks)
```bash
python3 bin/validate_frontmatter.py _episodes --strict
```

## What it validates

### Required Fields
- `number` (string) - Episode number
- `layout` (string) - Must be "episode"
- `title` (string) - Full episode title
- `titolo` (string) - Episode title without number
- `description` (string) - Full description
- `duration` (integer) - Duration in seconds (must be positive)
- `youtube` (string) - YouTube video ID (11 characters)
- `tags` (list) - Topic tags
- `date` (string) - Publication date in YYYY-MM-DD format
- `summary` (list) - Key discussion points
- `guests` (list) - Guest names
- `host` (string) - Host name
- `quote_claude` (string) - Claude AI quote
- `quote_openai` (string) - OpenAI quote
- `quote_deepseek` (string) - DeepSeek quote
- `quote_llama` (string) - Llama quote
- `quote_deepseek_reasoning` (string) - DeepSeek reasoning
- `claude_article` (string) - Claude-generated article

### Optional Fields
- `links` (string) - Additional links

## Validation Rules

1. All required fields must be present and non-empty
2. Field types must match expected types
3. Date must be in YYYY-MM-DD format
4. YouTube ID should be 11 characters (alphanumeric, dash, underscore)
5. Duration must be a positive integer
6. Layout must be "episode"
7. Arrays (tags, summary, guests) should not be empty (warning only)

## Exit Codes

- `0` - All validations passed
- `1` - One or more validations failed

## Output

- `✓` - File passed validation
- `✗` - File failed validation
- `ERROR:` - Critical validation error
- `WARNING:` - Non-critical issue

## Dependencies

- Python 3.6+
- PyYAML (install with: `pip install pyyaml`)
