#!/bin/bash

PLAYLIST='PLnEyHqL3Zgg_5rT9Bmzv3QNzqjkB50zVh' # BGE Playlist

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
DIR=$1
SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE}")")

cd "$DIR"
# Loop through each file in the directory
for FILE in $( ls *.mp4 | grep -v 'timebolted' ); do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the txt file
        EPISODE="${FILE%.mp4}"

        # Check if the txt file already exists
        if [ ! -e "${EPISODE}_youtube.yaml" ]; then
            # Run the YouTube get info script
            echo "Generating Youtube info yaml for episode  $EPISODE"
            $SCRIPT_DIR/GetYouTubeId.py "$EPISODE" "https://www.youtube.com/playlist?list=$PLAYLIST" > "${EPISODE}_youtube.yaml"
        else
            echo "Skipping, ${EPISODE}_youtube.yaml already exists."
        fi
    fi
done
