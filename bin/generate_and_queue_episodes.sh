#!/bin/bash

# BGE Quote Generator - Batch Image Generation and Queue Creation
# Generates images for episodes 1-98 and creates publishing queue
# Starting from Monday, October 13, 2025
# Publishing 2 quotes per day on all platforms

set -e  # Exit on error

# Configuration
START_EPISODE=1
END_EPISODE=98
START_DATE="2025-10-13"  # Monday, October 13, 2025
QUOTES_PER_DAY=2
PLATFORMS=("twitter" "instagram" "linkedin" "facebook")

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BGE Quote Generator - Batch Processing${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Episodes:${NC} $START_EPISODE to $END_EPISODE"
echo -e "${GREEN}Start Date:${NC} $START_DATE"
echo -e "${GREEN}Quotes per Day:${NC} $QUOTES_PER_DAY"
echo -e "${GREEN}Platforms:${NC} ${PLATFORMS[@]}"
echo ""

# Step 1: Generate all images
echo -e "${BLUE}Step 1: Generating quote images for all episodes${NC}"
echo -e "${YELLOW}This may take a while...${NC}"
echo ""

for episode in $(seq $START_EPISODE $END_EPISODE); do
    echo -e "${GREEN}Generating images for episode $episode...${NC}"
    
    # Generate images for all platforms
    if bge-quote-gen --episode "$episode" 2>&1; then
        echo -e "${GREEN}✓ Episode $episode images generated${NC}"
    else
        echo -e "${RED}✗ Failed to generate images for episode $episode${NC}"
        echo -e "${YELLOW}Continuing with next episode...${NC}"
    fi
    echo ""
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Image generation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Step 2: Create publishing queue
echo -e "${BLUE}Step 2: Creating publishing queue${NC}"
echo ""

# Calculate total number of posts
TOTAL_EPISODES=$((END_EPISODE - START_EPISODE + 1))
TOTAL_POSTS=$((TOTAL_EPISODES * ${#PLATFORMS[@]}))
TOTAL_DAYS=$((TOTAL_POSTS / QUOTES_PER_DAY))

echo -e "${GREEN}Total posts to schedule:${NC} $TOTAL_POSTS"
echo -e "${GREEN}Total days needed:${NC} $TOTAL_DAYS days"
echo ""

# Create array of all episode-platform combinations
declare -a queue_items=()
for episode in $(seq $START_EPISODE $END_EPISODE); do
    for platform in "${PLATFORMS[@]}"; do
        queue_items+=("$episode:$platform")
    done
done

# Schedule posts
current_date="$START_DATE"
posts_today=0
item_index=0

echo -e "${YELLOW}Scheduling posts...${NC}"
echo ""

while [ $item_index -lt ${#queue_items[@]} ]; do
    # Get episode and platform
    IFS=':' read -r episode platform <<< "${queue_items[$item_index]}"
    
    # Calculate time for this post (stagger throughout the day)
    if [ $posts_today -eq 0 ]; then
        schedule_time="09:00"
    else
        schedule_time="15:00"
    fi
    
    full_schedule="$current_date $schedule_time"
    
    echo -e "${GREEN}Scheduling:${NC} Episode $episode on $platform for $full_schedule"
    
    # Add to queue
    if bge-quote-gen --episode "$episode" --platform "$platform" --queue --schedule "$full_schedule" 2>&1; then
        echo -e "${GREEN}✓ Added to queue${NC}"
    else
        echo -e "${RED}✗ Failed to add to queue${NC}"
    fi
    
    # Increment counters
    ((item_index++))
    ((posts_today++))
    
    # Move to next day if we've scheduled enough posts
    if [ $posts_today -ge $QUOTES_PER_DAY ]; then
        posts_today=0
        # Add one day to current_date (macOS compatible)
        current_date=$(date -j -v+1d -f "%Y-%m-%d" "$current_date" "+%Y-%m-%d" 2>/dev/null || date -d "$current_date + 1 day" "+%Y-%m-%d")
        echo ""
    fi
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Queue creation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Step 3: Show queue summary
echo -e "${BLUE}Step 3: Queue Summary${NC}"
echo ""
bge-quote-gen --queue-list

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All done!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Review the queue: ${BLUE}bge-quote-gen --queue-list${NC}"
echo -e "2. Edit queue file if needed: ${BLUE}nano social-quote-generator/output/publish_queue.json${NC}"
echo -e "3. Test publishing: ${BLUE}bge-quote-gen --queue-publish --dry-run${NC}"
echo -e "4. Set up cron job for automated publishing (see QUEUE_GUIDE.md)"
echo ""
echo -e "${GREEN}Publishing will start on: $START_DATE${NC}"
echo -e "${GREEN}Publishing will end approximately on: $current_date${NC}"
echo ""
