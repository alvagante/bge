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
  
        ## CLAUDE
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

        ## OPENAI
        # Construct the name of the openai txt file
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

        ## DEEPSEEK
        # Construct the name of the deepseek txt file
        DEEPSEEK_TXT_FILE="${FILE%_points.txt}_quote_deepseek_reasoning.txt"
        EPISODE=$(basename "$FILE" | grep -oE '[0-9]+')

        # Check if the txt file already exists
        if [ ! -e "$DEEPSEEK_TXT_FILE" ]; then
            # Run the summarise script
            echo "Generating a quote with reasoning for episode $EPISODE to $DEEPSEEK_TXT_FILE"
            $SCRIPT_DIR/GenerateQuoteDeepSeek.py "$DIR" "$EPISODE" > "$DEEPSEEK_TXT_FILE"
#        else
#            echo "Skipping, $DEEPSEEK_TXT_FILE already exists."
        fi

        # Generate the file with just the quote
        DEEPSEEK_QUOTE_FILE="${FILE%_points.txt}_quote_deepseek.txt"
        # Check if the txt file already exists and if DEEPSEEK_TXT_FILE exists and is not empty
        if [ ! -e "$DEEPSEEK_QUOTE_FILE" ] && [ -s "$DEEPSEEK_TXT_FILE" ]; then
          # Extract from $DEEPSEEK_TXT_FILE only the text after the string </reason>
          echo "Generating quote only file for episode $EPISODE to $DEEPSEEK_QUOTE_FILE"
          sed -n '/<\/think>/,$p' "$DEEPSEEK_TXT_FILE" | sed '1d' > "$DEEPSEEK_QUOTE_FILE"
        fi

    fi
done
