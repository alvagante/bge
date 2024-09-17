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
for FILE in "$DIR"/*_article.txt; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the txt file
        EPISODE="${FILE%_article.txt}"

        # Check if the txt file already exists
        if [ ! -e "${EPISODE}.md" ]; then
            # Run the frontmatter generate script
            echo "Generating frontmatter for episode to $EPISODE"
            $SCRIPT_DIR/frontmatter_generator.py "$EPISODE" 
        else
            echo "Skipping, ${EPISODE}.md already exists."
        fi
    fi
done
