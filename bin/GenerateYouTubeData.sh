#!/bin/bash

PLAYLIST='PLnEyHqL3Zgg_5rT9Bmzv3QNzqjkB50zVh' # BGE Playlist

if [ -z "$2" ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

SOURCE_DIR=$1
DESTINATION_DIR=$2
SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE}")")

cd "$SOURCE_DIR"
# Loop through each file in the directory
for FILE in $( ls *.mp4 | grep -v 'timebolted' ); do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the txt file
        EPISODE="${FILE%.mp4}"

        # Check if the txt file already exists
        if [ ! -e "${DESTINATION_DIR}/${EPISODE}_youtube.yaml" ]; then
            # Run the YouTube get info script
            echo "Running $SCRIPT_DIR/GenerateYouTubeData.py \"$EPISODE\" \"https://www.youtube.com/playlist?list=$PLAYLIST\" > \"${DESTINATION_DIR}/${EPISODE}_youtube.yaml\""
            $SCRIPT_DIR/GenerateYouTubeData.py "$EPISODE" "https://www.youtube.com/playlist?list=$PLAYLIST" > "${DESTINATION_DIR}/${EPISODE}_youtube.yaml"
        else
            echo "Skipping, ${EPISODE}_youtube.yaml already exists."
        fi
    fi
done
