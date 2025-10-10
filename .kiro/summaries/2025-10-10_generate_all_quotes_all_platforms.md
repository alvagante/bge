# Generate All Quotes for All Platforms

**Date:** 2025-10-10  
**Task:** Update quote generator to generate all 16 images (4 quotes × 4 platforms) by default

## Changes Made

### 1. Updated Filename Convention

**New Format:** `bge_{episode_number}_{author}_{platform}_{timestamp}.png`

Example: `bge_13_claude_instagram_20251010_143022.png`

**Modified Files:**
- `image_generator.py::_save_image()` - Added `quote_source` parameter to filename

### 2. Added Multi-Quote Extraction

**New Method:** `QuoteExtractor.extract_all_quotes_for_episode()`

This method extracts all 4 quotes (claude, openai, deepseek, llama) for a given episode instead of just one based on preference.

**Modified Files:**
- `quote_extractor.py` - Added new method to extract all quotes from all sources

### 3. Updated Orchestrator to Generate All Images

**Modified:** `PipelineOrchestrator._process_episode()`

The orchestrator now:
1. Extracts all 4 quotes for the episode
2. Generates images for each quote × each platform
3. Results in 16 images per episode (4 quotes × 4 platforms)

**Modified Files:**
- `orchestrator.py::_process_episode()` - Loop through all quotes and all platforms

## Behavior Changes

### Before
```bash
bge-quote-gen --episode 13
```
Generated: 4 images (1 quote × 4 platforms)
- Based on preferred quote source from config
- One image per platform

### After
```bash
bge-quote-gen --episode 13
```
Generates: 16 images (4 quotes × 4 platforms)
- All available quotes (claude, openai, deepseek, llama)
- All configured platforms (instagram, twitter, facebook, linkedin)

## File Naming Examples

For episode 13 generated on 2025-10-10 at 14:30:22:

```
bge_13_claude_instagram_20251010_143022.png
bge_13_claude_twitter_20251010_143023.png
bge_13_claude_facebook_20251010_143024.png
bge_13_claude_linkedin_20251010_143025.png
bge_13_openai_instagram_20251010_143026.png
bge_13_openai_twitter_20251010_143027.png
bge_13_openai_facebook_20251010_143028.png
bge_13_openai_linkedin_20251010_143029.png
bge_13_deepseek_instagram_20251010_143030.png
bge_13_deepseek_twitter_20251010_143031.png
bge_13_deepseek_facebook_20251010_143032.png
bge_13_deepseek_linkedin_20251010_143033.png
bge_13_llama_instagram_20251010_143034.png
bge_13_llama_twitter_20251010_143035.png
bge_13_llama_facebook_20251010_143036.png
bge_13_llama_linkedin_20251010_143037.png
```

## Backward Compatibility

The changes are backward compatible:
- Existing CLI options still work
- `--platform` flag can still be used to limit to specific platforms
- `--quote-source` flag is now less relevant but still works for single-quote extraction via `extract_episode()`

## Testing

To test the changes:

```bash
# Generate all 16 images for episode 13
bge-quote-gen --episode 13

# Generate only for specific platform (4 images: 4 quotes × 1 platform)
bge-quote-gen --episode 13 --platform instagram

# Dry run to see what would be generated
bge-quote-gen --episode 13 --dry-run
```

## Notes

- If an episode doesn't have all 4 quotes, only available quotes will be generated
- The orchestrator logs which quotes are found and which are missing
- Each image generation is independent, so partial failures won't block other images
