#!/bin/bash

# Test script for landscape layout with 3-column grid
# This will generate test images to verify the new layout

echo "Testing Landscape Layout with 3-Column Grid"
echo "============================================"
echo ""

# Test with different authors to see different backgrounds
echo "1. Testing Claude (Brigante Claudio) - Twitter landscape"
bge-quote-gen --episode 1 --platform twitter --quote-source claude --dry-run --verbose

echo ""
echo "2. Testing OpenAI (Geek Estinto) - Facebook landscape"
bge-quote-gen --episode 1 --platform facebook --quote-source openai --dry-run --verbose

echo ""
echo "3. Testing Llama (Metante) - LinkedIn landscape"
bge-quote-gen --episode 1 --platform linkedin --quote-source llama --dry-run --verbose

echo ""
echo "4. Testing DeepSeek (Deep Geek) - Twitter landscape"
bge-quote-gen --episode 1 --platform twitter --quote-source deepseek --dry-run --verbose

echo ""
echo "5. Testing Instagram (square layout - should use original layout)"
bge-quote-gen --episode 1 --platform instagram --quote-source claude --dry-run --verbose

echo ""
echo "============================================"
echo "Test complete! Check images in:"
echo "social-quote-generator/output/images/"
echo ""
echo "Expected landscape layout (Twitter/Facebook/LinkedIn):"
echo "  Left column (25%):"
echo "    - Logo at top"
echo "    - Guests with bigger font (28pt)"
echo "    - Episode cover at bottom"
echo "  Right columns (75%):"
echo "    - Episode title: 'BGE {NUMBER}: {TITLE}' (48pt)"
echo "    - Quote box with adaptive text size"
echo "    - Author attribution at bottom-right"
echo ""
echo "Expected square layout (Instagram):"
echo "    - Original centered layout"
echo "    - Logo overlay"
echo "    - Centered quote"
echo "    - Episode metadata at bottom"
