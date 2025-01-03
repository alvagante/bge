#!/bin/bash

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
DIR=$1
SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE}")")

# Loop through each file in the directory
for FILE in "$DIR"/*.md; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the txt file
        EPISODE="${FILE%.md}"

        # Check if the txt file already exists
        if [ ! -e "${EPISODE}_md.txt" ]; then
            # Run the frontmatter generate script
            echo "Generating ia data for episode to $EPISODE"
            cp "${EPISODE}.md" "${EPISODE}_md.txt" 
#        else
#            echo "Skipping, ${EPISODE}_md.txt already exists."
        fi
    fi
done
