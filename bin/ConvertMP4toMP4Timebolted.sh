#!/bin/bash
export TMPDIR=/tmp

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
DIR=$1

# Loop through each file in the directory
cd "$DIR" || exit
for FILE in $( ls *.mp4 | grep -v 'timebolted' ); do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the timebolted file
        TIMEBOLTED_FILE="${FILE%.mp4}_timebolted.mp4"

        # Check if the timebolted file already exists
        if [ ! -e "$TIMEBOLTED_FILE" ]; then
            # Execute the unsilence command to generate the timebolted file
            echo "unsilence -y $FILE $TIMEBOLTED_FILE"
            unsilence -y "$FILE" "$TIMEBOLTED_FILE"
#        else
#            echo "Skipping, $TIMEBOLTED_FILE already exists."
        fi
    fi
done