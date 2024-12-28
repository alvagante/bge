#!/bin/bash
export TMPDIR=/tmp

if [ -z "$3" ]; then
    echo "Usage: $0 <episode_number> <seconds_to_trim_at_beginning> <seconds_to_trim_at_end>"
    exit 1
fi

VIDEO_DIR='/Users/al/Library/CloudStorage/OneDrive-Personal/BGE/Episodes'

# Function to highlight text in bold
bold() {
    echo -e "\033[1m$1\033[0m"
}

SOURCE_FILE="$VIDEO_DIR/$1_timebolted.mp4"
TRIMMED_FILE="$VIDEO_DIR/$1_trimmed.mp4"
BEGIN_TRIM=$2
END_TRIM=$3

bold "Trimming ${SOURCE_FILE} to ${TRIMMED_FILE} with ${BEGIN_TRIM} seconds at the beginning and ${END_TRIM} seconds at the end"
ffmpeg -i "$SOURCE_FILE" -ss "$BEGIN_TRIM" -to "$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$SOURCE_FILE" | awk '{print int($1 - '"$END_TRIM"')}')" -c copy "$TRIMMED_FILE"

bold "Trimming completed. Replacing the original file with the trimmed file."
mv "$TRIMMED_FILE" "$SOURCE_FILE"