# Utilities Guide

This guide explains how to use the logging, error handling, validation, and reporting utilities in the Social Quote Generator.

## Quick Start

The easiest way to set up all utilities is with the `setup_pipeline_utilities()` helper:

```python
from src.utils import setup_pipeline_utilities

# Initialize all utilities at once
logger, error_handler, reporter, validator = setup_pipeline_utilities(
    log_level='INFO',
    log_dir='output/logs',
    console_output=True,
    file_output=True
)
```

## Logging

### Basic Usage

```python
from src.utils import get_logger

logger = get_logger(log_level='INFO')

logger.debug('Detailed debugging information')
logger.info('General information')
logger.warning('Warning message')
logger.error('Error occurred')
logger.critical('Critical error')
```

### Configuration Options

```python
logger = get_logger(
    name='my_module',           # Logger name
    log_dir='output/logs',      # Log file directory
    log_level='DEBUG',          # DEBUG, INFO, WARNING, ERROR, CRITICAL
    console_output=True,        # Enable console logging
    file_output=True            # Enable file logging
)
```

## Error Handling

### Recording Errors

```python
from src.utils import ErrorHandler, ErrorSeverity

error_handler = ErrorHandler(logger)

# Configuration errors
error_handler.handle_configuration_error(
    message='Invalid configuration value',
    severity=ErrorSeverity.ERROR
)

# Extraction errors
error_handler.handle_extraction_error(
    episode_number='42',
    message='Quote not found',
    exception=e,  # Optional exception object
    context={'source': 'claude'}  # Optional context
)

# Generation errors
error_handler.handle_generation_error(
    episode_number='42',
    platform='instagram',
    message='Template not found'
)

# Publishing errors
error_handler.handle_publishing_error(
    episode_number='42',
    platform='twitter',
    message='API rate limit exceeded'
)

# Authentication errors (automatically marked as FATAL)
error_handler.handle_authentication_error(
    platform='twitter',
    message='Invalid API credentials'
)
```

### Checking for Errors

```python
if error_handler.has_errors():
    print(f"Total errors: {error_handler.get_error_count()}")

if error_handler.has_fatal_errors():
    print("Fatal errors occurred - stopping execution")
    exit(1)
```

### Error Summaries

```python
# Print human-readable summary
error_handler.print_summary()

# Get structured summary
summary = error_handler.get_summary()
print(f"Total errors: {summary['total_errors']}")
print(f"By category: {summary['by_category']}")
print(f"By severity: {summary['by_severity']}")
```

## Summary Reporting

### Tracking Execution

```python
from src.utils import SummaryReporter, create_episode_result

reporter = SummaryReporter(logger)

# Start tracking
reporter.start_execution()

# Record operations
reporter.record_image_generated('42', 'instagram')
reporter.record_post_published('42', 'twitter', 'https://twitter.com/...')

# Add episode results
result = create_episode_result(
    episode_number='42',
    success=True,
    images_generated=2,
    posts_published=1,
    platforms=['instagram', 'twitter']
)
reporter.add_episode_result(result)

# End tracking
reporter.end_execution()
```

### Displaying Summaries

```python
# Quick summary (brief)
reporter.print_quick_summary()

# Full summary (detailed)
reporter.print_summary()

# Get structured data
summary = reporter.get_summary()
print(f"Duration: {summary.duration_seconds}s")
print(f"Success rate: {summary.successful_episodes / summary.total_episodes_processed * 100}%")
```

## Validation

### Episode Numbers

```python
from src.utils import Validator, ValidationError

validator = Validator(logger)

try:
    validator.validate_episode_number('42')
    print("Valid episode number")
except ValidationError as e:
    print(f"Invalid: {e}")
```

### File Paths

```python
try:
    # Check if file exists
    validator.validate_file_path('config.yaml', must_exist=True)
    
    # Just validate format
    validator.validate_file_path('output/image.png', must_exist=False)
except ValidationError as e:
    print(f"Invalid path: {e}")
```

### Directories

```python
try:
    # Create directory if missing
    validator.validate_directory_path('output/images', create_if_missing=True)
except ValidationError as e:
    print(f"Invalid directory: {e}")
```

### Image Dimensions

