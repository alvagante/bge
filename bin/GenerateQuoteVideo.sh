#!/bin/bash
#
# GenerateQuoteVideo.sh
# Creates a short vertical video with quote from BGE episode
#
# Usage: ./GenerateQuoteVideo.sh <episode_number> <quote_source>
# Example: ./GenerateQuoteVideo.sh 6 claude
#
# Quote sources: claude, openai, deepseek, llama
#

set -e

# =============================================================================
# CONFIGURATION - Easy customization section
# =============================================================================

# Directories (adjust these paths as needed)
BASE_DIR="/home/al/bge"
EPISODES_DIR="${BASE_DIR}/_episodes"
COVERS_DIR="${BASE_DIR}/assets/covers"
FONTS_DIR="${BASE_DIR}/assets/fonts"
MUSIC_DIR="${BASE_DIR}/assets/music"         # Directory with background music mp3 files
OUTPUT_DIR="${BASE_DIR}/assets/videos"       # Output directory for generated videos
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
QUOTE_FONT_SIZE=48
QUOTE_FONT_COLOR="white"
QUOTE_BOX_COLOR="black@0.6"                   # Semi-transparent background
QUOTE_BOX_BORDER=20
QUOTE_X="(w-text_w)/2"                        # Centered horizontally
QUOTE_Y="(h*0.55)"                            # Below center
QUOTE_MAX_WIDTH=900                           # Maximum width for text wrapping

# Episode title settings
TITLE_FONT_SIZE=36
TITLE_FONT_COLOR="white"
TITLE_X="(w-text_w)/2"
TITLE_Y="100"

# Episode number settings
EPISODE_FONT_SIZE=72
EPISODE_FONT_COLOR="#FFD700"                  # Gold color
EPISODE_X="(w-text_w)/2"
EPISODE_Y="40"

# Author settings
AUTHOR_FONT_SIZE=32
AUTHOR_FONT_COLOR="#AAAAAA"                   # Light gray
AUTHOR_X="(w-text_w)/2"
AUTHOR_Y="(h*0.85)"

# Audio settings
MUSIC_VOLUME=0.15                             # Background music volume (0.0 - 1.0)
VOICE_VOLUME=1.0                              # TTS voice volume
TTS_ENGINE="gtts"                             # Options: gtts, espeak, piper

# Image effects (comma-separated list for random selection)
IMAGE_EFFECTS="zoompan,ken_burns,pulse,none"

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
    echo "Usage: $0 <episode_number> <quote_source>"
    echo ""
    echo "Arguments:"
    echo "  episode_number  - The BGE episode number (e.g., 6)"
    echo "  quote_source    - Source of the quote: claude, openai, deepseek, llama"
    echo ""
    echo "Example:"
    echo "  $0 6 claude"
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

# Select a random image effect
get_random_effect() {
    IFS=',' read -ra effects <<< "$IMAGE_EFFECTS"
    local random_index=$((RANDOM % ${#effects[@]}))
    echo "${effects[$random_index]}"
}

# Generate TTS audio for the quote
generate_tts() {
    local text="$1"
    local output_file="$2"
    
    echo "Generating TTS audio..."
    
    case "$TTS_ENGINE" in
        gtts)
            # Google Text-to-Speech (requires: pip install gtts)
            python3 -c "
from gtts import gTTS
import sys
text = '''$text'''
tts = gTTS(text=text, lang='it')
tts.save('$output_file')
"
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

# Word wrap text to fit within max width (approximate)
wrap_text() {
    local text="$1"
    local max_chars=40  # Approximate characters per line for the font size
    
    echo "$text" | fold -s -w "$max_chars"
}

# Escape text for ffmpeg drawtext filter
escape_for_ffmpeg() {
    local text="$1"
    # Escape special characters for ffmpeg drawtext
    text="${text//\\/\\\\}"
    text="${text//:/\\:}"
    text="${text//\'/\\\'}"
    text="${text//\"/\\\"}"
    text="${text//[/\\[}"
    text="${text//]/\\]}"
    text="${text//;/\\;}"
    text="${text//,/\\,}"
    echo "$text"
}

# Build ffmpeg filter for image effect
build_image_effect_filter() {
    local effect="$1"
    local duration="$2"
    
    case "$effect" in
        zoompan)
            # Slow zoom in effect
            echo "zoompan=z='min(zoom+0.0015,1.5)':d=$((duration * VIDEO_FPS)):s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:fps=${VIDEO_FPS}"
            ;;
        ken_burns)
            # Ken Burns effect (zoom + pan)
            echo "zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$((duration * VIDEO_FPS)):s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:fps=${VIDEO_FPS}"
            ;;
        pulse)
            # Subtle pulse/breathe effect
            echo "zoompan=z='1+0.05*sin(2*PI*in/$((VIDEO_FPS * 4)))':d=$((duration * VIDEO_FPS)):s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:fps=${VIDEO_FPS}"
            ;;
        none|*)
            # No effect, just scale
            echo "scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:${BACKGROUND_COLOR}"
            ;;
    esac
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

