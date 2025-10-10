#!/bin/bash
#
# Setup cron job for automated queue publishing
#
# Usage: ./scripts/setup_cron.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}BGE Queue Publishing - Cron Setup${NC}"
echo "======================================"
echo ""

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "Project root: $PROJECT_ROOT"

# Find Python virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    VENV_PATH="$PROJECT_ROOT/.venv"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    VENV_PATH="$PROJECT_ROOT/venv"
else
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please create a virtual environment first:"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -e social-quote-generator/"
    exit 1
fi

echo "Virtual environment: $VENV_PATH"

# Check if bge-quote-gen is installed
if [ ! -f "$VENV_PATH/bin/bge-quote-gen" ]; then
    echo -e "${RED}Error: bge-quote-gen not installed${NC}"
    echo "Please install the package first:"
    echo "  source $VENV_PATH/bin/activate"
    echo "  pip install -e social-quote-generator/"
    exit 1
fi

# Create logs directory
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
echo "Log directory: $LOG_DIR"
echo ""

# Generate cron entry
CRON_ENTRY="*/15 * * * * cd $PROJECT_ROOT && $VENV_PATH/bin/bge-quote-gen --queue-publish >> $LOG_DIR/publish.log 2>&1"

echo -e "${YELLOW}Suggested cron entry:${NC}"
echo ""
echo "$CRON_ENTRY"
echo ""

# Ask user if they want to add it
echo -e "${YELLOW}Options:${NC}"
echo "1. Add to crontab automatically"
echo "2. Show instructions for manual setup"
echo "3. Exit"
echo ""
read -p "Choose option (1-3): " choice

case $choice in
    1)
        # Check if entry already exists
        if crontab -l 2>/dev/null | grep -q "bge-quote-gen --queue-publish"; then
            echo -e "${YELLOW}Warning: A similar cron entry already exists${NC}"
            crontab -l | grep "bge-quote-gen --queue-publish"
            echo ""
            read -p "Do you want to add another entry? (y/n): " confirm
            if [ "$confirm" != "y" ]; then
                echo "Cancelled"
                exit 0
            fi
        fi
        
        # Add to crontab
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
        echo -e "${GREEN}✓ Cron entry added successfully${NC}"
        echo ""
        echo "The queue will be checked every 15 minutes"
        echo "Logs will be written to: $LOG_DIR/publish.log"
        echo ""
        echo "To view current crontab:"
        echo "  crontab -l"
        echo ""
        echo "To remove the entry:"
        echo "  crontab -e"
        ;;
        
    2)
        echo ""
        echo -e "${GREEN}Manual Setup Instructions:${NC}"
        echo ""
        echo "1. Edit your crontab:"
        echo "   crontab -e"
        echo ""
        echo "2. Add this line:"
        echo "   $CRON_ENTRY"
        echo ""
        echo "3. Save and exit"
        echo ""
        echo "Alternative schedules:"
        echo ""
        echo "# Every hour at minute 0"
        echo "0 * * * * cd $PROJECT_ROOT && $VENV_PATH/bin/bge-quote-gen --queue-publish >> $LOG_DIR/publish.log 2>&1"
        echo ""
        echo "# Three times per day (9 AM, 3 PM, 9 PM)"
        echo "0 9,15,21 * * * cd $PROJECT_ROOT && $VENV_PATH/bin/bge-quote-gen --queue-publish >> $LOG_DIR/publish.log 2>&1"
        echo ""
        echo "# Every 30 minutes"
        echo "*/30 * * * * cd $PROJECT_ROOT && $VENV_PATH/bin/bge-quote-gen --queue-publish >> $LOG_DIR/publish.log 2>&1"
        echo ""
        ;;
        
    3)
        echo "Exited without changes"
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Add episodes to queue:"
echo "   bge-quote-gen --episode 98 --queue"
echo ""
echo "2. Test publishing (dry run):"
echo "   bge-quote-gen --queue-publish --dry-run"
echo ""
echo "3. Monitor logs:"
echo "   tail -f $LOG_DIR/publish.log"
echo ""
echo "4. View queue:"
echo "   bge-quote-gen --queue-list"
echo ""

