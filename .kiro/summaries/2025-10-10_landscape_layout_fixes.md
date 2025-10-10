# Landscape Layout Fixes

**Date:** 2025-10-10  
**Task:** Fix landscape picture layout issues

## Issues Fixed

### 1. Logo Stretched
**Problem:** Logo aspect ratio was not being preserved - it was being resized with a fixed calculation `int((left_col_width - padding * 2) * 0.6)` which didn't respect the original image proportions.

**Solution:** Calculate the logo size by preserving the original aspect ratio:
```python
original_width, original_height = logo.size
aspect_ratio = original_height / original_width
logo_width = max_logo_width
logo_height = int(logo_width * aspect_ratio)
```

### 2. Missing Guest List
**Problem:** Guests were not visible in the rendered image.

**Solution:** 
- Recreated the `draw` object after image mode conversions (RGBA → RGB)
- Increased guest font size from 28 to 32 for better visibility
- The draw object needs to be recreated after `image.convert("RGB")` operations

### 3. Missing Title
**Problem:** Episode title and number were not visible.

**Solution:** Recreated the `draw` object after all image mode conversions, ensuring text rendering happens on the final RGB image.

## Technical Details

The core issue was that PIL's `ImageDraw.Draw()` object becomes invalid after converting the image mode. The fix ensures we recreate the draw object after:
1. Pasting the logo (RGBA → RGB conversion)
2. Pasting the episode cover (RGBA → RGB conversion)

This ensures all text rendering (guests, title) happens on the correct image object.

## Layout Structure (Confirmed)

**Left Column (25% width):**
- Logo (top, aspect ratio preserved)
- Guests list (bigger font: 32px)
- Episode cover (bottom, aspect ratio preserved)

**Right Columns (75% width):**
- Episode title: "BGE [NUMBER]: [TITLE]" (top, 48px font)
- Quote box (fills remaining space)
