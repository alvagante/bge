#!/usr/bin/env python3
"""
Standalone script for publishing from queue.
Designed to be run by cron jobs.

Usage:
    python scripts/publish_from_queue.py [--config path/to/config.yaml] [--dry-run] [--verbose]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bge_social_quote_generator.config import Config, ConfigurationError
from bge_social_quote_generator.queue import QueuePublisher


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Publish pending items from queue (for cron jobs)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (don\'t actually publish)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")
        config = Config(args.config)
        
        # Initialize publisher
        publisher = QueuePublisher(config)
        
        # Publish pending items
        results = publisher.publish_pending(args.dry_run)
        
        # Exit with appropriate code
        if results["total"] == 0:
            # No items to publish - this is normal
            return 0
        elif results["published"] > 0:
            # At least one item published successfully
            return 0
        else:
            # All items failed
            return 1
            
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
