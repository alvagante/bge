#!/bin/bash

# Script to remove silence from video files using ffmpeg
# Works better with OneDrive/cloud files than unsilence

INPUT_FILE="$1"
OUTPUT_FILE="$2"
SILENCE_THRESHOLD="${3:--30dB}"
SILENCE_DURATION="${4:-0.5}"

if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: $0 <input_file> <output_file> [silence_threshold] [silence_duration]"
    echo "Example: $0 input.mp4 output.mp4 -30dB 0.5"
    exit 1
fi

echo "Detecting silence in: $INPUT_FILE"
echo "Output will be: $OUTPUT_FILE"
echo "Silence threshold: $SILENCE_THRESHOLD"
echo "Silence duration: ${SILENCE_DURATION}s"

# Step 1: Detect silence periods
echo "Step 1: Detecting silence periods..."
ffmpeg -i "$INPUT_FILE" -af silencedetect=noise=$SILENCE_THRESHOLD:d=$SILENCE_DURATION -f null - 2>&1 | \
    grep -oP 'silence_(start|end): \K[0-9.]+' > /tmp/silence_periods.txt

if [ ! -s /tmp/silence_periods.txt ]; then
    echo "No silence detected or error reading file. Trying alternative method..."
    # Alternative: just copy the file
    echo "Copying file without silence removal..."
    ffmpeg -i "$INPUT_FILE" -c copy "$OUTPUT_FILE" -y
    exit $?
fi

# Step 2: Create filter to remove silence
echo "Step 2: Creating removal filter..."
python3 - <<'PYTHON_SCRIPT'
import sys

# Read silence periods
with open('/tmp/silence_periods.txt', 'r') as f:
    times = [float(line.strip()) for line in f if line.strip()]

if len(times) < 2:
    print("Not enough silence data to process", file=sys.stderr)
    sys.exit(1)

# Pair up start and end times
silence_periods = []
for i in range(0, len(times)-1, 2):
    silence_periods.append((times[i], times[i+1]))

# Create segments to keep (non-silent parts)
keep_segments = []
last_end = 0
for start, end in silence_periods:
    if start > last_end:
        keep_segments.append((last_end, start))
    last_end = end

# Add final segment if needed
if silence_periods:
    keep_segments.append((silence_periods[-1][1], 999999))  # Large number for end

# Generate ffmpeg select filter
if keep_segments:
    select_expr = '+'.join([f'between(t,{s},{e})' for s, e in keep_segments])
    print(select_expr)
else:
    print("1")  # Keep everything if no segments
PYTHON_SCRIPT

SELECT_FILTER=$(python3 - <<'PYTHON_SCRIPT'
import sys

# Read silence periods
with open('/tmp/silence_periods.txt', 'r') as f:
    times = [float(line.strip()) for line in f if line.strip()]

if len(times) < 2:
    print("1")  # Keep everything
    sys.exit(0)

# Pair up start and end times
silence_periods = []
for i in range(0, len(times)-1, 2):
    silence_periods.append((times[i], times[i+1]))

# Create segments to keep (non-silent parts)
keep_segments = []
last_end = 0
for start, end in silence_periods:
    if start > last_end:
        keep_segments.append((last_end, start))
    last_end = end

# Generate ffmpeg select filter
if keep_segments:
    select_expr = '+'.join([f'between(t,{s},{e})' for s, e in keep_segments])
    print(select_expr)
else:
    print("1")  # Keep everything if no segments
PYTHON_SCRIPT
)

# Step 3: Apply filter and create output
echo "Step 3: Removing silence and creating output..."
ffmpeg -i "$INPUT_FILE" \
    -vf "select='$SELECT_FILTER',setpts=N/FRAME_RATE/TB" \
    -af "aselect='$SELECT_FILTER',asetpts=N/SR/TB" \
    "$OUTPUT_FILE" -y

echo "Done! Output saved to: $OUTPUT_FILE"
