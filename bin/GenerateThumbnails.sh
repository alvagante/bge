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
for FILE in $SOURCE_DIR/BGE\ *.png; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        DEST_FILE=$(basename "$FILE")
        # Check if the destination file already exists
        if [ ! -e "${DESTINATION_DIR}/${DEST_FILE}" ]; then
            # Convert file
            echo "Generating resized png ${DESTINATION_DIR}/${DEST_FILE}"
            sips --resampleHeight 140 "${FILE}" --out "${DESTINATION_DIR}/${DEST_FILE}"
#        else
#            echo "Skipping, ${DESTINATION_DIR}/${DEST_FILE} already exists."
        fi
    fi
done
