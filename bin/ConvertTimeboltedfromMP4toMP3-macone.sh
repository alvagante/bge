#!/bin/bash
export TMPDIR=/tmp

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
DIR=$1

# Loop through each file in the directory
for FILE in "$DIR"/*timebolted.mp4; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the mp3 file
        MP3_FILE="${FILE%.mp4}.mp3"

        # Check if the mp3 file already exists
        if [ ! -e "$MP3_FILE" ]; then
            # Execute the pippo command to generate the mp3 file
            ffmpeg -i "$FILE" -vn -ab 256k "$MP3_FILE"
        else
            echo "Skipping, $MP3_FILE already exists."
        fi
    fi
done
