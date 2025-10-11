# Author-Specific Templates Guide

This guide explains how to create custom background images for each quote author in the BGE Social Quote Generator.

## Overview

The system supports different background images for each AI quote author (Claude, OpenAI, Llama, DeepSeek). This allows you to create unique visual identities for each author's quotes.

## File Naming Convention

Create PNG files with this naming pattern:

```
{author}_{layout}.png
```

Where:
- **{author}**: `claude`, `openai`, `llama`, or `deepseek` (lowercase)
- **{layout}**: `landscape` or `square`

## Required Files

### Landscape Templates (1200x675)
Used for Twitter, Facebook, and LinkedIn:

- `claude_landscape.png` - Brigante Claudio quotes
- `openai_landscape.png` - Geek Estinto quotes
- `llama_landscape.png` - Metante quotes
- `deepseek_landscape.png` - Deep Geek quotes

### Square Templates (1080x1080)
Used for Instagram:

- `claude_square.png` - Brigante Claudio quotes
- `openai_square.png` - Geek Estinto quotes
- `llama_square.png` - Metante quotes
- `deepseek_square.png` - Deep Geek quotes

## Design Guidelines

### Dimensions
- **Landscape**: 1200x675 pixels (16:9 aspect ratio)
- **Square**: 1080x1080 pixels (1:1 aspect ratio)

### Layout Considerations

#### For Landscape Templates (1200x675):
The new 3-column layout divides the image as follows:

**Left Column (~300px width)**:
- Logo at top
- Guests text (wraps if needed)
- Episode cover at bottom

**Right Columns (~900px width)**:
- Episode title/number at top
- Quote box in center (with rounded corners and padding)

**Design Tips**:
- Keep the left 300px relatively clean for logo/guests/cover
- The right 900px should have good contrast for the quote box
- Consider subtle gradients or patterns
- Avoid busy backgrounds in the center-right area

#### For Square Templates (1080x1080):
Uses the original centered layout:
- Logo overlay (configurable position)
- Centered quote text
- Episode cover overlay (configurable position)
- Metadata at bottom

**Design Tips**:
- Keep center area clear for quote text
- Ensure good contrast throughout
- Consider symmetrical designs

### Color and Contrast
- Use colors that complement white text (default quote color)
- Ensure sufficient contrast ratio (WCAG AA: 4.5:1 minimum)
- Test with both short and long quotes
- Consider the quote box background (semi-transparent black by default)

### Branding
- Include subtle BGE branding elements
- Don't overlap with logo position (configurable in config.yaml)
- Leave space for episode cover overlay
- Consider the overall BGE visual identity

### Author Themes (Suggested)

**Claude (Brigante Claudio)**:
- Theme: Professional, analytical
- Suggested colors: Blues, greys, cool tones
- Fallback color: #1a2332 (dark blue-grey)

**OpenAI (Geek Estinto)**:
- Theme: Modern, tech-forward
- Suggested colors: Purples, teals, vibrant tones
- Fallback color: #2d1a2e (dark purple)

**Llama (Metante)**:
- Theme: Natural, grounded
- Suggested colors: Greens, earth tones
- Fallback color: #1a2e1a (dark green)

**DeepSeek (Deep Geek)**:
- Theme: Bold, intense
- Suggested colors: Reds, oranges, warm tones
- Fallback color: #2e1a1a (dark red)

## File Format

- **Format**: PNG (supports transparency)
- **Color Mode**: RGB or RGBA
- **Bit Depth**: 24-bit or 32-bit
- **Compression**: PNG compression (lossless)

## Testing Your Templates

After creating your templates, test them with:

```bash
# Test landscape template for each author
bge-quote-gen --episode 1 --platform twitter --quote-source claude --dry-run
bge-quote-gen --episode 1 --platform twitter --quote-source openai --dry-run
bge-quote-gen --episode 1 --platform twitter --quote-source llama --dry-run
bge-quote-gen --episode 1 --platform twitter --quote-source deepseek --dry-run

# Test square template for each author
bge-quote-gen --episode 1 --platform instagram --quote-source claude --dry-run
bge-quote-gen --episode 1 --platform instagram --quote-source openai --dry-run
bge-quote-gen --episode 1 --platform instagram --quote-source llama --dry-run
bge-quote-gen --episode 1 --platform instagram --quote-source deepseek --dry-run
```

Check the generated images in `social-quote-generator/output/images/`

## Fallback Behavior

If an author-specific template is not found, the system will:

1. Try the author-specific template (e.g., `claude_landscape.png`)
2. Fall back to default template (e.g., `default_landscape.png`)
3. Fall back to solid color background (using author-specific colors)

This means you can create templates incrementally - start with one author and add others later.

## Example Workflow

1. **Design Phase**:
   - Create mockups in your design tool (Figma, Photoshop, etc.)
   - Use the correct dimensions
   - Test with sample quote text overlays
   - Get feedback from team

2. **Export Phase**:
   - Export as PNG files
   - Use the exact naming convention
   - Verify dimensions
   - Check file sizes (keep under 1MB for performance)

3. **Deploy Phase**:
   - Copy PNG files to `social-quote-generator/templates/`
   - Test with various episodes and quote lengths
   - Verify on different platforms
   - Adjust if needed

4. **Iterate**:
   - Gather feedback from generated images
   - Refine designs based on readability
   - Update templates as needed

## Tips for Success

- **Start Simple**: Begin with subtle gradients or solid colors
- **Test Early**: Generate test images frequently during design
- **Consider Mobile**: Most social media is viewed on mobile devices
- **Maintain Consistency**: Keep a cohesive visual style across authors
- **Document Choices**: Note why you chose specific colors/themes for each author
- **Version Control**: Keep source files (PSD, Figma, etc.) in version control

## Need Help?

- Check `README.md` in this directory for general template guidelines
- Review `config/config.yaml` for configuration options
- See `.kiro/summaries/` for implementation details
- Test with `--verbose` flag for detailed logging

