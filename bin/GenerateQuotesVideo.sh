#!/bin/bash
#
# GenerateQuotesVideo.sh
# Creates a short vertical video with all quotes from BGE episode
#
# Usage: ./GenerateQuotesVideo.sh <episode_number>
# Example: ./GenerateQuotesVideo.sh 6
#
# Generates a video with all quotes (claude, openai, deepseek, llama) using different voices
#

set -e

# =============================================================================
# CONFIGURATION - Easy customization section
# =============================================================================

# Directories (adjust these paths as needed)
BASE_DIR="/home/al/bge"
EPISODES_DIR="${BASE_DIR}/_episodes"
COVERS_DIR="/home/al/rclone/onedrive/BGE/Copertine"
FONTS_DIR="${BASE_DIR}/assets/fonts"
MUSIC_DIR="${BASE_DIR}/assets/songs"         # Directory with background music mp3 files
OUTPUT_DIR="/home/al/rclone/onedrive/BGE/Clips/Quotes"       # Output directory for generated videos
TEMP_DIR="/tmp/bge_video_$$"                 # Temporary working directory

# Video settings
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
VIDEO_FPS=30
VIDEO_DURATION_MIN=8                          # Minimum video duration in seconds
BACKGROUND_COLOR="black"

# Font settings
FONT_FILE="${FONTS_DIR}/Kanit-Regular.ttf"
FONT_FILE_ALT="${FONTS_DIR}/Peace Sans Webfont.ttf"

# Quote text settings
QUOTE_FONT_SIZE=76
QUOTE_FONT_COLOR="white"
QUOTE_BOX_COLOR="black@0.7"                   # Semi-transparent background
QUOTE_BOX_BORDER=20
QUOTE_PADDING_LEFT=120                         # Left padding for text
QUOTE_PADDING_RIGHT=120                        # Right padding for text
QUOTE_Y="120"                                 # Top position for quote text
QUOTE_MAX_CHARS=38                            # Max characters per line for word wrap

# Episode title settings
TITLE_FONT_SIZE=10
TITLE_FONT_COLOR="white"
TITLE_X="(w-text_w)/2"
TITLE_Y="60"

# Episode number settings
EPISODE_FONT_SIZE=72
EPISODE_FONT_COLOR="#FFD700"                  # Gold color
EPISODE_X="(w-text_w)/2"
EPISODE_Y="40"

# Author settings
AUTHOR_FONT_SIZE=56
AUTHOR_FONT_COLOR="#FFD700"                   # Gold color for author
AUTHOR_PADDING_LEFT=760                        # Left padding for author text

# Audio settings
MUSIC_VOLUME=0.12                             # Background music volume (0.0 - 1.0)
VOICE_VOLUME=1.0                              # TTS voice volume
TTS_ENGINE="openai"                           # Options: gtts, espeak, piper, openai

# Quote sources to process (in order)
QUOTE_SOURCES=("claude" "openai" "deepseek" "llama")

# OpenAI TTS voices for each quote source
declare -A OPENAI_VOICES=(
    ["claude"]="onyx"
    ["openai"]="nova"
    ["deepseek"]="fable"
    ["llama"]="shimmer"
)

# =============================================================================
# AUTHOR NAME MAPPING
# =============================================================================
declare -A AUTHOR_NAMES=(
    ["claude"]="Brigante Claudio"
    ["openai"]="Geek Estinto"
    ["deepseek"]="Deep Geek"
    ["llama"]="Metante"
)

# =============================================================================
# FUNCTIONS
# =============================================================================

show_usage() {
    echo "Usage: $0 <episode_number>"
    echo ""
    echo "Arguments:"
    echo "  episode_number  - The BGE episode number (e.g., 6)"
    echo ""
    echo "Example:"
    echo "  $0 6"
    echo ""
    echo "This will generate a video with all quotes (claude, openai, deepseek, llama)"
    echo "using different voices for each quote."
    echo ""
    echo "Configuration can be customized at the top of this script."
    exit 1
}

cleanup() {
    echo "Cleaning up temporary files..."
    rm -rf "${TEMP_DIR}"
}

