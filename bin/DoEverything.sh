#!/bin/bash
BGE_DIR="/Users/al/Library/CloudStorage/OneDrive-Personal/BGE"
GIT_DIR=$(git rev-parse --show-toplevel)
EPISODES_DIR="${BGE_DIR}/Episodes"
SCRIPT_DIR="${GIT_DIR}/bin"

# Function to highlight text in bold
bold() {
    echo -e "\033[1m$1\033[0m"
}

bold "Converting MP4 files to timebolted MP4 files in $EPISODES_DIR"
#$SCRIPT_DIR/ConvertMP4toMP4Timebolted.sh "$EPISODES_DIR"

bold "Converting timebolted MP4 files to MP3 files in $EPISODES_DIR"
#$SCRIPT_DIR/ConvertTimeboltedfromMP4toMP3.sh "$EPISODES_DIR"

bold "Converting MP3 files to TXT files in $EPISODES_DIR"
#$SCRIPT_DIR/ConvertTimeboltedfromMP3toTXT.sh "$EPISODES_DIR"

bold "Get YouTube data in $EPISODES_DIR"
$SCRIPT_DIR/GenerateYouTubeData.sh "$EPISODES_DIR" "$GIT_DIR/assets/texts"

bold "Summarising TXT files in $EPISODES_DIR"
#$SCRIPT_DIR/SummariseTimeboltedTXT.sh "$EPISODES_DIR"

bold "Extracting hashtags from summary TXT files in $EPISODES_DIR"
#$SCRIPT_DIR/HashtagsFromSummaryTXT.sh "$EPISODES_DIR"

bold "Generating frontmatters in $EPISODES_DIR"
$SCRIPT_DIR/GenerateFrontmatters.sh "$GIT_DIR/assets/texts" "$GIT_DIR/_episodes"

bold "Generating thumbnails in $GIT_DIR/assets/covers/"
$SCRIPT_DIR/GenerateThumbnails.sh "${BGE_DIR}/Copertine" "$GIT_DIR/assets/covers"

bold "Generating data source for AI"
#$SCRIPT_DIR/GenerateDataSource.sh "$EPISODES_DIR"