# Check arguments
if [[ $# -lt 2 ]]; then
    show_usage
fi

EPISODE_NUMBER="$1"
QUOTE_SOURCE="$2"

# Validate quote source
if [[ -z "${AUTHOR_NAMES[$QUOTE_SOURCE]}" ]]; then
    echo "Error: Invalid quote source '$QUOTE_SOURCE'"
    echo "Valid options: claude, openai, deepseek, llama"
    exit 1
fi

# Set up file paths
EPISODE_FILE="${EPISODES_DIR}/${EPISODE_NUMBER}.md"
COVER_IMAGE="${COVERS_DIR}/BGE ${EPISODE_NUMBER}.png"
OUTPUT_VIDEO="${OUTPUT_DIR}/BGE_${EPISODE_NUMBER}_${QUOTE_SOURCE}.mp4"

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
echo "BGE Quote Video Generator"
echo "=========================================="
echo "Episode: $EPISODE_NUMBER"
echo "Quote Source: $QUOTE_SOURCE"
echo "Author Name: ${AUTHOR_NAMES[$QUOTE_SOURCE]}"
echo ""

# Extract data from episode file
echo "Parsing episode file..."
QUOTE=$(get_quote "$EPISODE_FILE" "$QUOTE_SOURCE")
TITLE=$(get_title "$EPISODE_FILE")
AUTHOR_NAME="${AUTHOR_NAMES[$QUOTE_SOURCE]}"

if [[ -z "$QUOTE" ]]; then
    echo "Error: Could not extract quote_${QUOTE_SOURCE} from episode file"
    exit 1
fi

echo "Quote: $QUOTE"
echo "Title: $TITLE"
echo ""

# Get random music
echo "Selecting background music..."
MUSIC_FILE=$(get_random_music "$MUSIC_DIR")
if [[ -n "$MUSIC_FILE" ]]; then
    echo "Music: $(basename "$MUSIC_FILE")"
else
    echo "Warning: No music files found in $MUSIC_DIR"
fi

# Generate TTS audio
TTS_FILE="${TEMP_DIR}/quote_voice.mp3"
generate_tts "$QUOTE" "$TTS_FILE"

# Get TTS duration and calculate video duration
TTS_DURATION=$(get_audio_duration "$TTS_FILE")
TTS_DURATION_INT=${TTS_DURATION%.*}
VIDEO_DURATION=$((TTS_DURATION_INT + 4))  # Add padding
if [[ $VIDEO_DURATION -lt $VIDEO_DURATION_MIN ]]; then
    VIDEO_DURATION=$VIDEO_DURATION_MIN
fi
echo "TTS Duration: ${TTS_DURATION}s"
echo "Video Duration: ${VIDEO_DURATION}s"

# Select random effect
EFFECT=$(get_random_effect)
echo "Image Effect: $EFFECT"

# Escape text for ffmpeg
QUOTE_ESCAPED=$(escape_for_ffmpeg "$QUOTE")
TITLE_ESCAPED=$(escape_for_ffmpeg "$TITLE")
AUTHOR_ESCAPED=$(escape_for_ffmpeg "— $AUTHOR_NAME")
EPISODE_TEXT="BGE ${EPISODE_NUMBER}"

# Build image effect filter
EFFECT_FILTER=$(build_image_effect_filter "$EFFECT" "$VIDEO_DURATION")

# Calculate text fade timing
TEXT_FADE_IN=1       # Start showing text at 1 second
TEXT_DURATION=$((VIDEO_DURATION - 2))

# Build ffmpeg filter complex
echo "Building video filters..."

FILTER_COMPLEX="
[0:v]${EFFECT_FILTER},format=yuv420p[bg];
[bg]drawtext=fontfile='${FONT_FILE}':text='${EPISODE_TEXT}':fontsize=${EPISODE_FONT_SIZE}:fontcolor=${EPISODE_FONT_COLOR}:x=${EPISODE_X}:y=${EPISODE_Y}:enable='between(t,0.5,${VIDEO_DURATION})'[v1];
[v1]drawtext=fontfile='${FONT_FILE}':text='${TITLE_ESCAPED}':fontsize=${TITLE_FONT_SIZE}:fontcolor=${TITLE_FONT_COLOR}:x=${TITLE_X}:y=${TITLE_Y}:enable='between(t,1,${VIDEO_DURATION})':box=1:boxcolor=${QUOTE_BOX_COLOR}:boxborderw=10[v2];
[v2]drawtext=fontfile='${FONT_FILE}':text='${QUOTE_ESCAPED}':fontsize=${QUOTE_FONT_SIZE}:fontcolor=${QUOTE_FONT_COLOR}:x=${QUOTE_X}:y=${QUOTE_Y}:enable='between(t,${TEXT_FADE_IN},${VIDEO_DURATION})':box=1:boxcolor=${QUOTE_BOX_COLOR}:boxborderw=${QUOTE_BOX_BORDER}[v3];
[v3]drawtext=fontfile='${FONT_FILE}':text='${AUTHOR_ESCAPED}':fontsize=${AUTHOR_FONT_SIZE}:fontcolor=${AUTHOR_FONT_COLOR}:x=${AUTHOR_X}:y=${AUTHOR_Y}:enable='between(t,2,${VIDEO_DURATION})'[vout]
"

# Build audio mix
echo "Building audio mix..."

if [[ -n "$MUSIC_FILE" && -f "$MUSIC_FILE" ]]; then
    # Mix TTS voice with background music
    AUDIO_FILTER="[1:a]adelay=${TEXT_FADE_IN}s:all=1,volume=${VOICE_VOLUME}[voice];[2:a]volume=${MUSIC_VOLUME},afade=t=out:st=$((VIDEO_DURATION - 2)):d=2[music];[voice][music]amix=inputs=2:duration=longest[aout]"
    
    AUDIO_INPUTS="-i \"${TTS_FILE}\" -i \"${MUSIC_FILE}\""
else
    # TTS only
    AUDIO_FILTER="[1:a]adelay=${TEXT_FADE_IN}s:all=1,volume=${VOICE_VOLUME},apad=whole_dur=${VIDEO_DURATION}[aout]"
    AUDIO_INPUTS="-i \"${TTS_FILE}\""
fi

# Generate video
echo ""
echo "Generating video..."
echo "Output: $OUTPUT_VIDEO"

eval ffmpeg -y \
    -loop 1 -i "\"${COVER_IMAGE}\"" \
    ${AUDIO_INPUTS} \
    -filter_complex "${FILTER_COMPLEX};${AUDIO_FILTER}" \
    -map "[vout]" -map "[aout]" \
    -c:v libx264 -preset medium -crf 23 \
    -c:a aac -b:a 192k \
    -t ${VIDEO_DURATION} \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "\"${OUTPUT_VIDEO}\""

echo ""
echo "=========================================="
echo "Video generated successfully!"
echo "Output: $OUTPUT_VIDEO"
echo "=========================================="