```python
try:
    validator.validate_image_dimensions(1080, 1080)
except ValidationError as e:
    print(f"Invalid dimensions: {e}")
```

### Colors

```python
try:
    validator.validate_color('#FFFFFF')  # Valid
    validator.validate_color('#FFF')     # Valid
    validator.validate_color('white')    # Invalid - raises ValidationError
except ValidationError as e:
    print(f"Invalid color: {e}")
```

### API Credentials

```python
twitter_config = {
    'api_key': 'your_key',
    'api_secret': 'your_secret',
    'access_token': 'your_token',
    'access_token_secret': 'your_token_secret'
}

is_valid, error_msg = validator.validate_api_credentials('twitter', twitter_config)
if not is_valid:
    print(f"Invalid credentials: {error_msg}")
```

### Text Sanitization

```python
# Remove control characters and normalize whitespace
clean_text = validator.sanitize_text("Hello\x00World\n\nTest")
print(clean_text)  # "Hello World Test"
```

## Helper Functions

### Configuration Validation

```python
from src.utils import validate_configuration

config = {
    'general': {
        'log_level': 'INFO',
        'output_dir': 'output/images'
    },
    'images': {
        'branding': {
            'primary_color': '#FFFFFF'
        }
    }
}

is_valid = validate_configuration(config, validator, error_handler)
if not is_valid:
    print("Configuration has errors")
    error_handler.print_summary()
```

### Platform Credentials Validation

```python
from src.utils import validate_platform_credentials

is_valid = validate_platform_credentials(
    platform='twitter',
    config=twitter_config,
    validator=validator,
    error_handler=error_handler
)
```

### Output Directories

```python
from src.utils import ensure_output_directories

ensure_output_directories('output/images', 'output/logs', logger)
```

### Duration Formatting

```python
from src.utils import format_duration

print(format_duration(5.5))      # "5.50s"
print(format_duration(65.3))     # "1m 5s"
print(format_duration(3725.8))   # "1h 2m"
```

## Complete Example

```python
from src.utils import (
    setup_pipeline_utilities,
    validate_configuration,
    create_episode_result,
    ErrorSeverity
)

# 1. Initialize utilities
logger, error_handler, reporter, validator = setup_pipeline_utilities(
    log_level='INFO',
    log_dir='output/logs'
)

# 2. Validate configuration
config = load_config()
if not validate_configuration(config, validator, error_handler):
    logger.error("Configuration validation failed")
    error_handler.print_summary()
    exit(1)

# 3. Start execution tracking
reporter.start_execution()

# 4. Process episodes
for episode_num in ['1', '2', '3']:
    try:
        # Validate episode number
        validator.validate_episode_number(episode_num)
        
        # Process episode...
        logger.info(f"Processing episode {episode_num}")
        
        # Record success
        result = create_episode_result(
            episode_number=episode_num,
            success=True,
            images_generated=2,
            posts_published=1
        )
        reporter.add_episode_result(result)
        
    except ValidationError as e:
        error_handler.handle_validation_error(
            message=f"Invalid episode: {episode_num}",
            exception=e,
            severity=ErrorSeverity.WARNING
        )
    except Exception as e:
        error_handler.handle_extraction_error(
            episode_number=episode_num,
            message=str(e),
            exception=e
        )

# 5. End execution and report
reporter.end_execution()
reporter.print_summary()
error_handler.print_summary()

# 6. Exit with appropriate code
exit(1 if error_handler.has_fatal_errors() else 0)
```

## Best Practices

1. **Always initialize utilities at the start** of your script
2. **Use try-except blocks** around validation calls
3. **Record all errors** even if you handle them
4. **Check for fatal errors** before continuing critical operations
5. **Print summaries** at the end of execution
6. **Use appropriate severity levels** for different error types
7. **Provide context** when recording errors
8. **Validate early** to catch errors before processing begins
9. **Use helpers** for common patterns to reduce boilerplate
10. **Log at appropriate levels** (DEBUG for details, INFO for progress, ERROR for problems)

## Error Severity Guidelines

- **FATAL**: Stops execution (authentication failures, missing critical files)
- **ERROR**: Logged but execution continues (failed to process one episode)
- **WARNING**: Minor issues (using fallback values, optional features unavailable)
- **INFO**: Informational messages (validation passed, using default values)
