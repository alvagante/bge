#!/bin/bash
# Test script to verify all quotes generation

echo "Testing BGE Quote Generator - All Quotes Generation"
echo "===================================================="
echo ""

# Check if episode number is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <episode_number>"
    echo "Example: $0 13"
    exit 1
fi

EPISODE=$1

echo "Testing episode: $EPISODE"
echo ""

# Run the generator in dry-run mode
echo "Running generator (dry-run mode)..."
bge-quote-gen --episode $EPISODE --dry-run --verbose

echo ""
echo "===================================================="
echo "Test completed!"
echo ""
echo "Expected output:"
echo "- 16 images should be generated (4 quotes × 4 platforms)"
echo "- Filenames should follow pattern: bge_${EPISODE}_<author>_<platform>_<timestamp>.png"
echo "- Authors: claude, openai, deepseek, llama"
echo "- Platforms: instagram, twitter, facebook, linkedin"
