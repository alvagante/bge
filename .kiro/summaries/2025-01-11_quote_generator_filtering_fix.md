# Quote Generator Filtering Fix

**Date:** 2025-01-11  
**Task:** Fix bge-quote-gen filtering logic for --quote-source and --platform options

## Problem

The `bge-quote-gen` command was not correctly filtering images based on command-line options:

- `bge-quote-gen --episode 1 --quote-source claude` generated 16 images instead of 4
- Expected behavior was not matching the actual output

## Root Cause

1. The config file had `preferred_source: "claude"` as default, which was always filtering to Claude quotes
2. The orchestrator was not respecting the `preferred_source` setting when generating images
3. The validator didn't allow `null` as a valid value for `preferred_source`

## Solution

### 1. Updated Config Files
Changed default `preferred_source` from `"claude"` to `null` in:
- `social-quote-generator/config/config.yaml`
- `social-quote-generator/config/config.example.yaml`

This allows generating all quotes by default.

### 2. Updated Orchestrator Logic
Modified `social-quote-generator/src/bge_social_quote_generator/orchestrator.py`:
- Added filtering logic in `_process_episode()` method
- Filters quotes based on `config.quote_settings.preferred_source`
- If `preferred_source` is `null` or `'random'`, all quotes are generated
- If a specific source is set, only that source's quotes are generated

### 3. Updated Validators
Modified `social-quote-generator/src/bge_social_quote_generator/utils/validators.py` and `config.py`:
- `validate_source()` now accepts `None` as valid (means "all sources")
- Updated validation logic to allow `null` in config files

## Expected Behavior (Now Working)

### Command: `bge-quote-gen --episode 1`
- **Output:** 16 images (4 quote sources × 4 platforms)
- All quotes from all sources for all platforms

### Command: `bge-quote-gen --episode 1 --quote-source claude`
- **Output:** 4 images (1 quote source × 4 platforms)
- Only Claude quotes for all platforms

### Command: `bge-quote-gen --episode 1 --platform linkedin`
- **Output:** 4 images (4 quote sources × 1 platform)
- All quotes from all sources for LinkedIn only

### Command: `bge-quote-gen --episode 1 --platform linkedin --quote-source claude`
- **Output:** 1 image (1 quote source × 1 platform)
- Only Claude quote for LinkedIn

## Testing Results

All scenarios tested and working correctly:
```bash
✓ bge-quote-gen --episode 1 --dry-run → 16 images
✓ bge-quote-gen --episode 1 --quote-source claude --dry-run → 4 images
✓ bge-quote-gen --episode 1 --platform linkedin --dry-run → 4 images
```

## Files Modified

1. `social-quote-generator/src/bge_social_quote_generator/orchestrator.py`
2. `social-quote-generator/src/bge_social_quote_generator/utils/validators.py`
3. `social-quote-generator/src/bge_social_quote_generator/config.py`
4. `social-quote-generator/config/config.yaml`
5. `social-quote-generator/config/config.example.yaml`
6. `social-quote-generator/COMMAND_REFERENCE.md` (documentation update)

## Impact

Users can now:
- Generate all quotes by default (no filtering)
- Filter to specific quote sources with `--quote-source`
- Filter to specific platforms with `--platform`
- Combine both filters for precise control
- Set `preferred_source: null` in config for default "all sources" behavior
