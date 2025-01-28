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
for FILE in "$DIR"/*_points.txt; do
    # Check if the file is a regular file
    if [ -f "$FILE" ]; then
        # Construct the name of the Claude txt file
        CLAUDE_TXT_FILE="${FILE%_points.txt}_quote_claude.txt"
        EPISODE=$(basename "$FILE" | grep -oE '[0-9]+')

        # Check if the txt file already exists
        if [ ! -e "$CLAUDE_TXT_FILE" ]; then
            # Run the summarise script
            echo "Generating a quote for episode $EPISODE to $CLAUDE_TXT_FILE"
            $SCRIPT_DIR/GenerateQuoteClaude.py "$DIR" "$EPISODE" > "$CLAUDE_TXT_FILE"
#        else
#            echo "Skipping, $CLAUDE_TXT_FILE already exists."
        fi

        # Construct the name of the Claude txt file
        OPENAI_TXT_FILE="${FILE%_points.txt}_quote_openai.txt"
        EPISODE=$(basename "$FILE" | grep -oE '[0-9]+')

        # Check if the txt file already exists
        if [ ! -e "$OPENAI_TXT_FILE" ]; then
            # Run the summarise script
            echo "Generating a quote for episode $EPISODE to $OPENAI_TXT_FILE"
            $SCRIPT_DIR/GenerateQuoteOpenAI.py "$DIR" "$EPISODE" > "$OPENAI_TXT_FILE"
#        else
#            echo "Skipping, $OPENAI_TXT_FILE already exists."
        fi


    fi
done
