#!/bin/bash

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
DIR=$1
SCRIPT_DIR=$(dirname "$(realpath "$BASH_SOURCE")")

# Loop through each file in the directory
for FILE in "$DIR"/*_timebolted.txt; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the txt file
        TXT_FILE="${FILE%_timebolted.txt}_points.txt"

        # Check if the txt file already exists
        if [ ! -e "$TXT_FILE" ]; then
            # Run the summarise script
            echo "Writing summary of $FILE to $TXT_FILE"
            $SCRIPT_DIR/GenerateSummary.py "$FILE" | sed '/^$/d' > "$TXT_FILE"
#        else
#            echo "Skipping, $TXT_FILE already exists."
        fi
    fi
done
