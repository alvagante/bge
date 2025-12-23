#!/bin/bash

# Check if the directory is provided
if [ -z "$2" ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

# Assign the directory to a variable
SOURCE_DIR=$1
DESTINATION_DIR=$2
SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE}")")

# Detect OS and set resize command
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use sips
    resize_image() {
        sips --resampleHeight 140 "$1" --out "$2"
    }
else
    # Linux - use ImageMagick
    resize_image() {
        convert "$1" -resize x140 "$2"
    }
fi

# Loop through each file in the directory
for FILE in $SOURCE_DIR/BGE\ *.png; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        DEST_FILE=$(basename "$FILE")
        # Check if the destination file already exists
        if [ ! -e "${DESTINATION_DIR}/${DEST_FILE}" ]; then
            # Convert file
            echo "Generating resized png ${DESTINATION_DIR}/${DEST_FILE}"
            resize_image "${FILE}" "${DESTINATION_DIR}/${DEST_FILE}"
#        else
#            echo "Skipping, ${DESTINATION_DIR}/${DEST_FILE} already exists."
        fi
    fi
done
