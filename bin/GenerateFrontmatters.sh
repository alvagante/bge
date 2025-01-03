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

# Loop through each file in the directory
for FILE in "$SOURCE_DIR"/*_youtube.yaml; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the txt file
        EPISODE="${FILE%_youtube.yaml}"

        # Check if the md file already exists
        if [ ! -e "${DESTINATION_DIR}/${EPISODE}.md" ]; then
            # Run the frontmatter generate script
            echo "Running  $SCRIPT_DIR/GenerateFrontmatter.py $EPISODE $DESTINATION_DIR"
            $SCRIPT_DIR/GenerateFrontmatter.py $EPISODE $DESTINATION_DIR 
        else
            echo "Skipping, ${DESTINATION_DIR}/${EPISODE}.md already exists."
        fi
    fi
done
