#!/bin/bash

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
SOURCE_DIR=$1
DESTINATION_DIR=$2
SCRIPT_DIR=$(dirname "$(realpath "$BASH_SOURCE")")

# Loop through each file in the directory
for FILE in "$SOURCE_DIR"/*_quote.txt; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the image file
        EPISODE=$(basename "$FILE" | grep -oE '[0-9]+')
        IMAGE_FILE="${DESTINATION_DIR}${EPISODE}.png"

        # Check if the txt file already exists
        if [ ! -e "$IMAGE_FILE" ]; then
            # Run the summarise script
            echo "Generating an image $EPISODE in $IMAGE_FILE"
            $SCRIPT_DIR/GenerateImageMidjourney.py "$FILE" "$IMAGE_FILE"
#        else
#            echo "Skipping, $IMAGE_FILE already exists."
        fi
    fi
done
