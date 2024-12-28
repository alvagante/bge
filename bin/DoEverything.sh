#!/bin/bash

VIDEO_DIR='/Users/al/Library/CloudStorage/OneDrive-Personal/ADI/Episodes'
#VIDEO_DIR='/Users/al/Library/CloudStorage/OneDrive-Personal/GITHUB/adi.example42.com'
#VIDEO_DIR='/Users/al/Library/CloudStorage/OneDrive-Personal/BGE/Episodes'
SCRIPT_DIR='/Users/al/Library/CloudStorage/OneDrive-Personal/BGE/bge.github.io/bin'


# Function to highlight text in bold
bold() {
    echo -e "\033[1m$1\033[0m"
}

bold "Converting MP4 files to timebolted MP4 files in $VIDEO_DIR"
#$SCRIPT_DIR/ConvertMP4toMP4Timebolted.sh "$VIDEO_DIR"

bold "Converting timebolted MP4 files to MP3 files in $VIDEO_DIR"
#$SCRIPT_DIR/ConvertTimeboltedfromMP4toMP3.sh "$VIDEO_DIR"

bold "Converting MP3 files to TXT files in $VIDEO_DIR"
#$SCRIPT_DIR/ConvertTimeboltedfromMP3toTXT.sh "$VIDEO_DIR"

bold "Get YouTube data in $VIDEO_DIR"
$SCRIPT_DIR/GenerateYouTubeData.sh "$VIDEO_DIR"

bold "Summarising TXT files in $VIDEO_DIR"
#$SCRIPT_DIR/SummariseTimeboltedTXT.sh "$VIDEO_DIR"

bold "Extracting hashtags from summary TXT files in $VIDEO_DIR"
#$SCRIPT_DIR/HashtagsFromSummaryTXT.sh "$VIDEO_DIR"

bold "Generating frontmatters in $VIDEO_DIR"
#$SCRIPT_DIR/GenerateFrontmatters.sh "$VIDEO_DIR"

bold "Generating data source for AI"
$SCRIPT_DIR/GenerateDataSource.sh "$VIDEO_DIR"