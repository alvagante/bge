#!/bin/bash

# Simple script to remove silence from video files using ffmpeg
# This version uses ffmpeg's built-in silenceremove filter

INPUT_FILE="$1"
OUTPUT_FILE="$2"

if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: $0 <input_file> <output_file>"
    echo "Example: $0 101.mp4 101_timebolted.mp4"
    exit 1
fi

echo "Removing silence from: $INPUT_FILE"
echo "Output will be: $OUTPUT_FILE"

# Use ffmpeg's silenceremove filter
# stop_periods=-1 means process the entire file
# stop_duration=0.5 means remove silence longer than 0.5 seconds
# stop_threshold=-40dB is the silence threshold
ffmpeg -i "$INPUT_FILE" \
    -af "silenceremove=start_periods=1:start_duration=0:start_threshold=-40dB:detection=peak,\
silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-40dB:detection=peak" \
    -c:v copy \
    "$OUTPUT_FILE" -y

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Success! Output saved to: $OUTPUT_FILE"
else
    echo "Error occurred. Exit code: $EXIT_CODE"
    echo ""
    echo "This might be due to OneDrive sync issues."
    echo "Suggestions:"
    echo "1. Make sure the file is fully synced in OneDrive"
    echo "2. Try copying the file to a local directory first"
    echo "3. Right-click the file in Finder and select 'Always keep on this device'"
fi

exit $EXIT_CODE