# Parse markdown frontmatter to extract a value
get_frontmatter_value() {
    local file="$1"
    local key="$2"
    
    # Extract value between --- markers, handling multi-line quoted strings
    awk -v key="$key" '
    /^---$/ { in_frontmatter = !in_frontmatter; next }
    in_frontmatter && $0 ~ "^"key":" {
        sub("^"key": *", "")
        # Remove surrounding quotes if present
        gsub(/^["'\'']|["'\'']$/, "")
        # Handle multi-line quoted strings
        if (/^["'\'']/) {
            gsub(/^["'\'']/, "")
            value = $0
            while (!/["'\'']$/ && getline > 0) {
                value = value " " $0
            }
            gsub(/["'\'']$/, "", value)
            print value
        } else {
            print
        }
        exit
    }
    ' "$file"
}

# Get the quote from markdown file based on source
get_quote() {
    local file="$1"
    local source="$2"
    local quote_key="quote_${source}"
    
    # Parse the frontmatter for the quote
    awk -v key="$quote_key" '
    BEGIN { in_frontmatter = 0; found = 0; quote = "" }
    /^---$/ { 
        if (in_frontmatter && found) exit
        in_frontmatter = !in_frontmatter
        next 
    }
    in_frontmatter && $0 ~ "^"key":" {
        found = 1
        sub("^"key": *", "")
        # Handle quoted string starting on same line
        if (/^["'\'']/) {
            gsub(/^["'\'']/, "")
            gsub(/["'\'']$/, "")
            gsub(/\\n$/, "")
        }
        quote = $0
        next
    }
    in_frontmatter && found && /^[a-z_]+:/ { exit }
    in_frontmatter && found {
        # Continue multi-line value
        gsub(/^[ \t]+/, "")
        gsub(/["'\'']$/, "")
        gsub(/\\n$/, "")
        if (quote != "") quote = quote " "
        quote = quote $0
    }
    END { 
        # Clean up the quote
        gsub(/^["'\'']|["'\'']$/, "", quote)
        gsub(/\\n/, "", quote)
        gsub(/[ \t]+$/, "", quote)
        print quote
    }
    ' "$file"
}

# Get episode title from markdown file
get_title() {
    local file="$1"
    
    awk '
    /^---$/ { in_frontmatter = !in_frontmatter; next }
    in_frontmatter && /^titolo:/ {
        sub("^titolo: *", "")
        gsub(/^["'\'']|["'\'']$/, "")
        print
        exit
    }
    ' "$file"
}

# Select a random music file from the music directory
get_random_music() {
    local music_dir="$1"
    
    if [[ ! -d "$music_dir" ]]; then
        echo ""
        return
    fi
    
    local music_files=("$music_dir"/*.mp3)
    
    if [[ ${#music_files[@]} -eq 0 || ! -f "${music_files[0]}" ]]; then
        echo ""
        return
    fi
    
    local random_index=$((RANDOM % ${#music_files[@]}))
    echo "${music_files[$random_index]}"
}

# Generate TTS audio for the quote using OpenAI API
generate_tts() {
    local text="$1"
    local output_file="$2"
    local voice="${3:-onyx}"
    
    echo "Generating TTS audio with voice: $voice..."
    
    case "$TTS_ENGINE" in
        openai)
            # OpenAI TTS API (requires OPENAI_API_KEY environment variable)
            if [[ -z "$OPENAI_API_KEY" ]]; then
                echo "Error: OPENAI_API_KEY environment variable not set"
                exit 1
            fi
            
            # Create temporary JSON file for the request
            local json_file="${TEMP_DIR}/tts_request.json"
            local text_file="${TEMP_DIR}/tts_text.txt"
            # Write text to file to avoid escaping issues
            printf '%s' "$text" > "$text_file"
            python3 -c "
import json
import sys
with open('$text_file', 'r') as f:
    text = f.read()
# Clean up any remaining escape sequences
text = text.replace('\\\\', '').replace('\\\"', '\"').strip()
data = {
    'model': 'tts-1',
    'input': text,
    'voice': '$voice',
    'response_format': 'mp3'
}
print(json.dumps(data))
" > "$json_file"
            
            curl -s -X POST "https://api.openai.com/v1/audio/speech" \
                -H "Authorization: Bearer $OPENAI_API_KEY" \
                -H "Content-Type: application/json" \
                -d @"$json_file" \
                --output "$output_file"
            
            rm -f "$json_file" "$text_file"
            ;;
        gtts)
            # Google Text-to-Speech (requires: pip install gtts)
            local text_file="${TEMP_DIR}/tts_text.txt"
            printf '%s' "$text" > "$text_file"
            python3 -c "
from gtts import gTTS
import sys
with open('$text_file', 'r') as f:
    text = f.read()
text = text.replace('\\\\', '').replace('\\\"', '\"').strip()
tts = gTTS(text=text, lang='it')
tts.save('$output_file')
"
            rm -f "$text_file"
            ;;
        espeak)
            # eSpeak (usually pre-installed on Linux)
            espeak -v it -w "$output_file" "$text"
            ;;
        piper)
            # Piper TTS (requires piper-tts installed)
            echo "$text" | piper --model it_IT-riccardo-x_low --output_file "$output_file"
            ;;
        *)
            echo "Unknown TTS engine: $TTS_ENGINE"
            exit 1
            ;;
    esac
    
    # Verify the file was created
    if [[ ! -f "$output_file" ]]; then
        echo "Error: Failed to generate TTS audio"
        exit 1
    fi
}

# Get audio duration in seconds
get_audio_duration() {
    local file="$1"
    ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file" 2>/dev/null
}

# Word wrap text to fit within max width and add newlines for ffmpeg
wrap_text_for_ffmpeg() {
    local text="$1"
    local max_chars="${2:-$QUOTE_MAX_CHARS}"
    
    # Use fold to wrap text, then join with escaped newlines
    echo "$text" | fold -s -w "$max_chars" | sed ':a;N;$!ba;s/\n/\\n/g'
}

# Escape text for ffmpeg drawtext filter
escape_for_ffmpeg() {
    local text="$1"
    # Escape special characters for ffmpeg drawtext
    # Order matters: escape backslashes first, but preserve \n for newlines
    # First, temporarily replace \n with a placeholder
    text="${text//\\n/__NEWLINE__}"
    text="${text//\\/\\\\}"
    # Restore newlines
    text="${text//__NEWLINE__/\\n}"
    # Escape single quotes by doubling them (ffmpeg drawtext convention)
    text="${text//\'/\'\'}"
    text="${text//:/\\:}"
    text="${text//\"/\\\"}"
    text="${text//[/\\[}"
    text="${text//]/\\]}"
    text="${text//;/\\;}"
    text="${text//,/\\,}"
    echo "$text"
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

# Check arguments
if [[ $# -lt 1 ]]; then
    show_usage
fi

EPISODE_NUMBER="$1"

# Set up file paths
EPISODE_FILE="${EPISODES_DIR}/${EPISODE_NUMBER}.md"
COVER_IMAGE="${COVERS_DIR}/BGE ${EPISODE_NUMBER}.png"
OUTPUT_VIDEO="${OUTPUT_DIR}/BGE_${EPISODE_NUMBER}_quotes.mp4"

# Check required files exist
if [[ ! -f "$EPISODE_FILE" ]]; then
    echo "Error: Episode file not found: $EPISODE_FILE"
    exit 1
fi

if [[ ! -f "$COVER_IMAGE" ]]; then
    echo "Error: Cover image not found: $COVER_IMAGE"
    exit 1
fi

if [[ ! -f "$FONT_FILE" ]]; then
    echo "Warning: Font file not found: $FONT_FILE"
    echo "Using system default font"
    FONT_FILE="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fi

# Create directories
mkdir -p "${TEMP_DIR}"
mkdir -p "${OUTPUT_DIR}"

# Set up cleanup trap
trap cleanup EXIT

echo "=========================================="
echo "BGE Quote Video Generator (All Quotes)"
echo "=========================================="
echo "Episode: $EPISODE_NUMBER"
echo ""

# Extract title from episode file
TITLE=$(get_title "$EPISODE_FILE")
echo "Title: $TITLE"
echo ""

# Collect all quotes and generate TTS for each
declare -a QUOTES
declare -a TTS_FILES
declare -a TTS_DURATIONS
declare -a AUTHORS
TOTAL_TTS_DURATION=0

echo "Processing quotes..."
for source in "${QUOTE_SOURCES[@]}"; do
    QUOTE=$(get_quote "$EPISODE_FILE" "$source")
    
    if [[ -z "$QUOTE" ]]; then
        echo "Warning: No quote_${source} found, skipping..."
        continue
    fi
    
    AUTHOR_NAME="${AUTHOR_NAMES[$source]}"
    VOICE="${OPENAI_VOICES[$source]}"
    
    echo ""
    echo "Quote ($source - $AUTHOR_NAME):"
    echo "  $QUOTE"
    
    # Generate TTS
    TTS_FILE="${TEMP_DIR}/quote_${source}.mp3"
    generate_tts "$QUOTE" "$TTS_FILE" "$VOICE"
    
    # Get duration
    TTS_DURATION=$(get_audio_duration "$TTS_FILE")
    TTS_DURATION_INT=${TTS_DURATION%.*}
    
    echo "  Duration: ${TTS_DURATION}s"
    
    QUOTES+=("$QUOTE")
    TTS_FILES+=("$TTS_FILE")
    TTS_DURATIONS+=("$TTS_DURATION")
    AUTHORS+=("$AUTHOR_NAME")
    
    TOTAL_TTS_DURATION=$(echo "$TOTAL_TTS_DURATION + $TTS_DURATION" | bc)
done

NUM_QUOTES=${#QUOTES[@]}
if [[ $NUM_QUOTES -eq 0 ]]; then
    echo "Error: No quotes found in episode file"
    exit 1
fi

echo ""
echo "Total quotes: $NUM_QUOTES"
echo "Total TTS duration: ${TOTAL_TTS_DURATION}s"

# Get random music
echo ""
echo "Selecting background music..."
MUSIC_FILE=$(get_random_music "$MUSIC_DIR")
if [[ -n "$MUSIC_FILE" ]]; then
    echo "Music: $(basename "$MUSIC_FILE")"
else
    echo "Warning: No music files found in $MUSIC_DIR"
fi

# Calculate video duration with padding
PADDING_PER_QUOTE=3  # seconds of padding between quotes
VIDEO_DURATION=$(echo "$TOTAL_TTS_DURATION + ($NUM_QUOTES * $PADDING_PER_QUOTE) + 2" | bc)
VIDEO_DURATION_INT=${VIDEO_DURATION%.*}
echo "Video Duration: ${VIDEO_DURATION_INT}s"

# Concatenate all TTS files with silence between them
echo ""
echo "Concatenating audio files..."
CONCAT_FILE="${TEMP_DIR}/concat_list.txt"
COMBINED_AUDIO="${TEMP_DIR}/combined_voice.mp3"

# Create silence file
SILENCE_FILE="${TEMP_DIR}/silence.mp3"
ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 2 -q:a 9 -acodec libmp3lame "$SILENCE_FILE" 2>/dev/null

# Build concat list with silence between quotes
> "$CONCAT_FILE"
for i in "${!TTS_FILES[@]}"; do
    echo "file '${TTS_FILES[$i]}'" >> "$CONCAT_FILE"
    if [[ $i -lt $((NUM_QUOTES - 1)) ]]; then
        echo "file '$SILENCE_FILE'" >> "$CONCAT_FILE"
    fi
done

# Concatenate
ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" -c copy "$COMBINED_AUDIO" 2>/dev/null

# Calculate timing for each quote display
echo ""
echo "Building video filters..."

# Calculate when each quote should appear
declare -a QUOTE_START_TIMES
declare -a QUOTE_END_TIMES
CURRENT_TIME=1.5  # Start after initial delay

for i in "${!TTS_DURATIONS[@]}"; do
    QUOTE_START_TIMES+=("$CURRENT_TIME")
    DURATION=${TTS_DURATIONS[$i]}
    END_TIME=$(echo "$CURRENT_TIME + $DURATION + 1" | bc)
    QUOTE_END_TIMES+=("$END_TIME")
    CURRENT_TIME=$(echo "$END_TIME + 1" | bc)  # 1 second gap
done

# Build background image filter (resize without distortion, place at bottom)
# Scale image to fit width, then overlay on black background at the bottom
BG_FILTER="color=c=${BACKGROUND_COLOR}:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:d=${VIDEO_DURATION_INT}[bg];[0:v]scale=${VIDEO_WIDTH}:-1,format=yuv420p[scaled];[bg][scaled]overlay=0:H-h[bgout]"

# Build text overlay filters for each quote
FILTER_COMPLEX="${BG_FILTER}"

# Add episode number at top (always visible)
EPISODE_TEXT="BGE ${EPISODE_NUMBER}"
FILTER_COMPLEX="${FILTER_COMPLEX};[bgout]drawtext=fontfile='${FONT_FILE}':text='${EPISODE_TEXT}':fontsize=${EPISODE_FONT_SIZE}:fontcolor=${EPISODE_FONT_COLOR}:x=(w-text_w)/2:y=40[v0]"

LAST_FILTER="v0"
FILTER_IDX=1

for i in "${!QUOTES[@]}"; do
    QUOTE="${QUOTES[$i]}"
    AUTHOR="${AUTHORS[$i]}"
    START_TIME="${QUOTE_START_TIMES[$i]}"
    END_TIME="${QUOTE_END_TIMES[$i]}"
    
    # Wrap and escape text
    WRAPPED_QUOTE=$(wrap_text_for_ffmpeg "$QUOTE" "$QUOTE_MAX_CHARS")
    QUOTE_ESCAPED=$(escape_for_ffmpeg "$WRAPPED_QUOTE")
    AUTHOR_ESCAPED=$(escape_for_ffmpeg "— $AUTHOR")
    
    # Add quote text (left-aligned with padding)
    FILTER_COMPLEX="${FILTER_COMPLEX};[${LAST_FILTER}]drawtext=fontfile='${FONT_FILE}':text='${QUOTE_ESCAPED}':fontsize=${QUOTE_FONT_SIZE}:fontcolor=${QUOTE_FONT_COLOR}:x=${QUOTE_PADDING_LEFT}:y=${QUOTE_Y}:enable='between(t,${START_TIME},${END_TIME})':box=1:boxcolor=${QUOTE_BOX_COLOR}:boxborderw=${QUOTE_BOX_BORDER}[v${FILTER_IDX}]"
    
    LAST_FILTER="v${FILTER_IDX}"
    FILTER_IDX=$((FILTER_IDX + 1))
    
    # Add author name (left-aligned, below quote area)
    AUTHOR_Y=$((QUOTE_Y + 400))  # Position below quote
    FILTER_COMPLEX="${FILTER_COMPLEX};[${LAST_FILTER}]drawtext=fontfile='${FONT_FILE}':text='${AUTHOR_ESCAPED}':fontsize=${AUTHOR_FONT_SIZE}:fontcolor=${AUTHOR_FONT_COLOR}:x=${AUTHOR_PADDING_LEFT}:y=${AUTHOR_Y}:enable='between(t,${START_TIME},${END_TIME})'[v${FILTER_IDX}]"
    
    LAST_FILTER="v${FILTER_IDX}"
    FILTER_IDX=$((FILTER_IDX + 1))
done

# Rename last filter to vout
FILTER_COMPLEX="${FILTER_COMPLEX};[${LAST_FILTER}]null[vout]"

# Build audio mix
echo "Building audio mix..."

# Build ffmpeg command
FFMPEG_CMD=(ffmpeg -y -loop 1 -i "${COVER_IMAGE}" -i "${COMBINED_AUDIO}")

if [[ -n "$MUSIC_FILE" && -f "$MUSIC_FILE" ]]; then
    # Mix combined voice with background music
    AUDIO_FILTER="[1:a]adelay=1500|1500,volume=${VOICE_VOLUME}[voice];[2:a]volume=${MUSIC_VOLUME},afade=t=out:st=$((VIDEO_DURATION_INT - 2)):d=2[music];[voice][music]amix=inputs=2:duration=longest[aout]"
    FFMPEG_CMD+=(-i "${MUSIC_FILE}")
else
    # Voice only
    AUDIO_FILTER="[1:a]adelay=1500|1500,volume=${VOICE_VOLUME},apad=whole_dur=${VIDEO_DURATION_INT}[aout]"
fi

# Generate video
echo ""
echo "Generating video..."
echo "Output: $OUTPUT_VIDEO"

"${FFMPEG_CMD[@]}" \
    -filter_complex "${FILTER_COMPLEX};${AUDIO_FILTER}" \
    -map "[vout]" -map "[aout]" \
    -c:v libx264 -preset medium -crf 23 \
    -c:a aac -b:a 192k \
    -t ${VIDEO_DURATION_INT} \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "${OUTPUT_VIDEO}"

echo ""
echo "=========================================="
echo "Video generated successfully!"
echo "Output: $OUTPUT_VIDEO"
echo "Duration: ${VIDEO_DURATION_INT}s"
echo "Quotes: $NUM_QUOTES"
echo "=========================================="
