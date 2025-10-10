#!/usr/bin/env python3
"""
BGE Social Quote Generator - CLI Entry Point

Command-line interface for generating and publishing quote images
from BGE podcast episodes to social media platforms.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .config import Config, ConfigurationError
from .orchestrator import PipelineOrchestrator
from .utils.validators import EpisodeValidator, ConfigValidator, PathValidator, ValidationError


# Version information
__version__ = "1.0.0"


def find_config_file(config_arg: str) -> str:
    """
    Find the configuration file, trying multiple locations.
    
    Args:
        config_arg: Config path from command line argument
        
    Returns:
        Absolute path to config file
        
    Raises:
        FileNotFoundError: If config file cannot be found
    """
    # If absolute path provided, use it directly
    config_path = Path(config_arg)
    if config_path.is_absolute():
        if config_path.exists():
            return str(config_path)
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Try multiple locations relative to different base paths
    search_paths = [
        # 1. Relative to current working directory
        Path.cwd() / config_arg,
        # 2. Relative to project root (assuming we're in a subdirectory)
        Path.cwd() / "social-quote-generator" / config_arg,
        # 3. Relative to this file's location (package installation)
        Path(__file__).parent.parent.parent / config_arg,
        # 4. Default config location
        Path.cwd() / "social-quote-generator" / "config" / "config.yaml",
        # 5. Config in package directory
        Path(__file__).parent.parent.parent / "config" / "config.yaml",
    ]
    
    for path in search_paths:
        if path.exists():
            return str(path.resolve())
    
    # If nothing found, provide helpful error message
    tried_paths = "\n  - ".join(str(p) for p in search_paths)
    raise FileNotFoundError(
        f"Config file not found. Tried:\n  - {tried_paths}\n\n"
        f"Please specify the full path with --config option."
    )


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_episode_list(episodes_arg: str) -> List[str]:
    """
    Parse comma-separated episode numbers.
    
    Args:
        episodes_arg: Comma-separated episode numbers (e.g., "1,5,10")
        
    Returns:
        List of episode number strings
        
    Raises:
        ValueError: If episode numbers are invalid
    """
    episodes = []
    for ep in episodes_arg.split(','):
        ep = ep.strip()
        if not ep:
            continue
        try:
            # Use EpisodeValidator to validate each episode number
            validated_ep = EpisodeValidator.validate_episode_number(ep)
            episodes.append(validated_ep)
        except ValidationError as e:
            raise ValueError(str(e))
    
    if not episodes:
        raise ValueError("No valid episode numbers provided")
    
    return episodes


def validate_platform(platform: str) -> str:
    """
    Validate platform name.
    
    Args:
        platform: Platform name to validate
        
    Returns:
        Validated platform name (lowercase)
        
    Raises:
        ValueError: If platform is not supported
    """
    try:
        return ConfigValidator.validate_platform(platform)
    except ValidationError as e:
        raise ValueError(str(e))


def validate_quote_source(source: str) -> str:
    """
    Validate quote source.
    
    Args:
        source: Quote source to validate
        
    Returns:
        Validated quote source (lowercase)
        
    Raises:
        ValueError: If source is not supported
    """
    try:
        return ConfigValidator.validate_quote_source(source)
    except ValidationError as e:
        raise ValueError(str(e))


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='bge-quote-gen',
        description='Generate and publish quote images from BGE podcast episodes',
        epilog='For more information, see the README.md file.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # Episode selection (mutually exclusive group)
    episode_group = parser.add_mutually_exclusive_group(required=True)
    
    episode_group.add_argument(
        '--episode', '-e',
        type=str,
        metavar='N',
        help='Process a single episode by number (e.g., --episode 42)'
    )
    
    episode_group.add_argument(
        '--episodes',
        type=str,
        metavar='N,M,P',
        help='Process multiple episodes (comma-separated, e.g., --episodes 1,5,10)'
    )
    
    episode_group.add_argument(
        '--all', '-a',
        action='store_true',
        help='Process all available episodes'
    )
    
    # Platform selection
    parser.add_argument(
        '--platform', '-p',
        type=str,
        metavar='PLATFORM',
        help='Generate images for specific platform (instagram, twitter, facebook, linkedin)'
    )
    
    # Publishing options
    publish_group = parser.add_mutually_exclusive_group()
    
    publish_group.add_argument(
        '--publish',
        action='store_true',
        help='Publish generated images to social media platforms'
    )
    
    publish_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate images without publishing (default behavior)'
    )
    
    # Configuration options
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.yaml',
        metavar='PATH',
        help='Path to configuration file (default: config/config.yaml, searches multiple locations)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        metavar='PATH',
        help='Override output directory for generated images'
    )
    
    parser.add_argument(
        '--quote-source',
        type=str,
        metavar='SOURCE',
        help='Preferred quote source (claude, openai, deepseek, llama, random)'
    )
    
    # Logging options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    # Queue management options
    parser.add_argument(
        '--queue',
        action='store_true',
        help='Add generated images to publishing queue instead of publishing immediately'
    )
    
    parser.add_argument(
        '--schedule',
        type=str,
        metavar='DATETIME',
        help='Schedule time for queue (e.g., "2025-10-13 09:00", "+2d", "tomorrow 9am")'
    )
    
    parser.add_argument(
        '--stagger',
        type=str,
        metavar='INTERVAL',
        help='Stagger posts across platforms (e.g., "6h", "30m", "1d")'
    )
    
    parser.add_argument(
        '--queue-list',
        action='store_true',
        help='List all pending items in queue'
    )
    
    parser.add_argument(
        '--queue-history',
        action='store_true',
        help='Show published items history'
    )
    
    parser.add_argument(
        '--queue-failed',
        action='store_true',
        help='Show failed items'
    )
    
    parser.add_argument(
        '--queue-remove',
        type=str,
        metavar='ID',
        help='Remove item from queue by ID'
    )
    
    parser.add_argument(
        '--queue-publish',
        action='store_true',
        help='Publish pending items from queue (for cron jobs)'
    )
    
    parser.add_argument(
        '--queue-publish-now',
        type=str,
        metavar='ID',
        help='Publish specific queue item immediately'
    )
    
    parser.add_argument(
        '--history-limit',
        type=int,
        default=10,
        metavar='N',
        help='Number of history items to show (default: 10)'
    )
    
    return parser


def main() -> int:
    """
    Main entry point for the CLI application.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Parse command-line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Handle queue management commands first (they don't need episode selection)
        if args.queue_list or args.queue_history or args.queue_failed or args.queue_remove or args.queue_publish or args.queue_publish_now:
            # Load configuration
            try:
                config_path = find_config_file(args.config)
                logger.info(f"Loading configuration from: {config_path}")
                config = Config(config_path)
            except FileNotFoundError as e:
                logger.error(str(e))
                return 1
            except ConfigurationError as e:
                logger.error(f"Configuration error: {e}")
                return 1
            
            # Import queue commands
            from .queue.cli_commands import QueueCommands
            queue_commands = QueueCommands(config)
            
            # Execute queue command
            if args.queue_list:
                queue_commands.list_queue()
                return 0
            elif args.queue_history:
                queue_commands.list_history(args.history_limit)
                return 0
            elif args.queue_failed:
                queue_commands.list_failed()
                return 0
            elif args.queue_remove:
                return 0 if queue_commands.remove_from_queue(args.queue_remove) else 1
            elif args.queue_publish:
                results = queue_commands.publish_queue(args.dry_run)
                return 0 if results["published"] > 0 or results["total"] == 0 else 1
            elif args.queue_publish_now:
                return 0 if queue_commands.publish_now(args.queue_publish_now, args.dry_run) else 1
        
        # Regular episode processing requires episode selection
        if not (args.episode or args.episodes or args.all):
            logger.error("Episode selection required (use --episode, --episodes, or --all)")
            parser.print_help()
            return 1
        # Display banner
        logger.info("=" * 60)
        logger.info("BGE Social Quote Generator v%s", __version__)
        logger.info("=" * 60)
        
        # Validate and parse episode selection
        episode_numbers: Optional[List[str]] = None
        
        if args.episode:
            # Single episode - validate using EpisodeValidator
            try:
                validated_episode = EpisodeValidator.validate_episode_number(args.episode)
                episode_numbers = [validated_episode]
                logger.info(f"Processing episode: {validated_episode}")
            except ValidationError as e:
                logger.error(f"Invalid episode number: {e}")
                return 1
            
        elif args.episodes:
            # Multiple episodes
            try:
                episode_numbers = parse_episode_list(args.episodes)
                logger.info(f"Processing episodes: {', '.join(episode_numbers)}")
            except ValueError as e:
                logger.error(str(e))
                return 1
                
        elif args.all:
            # All episodes
            episode_numbers = None
            logger.info("Processing all episodes")
        
        # Validate platform if specified
        platforms: Optional[List[str]] = None
        if args.platform:
            try:
                platform = validate_platform(args.platform)
                platforms = [platform]
                logger.info(f"Target platform: {platform}")
            except ValueError as e:
                logger.error(str(e))
                return 1
        else:
            logger.info("Target platforms: all configured")
        
        # Validate quote source if specified
        if args.quote_source:
            try:
                quote_source = validate_quote_source(args.quote_source)
                logger.info(f"Quote source: {quote_source}")
            except ValueError as e:
                logger.error(str(e))
                return 1
        
        # Determine publish mode
        publish = args.publish
        dry_run = args.dry_run or not args.publish
        
        if publish:
            logger.info("Mode: PUBLISH (images will be posted to social media)")
        else:
            logger.info("Mode: DRY RUN (images will be generated only)")
        
        # Find and load configuration
        try:
            config_path = find_config_file(args.config)
            logger.info(f"Loading configuration from: {config_path}")
            config = Config(config_path)
        except FileNotFoundError as e:
            logger.error(str(e))
            return 1
        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            return 1
        
        # Apply command-line overrides to configuration
        if args.output_dir:
            # Validate output directory path
            try:
                PathValidator.validate_directory_path(args.output_dir, "output directory")
                logger.info(f"Overriding output directory: {args.output_dir}")
                config.override_output_dir(args.output_dir)
            except ValidationError as e:
                logger.error(f"Invalid output directory: {e}")
                return 1
        
        if args.quote_source:
            try:
                logger.info(f"Overriding quote source: {args.quote_source}")
                config.override_quote_source(args.quote_source)
            except ConfigurationError as e:
                logger.error(f"Invalid quote source: {e}")
                return 1
        
        # Check if we should add to queue instead of publishing
        if args.queue:
            # Queue mode - generate images and add to queue
            from .queue.cli_commands import QueueCommands
            queue_commands = QueueCommands(config)
            
            # Process each episode
            success_count = 0
            for episode_num in episode_numbers or []:
                if queue_commands.add_to_queue(
                    episode_num,
                    platforms,
                    args.schedule,
                    args.stagger
                ):
                    success_count += 1
            
            if success_count > 0:
                logger.info(f"\n✓ Successfully added {success_count} episode(s) to queue")
                return 0
            else:
                logger.error("\n✗ Failed to add episodes to queue")
                return 1
        
        # Regular mode - generate and optionally publish immediately
        # Initialize orchestrator
        logger.info("Initializing pipeline orchestrator...")
        orchestrator = PipelineOrchestrator(config)
        
        # Run pipeline
        result = orchestrator.run(
            episode_numbers=episode_numbers,
            platforms=platforms,
            publish=publish,
            dry_run=dry_run
        )
        
        # Display results
        print("\n" + result.get_summary())
        
        # Determine exit code based on results
        if result.total_episodes == 0:
            logger.warning("No episodes were processed")
            return 1
        
        if result.successful_images == 0:
            logger.error("No images were generated successfully")
            return 1
        
        if publish and result.successful_posts == 0:
            logger.warning("No posts were published successfully")
            return 1
        
        # Success
        logger.info("Pipeline completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        return 130  # Standard exit code for SIGINT
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
