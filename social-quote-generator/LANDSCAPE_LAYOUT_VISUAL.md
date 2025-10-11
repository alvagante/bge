# Landscape Layout Visual Guide

## Layout Structure (1200x675 pixels)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────┐  ┌────────────────────────────────────────────────────────┐ │
│  │          │  │                                                        │ │
│  │   LOGO   │  │  BGE 1: Episode Title Here                            │ │
│  │          │  │                                                        │ │
│  └──────────┘  └────────────────────────────────────────────────────────┘ │
│                                                                             │
│  con Guest 1,  ┌────────────────────────────────────────────────────────┐ │
│  Guest 2       │                                                        │ │
│                │  ╔══════════════════════════════════════════════════╗  │ │
│                │  ║                                                  ║  │ │
│  ┌──────────┐  │  ║  "Quote text goes here and will be centered    ║  │ │
│  │          │  │  ║   both horizontally and vertically. The text   ║  │ │
│  │ EPISODE  │  │  ║   size adapts to fill the box nicely."         ║  │ │
│  │  COVER   │  │  ║                                                  ║  │ │
│  │          │  │  ║                          — Author Name           ║  │ │
│  │          │  │  ╚══════════════════════════════════════════════════╝  │ │
│  └──────────┘  │                                                        │ │
│                └────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
    ← 300px →      ←─────────────── 900px ──────────────────→
    (25%)                          (75%)
```

## Column Breakdown

### Left Column (~300px / 25% width)

**From top to bottom:**

1. **Logo** (top)
   - Scaled to fit column width
   - Maintains aspect ratio
   - White logo on colored background

2. **Guests** (middle)
   - Format: "con Guest 1, Guest 2, Guest 3"
   - Font size: 28pt (bigger than before)
   - Color: White (#FFFFFF)
   - Text wraps if too long

3. **Episode Cover** (bottom)
   - Positioned at bottom of column
   - Maintains 16:9 aspect ratio
   - Scales to fit column width
   - Format: `BGE {number}.png`

### Right Columns (~900px / 75% width)

**From top to bottom:**

1. **Episode Title/Number** (top)
   - Format: `BGE {NUMBER}: {TITLE}`
   - Font size: 48pt
   - Color: White (#FFFFFF)
   - Wraps to multiple lines if needed

2. **Quote Box** (fills remaining space)
   - Rounded corners (20px radius)
   - Semi-transparent black background (opacity: 180/255)
   - Padding: 40px on all sides
   - **Quote text:**
     - Adaptive font size (20-60pt)
     - Automatically sized to fill box nicely
     - Centered horizontally and vertically
     - Color: White (#FFFFFF)
   - **Author attribution:**
     - Bottom-right corner of box
     - Font size: 32pt
     - Color: Light grey (#CCCCCC)
     - Format: "— Author Name"

## Author-Specific Backgrounds

Each author can have a unique background image:

- **claude_landscape.png** → Brigante Claudio
- **openai_landscape.png** → Geek Estinto
- **llama_landscape.png** → Metante
- **deepseek_landscape.png** → Deep Geek

If no author-specific template exists, falls back to:
1. `default_landscape.png`
2. Solid color with author-specific color

## Adaptive Text Sizing

The quote text size automatically adjusts based on:
- Available box width (~820px after padding)
- Available box height (varies based on title length)
- Quote length

**Algorithm:**
1. Starts at maximum size (60pt)
2. Wraps text to fit width
3. Checks if total height fits
4. Reduces size by 2pt and repeats
5. Stops when text fits or reaches minimum (20pt)

This ensures quotes of any length look good!

## Example Dimensions

For 1200x675 landscape:
- Left column: ~300px wide
- Right columns: ~900px wide
- Logo area: ~240px wide × ~144px tall
- Episode cover: ~240px wide × ~135px tall (16:9)
- Quote box: ~900px wide × ~450-500px tall (varies)
- Quote text area: ~820px wide × ~370-420px tall (after padding)

## Color Scheme

**Default colors:**
- Background: Author-specific or #1a1a1a
- Text: White (#FFFFFF)
- Metadata: Light grey (#CCCCCC)
- Quote box: Semi-transparent black (rgba(0,0,0,180))

**Author-specific fallback colors:**
- Claude: #1a2332 (dark blue-grey)
- OpenAI: #2d1a2e (dark purple)
- Llama: #1a2e1a (dark green)
- DeepSeek: #2e1a1a (dark red)

## Testing

Run the test script to see the layout in action:

```bash
./social-quote-generator/test_landscape_layout.sh
```

Or test individual platforms:

```bash
# Twitter (landscape)
bge-quote-gen --episode 1 --platform twitter --quote-source claude --dry-run

# Facebook (landscape)
bge-quote-gen --episode 1 --platform facebook --quote-source openai --dry-run

# LinkedIn (landscape)
bge-quote-gen --episode 1 --platform linkedin --quote-source llama --dry-run

# Instagram (square - uses original layout)
bge-quote-gen --episode 1 --platform instagram --quote-source deepseek --dry-run
```

Check generated images in: `social-quote-generator/output/images/`

## Notes

- Square layouts (Instagram) continue to use the original centered layout
- All landscape platforms (Twitter, Facebook, LinkedIn) use the new 3-column layout
- The layout automatically detects landscape by checking if width > height
- All styling is configurable via `config/config.yaml`
