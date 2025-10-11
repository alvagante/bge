# Landscape Layout Refinement for Social Quote Generator

**Date:** 2025-10-10  
**Task:** Refine picture output for landscape images with new 3-column layout and author-specific background images

## Changes Made

### 1. Author-Specific Background Images

Added support for different background **images** for each quote author. The system now looks for author-specific template files:

**Naming Convention**: `{author}_{layout}.png`

Examples:
- `claude_landscape.png` - Background for Claude quotes on Twitter/Facebook/LinkedIn
- `openai_square.png` - Background for OpenAI quotes on Instagram
- `llama_landscape.png` - Background for Llama quotes on landscape platforms
- `deepseek_landscape.png` - Background for DeepSeek quotes on landscape platforms

**Fallback Chain**:
1. Author-specific template (e.g., `claude_landscape.png`)
2. Default platform template (e.g., `default_landscape.png`)
3. Solid color background with author-specific colors:
   - **Claude (Brigante Claudio)**: Dark blue-grey (#1a2332)
   - **OpenAI (Geek Estinto)**: Dark purple (#2d1a2e)
   - **Llama (Metante)**: Dark green (#1a2e1a)
   - **DeepSeek (Deep Geek)**: Dark red (#2e1a1a)

### 2. New Landscape Layout (3-Column Grid)

For landscape images (width > height), implemented a new layout:

#### Left Column (~25% width):
1. **Logo** - At the top
2. **Guests** - Below logo with bigger font (28pt)
3. **Episode Cover** - At the bottom (maintains 16:9 aspect ratio)

#### Right Columns 2-3 (~75% width):
1. **Episode Title/Number** - At the top with format: `BGE {NUMBER}: {TITLE}` (48pt font)
2. **Quote Box** - Below title with:
   - Rounded corners and padding (as before)
   - **Adaptive text size** - Automatically calculates optimal font size to fill the box nicely
   - Quote text centered both horizontally and vertically
   - Author attribution at bottom-right of box

### 3. Adaptive Text Sizing

Implemented `_find_optimal_font_size()` method that:
- Uses binary search to find the largest font size that fits
- Considers both width and height constraints
- Ensures text fills the box nicely without overflow
- Range: 20pt (minimum) to 60pt (maximum)

### 4. Code Structure

#### New Methods:
- `_render_landscape_layout()` - Main method for landscape layout
- `_render_adaptive_quote_box()` - Renders quote box with adaptive sizing
- `_find_optimal_font_size()` - Calculates optimal font size for available space
- `_wrap_text_to_width()` - Helper for text wrapping
- `_get_author_template_path()` - Returns path to author-specific template image
- `_get_background_color_for_author()` - Returns author-specific background color (fallback)

#### Modified Methods:
- `_load_template()` - Now accepts `quote_source` parameter for author-specific backgrounds
- `generate()` - Detects landscape vs portrait and routes to appropriate layout

### 5. Configuration Updates

Added to `config/config.yaml`:
```yaml
author_backgrounds:
  claude: "#1a2332"
  openai: "#2d1a2e"
  llama: "#1a2e1a"
  deepseek: "#2e1a1a"
```

## Backward Compatibility

- Square and portrait layouts continue to use the original rendering method
- All existing configuration options remain functional
- No breaking changes to the API or CLI

## Implementation Status

✅ **COMPLETE** - All landscape layout features are implemented and ready to use:

- ✅ 3-column grid layout for landscape images
- ✅ Left column with logo, guests (28pt), and episode cover
- ✅ Right columns with title (BGE {NUMBER}: {TITLE}) and quote box
- ✅ Adaptive text sizing (20-60pt) to fill box nicely
- ✅ Author-specific template image support
- ✅ Fallback to author-specific colors
- ✅ All helper methods implemented

## Testing Recommendations

1. Generate landscape images for all platforms (Twitter, Facebook, LinkedIn)
2. Test with different quote sources to verify background images/colors
3. Test with quotes of varying lengths to verify adaptive text sizing
4. Verify guests text wrapping in left column
5. Check episode cover positioning and sizing

**Quick Test:**
```bash
./social-quote-generator/test_landscape_layout.sh
```

## Example Commands

```bash
# Test landscape layout with different authors
bge-quote-gen --episode 1 --platform twitter --quote-source claude --dry-run
bge-quote-gen --episode 1 --platform twitter --quote-source openai --dry-run
bge-quote-gen --episode 1 --platform twitter --quote-source llama --dry-run
bge-quote-gen --episode 1 --platform twitter --quote-source deepseek --dry-run

# Test with Facebook (also landscape)
bge-quote-gen --episode 1 --platform facebook --quote-source claude --dry-run

# Test with Instagram (square - should use original layout)
bge-quote-gen --episode 1 --platform instagram --quote-source claude --dry-run
```

## Files Modified

1. `social-quote-generator/src/generators/image_generator.py` - Main implementation
2. `social-quote-generator/config/config.yaml` - Configuration updates and documentation
3. `social-quote-generator/templates/README.md` - Documentation for author-specific templates

## Creating Author-Specific Templates

To create custom background images for each author:

1. Create PNG files in `social-quote-generator/templates/` with naming pattern:
   - `claude_landscape.png` (1200x675)
   - `claude_square.png` (1080x1080)
   - `openai_landscape.png` (1200x675)
   - `openai_square.png` (1080x1080)
   - `llama_landscape.png` (1200x675)
   - `deepseek_landscape.png` (1200x675)
   - etc.

2. Design guidelines:
   - Use platform-specific dimensions
   - Leave space for text overlay (center area)
   - Ensure good contrast for white text
   - Include subtle branding elements
   - Test with various quote lengths

3. The system will automatically use these templates when generating images for the corresponding author

## Notes

- The adaptive text sizing ensures quotes of any length will fit nicely in the box
- Guests text in the left column wraps automatically if too long
- Episode cover maintains aspect ratio and scales to fit left column width
- All styling (colors, padding, corner radius) remains configurable via config.yaml
