#!/bin/bash

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
DIR=$1

# Loop through each file in the directory
for FILE in $( ls "$DIR"/*.mp3 | grep -v timebolted ) ; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the txt file
        TXT_FILE="${FILE%.mp3}.txt"

        # Check if the txt file already exists
        if [ ! -e "$TXT_FILE" ]; then
            # Execute the vosk-transcriber command to generate the txt file
            vosk-transcriber -i "$FILE" -o "$TXT_FILE"  --lang it --model-name vosk-model-it-0.22
        else
            echo "Skipping, $TXT_FILE already exists."
        fi
    fi
done
