#!/bin/bash

if [ -z "$2" ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

SOURCE_DIR=$1
DESTINATION_DIR=$2

# Loop through each file in the directory
for FILE in "$SOURCE_DIR"/*timebolted.mp3; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        DEST_FILE=$(basename "$FILE")
        TXT_FILE="${DEST_FILE%.mp3}.txt"

        # Check if the txt file already exists
        if [ ! -e "${DESTINATION_DIR}/${TXT_FILE}" ]; then
            # Execute the pippo command to generate the txt file
            vosk-transcriber -i "$FILE" -o "${DESTINATION_DIR}/${TXT_FILE}"  --lang it --model-name vosk-model-it-0.22
#        else
#            echo "Skipping, ${DESTINATION_DIR}/${TXT_FILE} already exists."
        fi
    fi
done
