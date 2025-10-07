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


# Version information
__version__ = "1.0.0"


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
        if not ep.isdigit():
            raise ValueError(f"Invalid episode number: {ep}")
        episodes.append(ep)
    
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
    valid_platforms = ["instagram", "twitter", "facebook", "linkedin"]
    platform_lower = platform.lower()
    
    if platform_lower not in valid_platforms:
        raise ValueError(
            f"Invalid platform: {platform}. "
            f"Valid options: {', '.join(valid_platforms)}"
        )
    
    return platform_lower


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
    valid_sources = ["claude", "openai", "deepseek", "llama", "random"]
    source_lower = source.lower()
    
    if source_lower not in valid_sources:
        raise ValueError(
            f"Invalid quote source: {source}. "
            f"Valid options: {', '.join(valid_sources)}"
        )
    
    return source_lower


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='bge-quote-generator',
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
        help='Path to configuration file (default: config/config.yaml)'
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
        # Display banner
        logger.info("=" * 60)
        logger.info("BGE Social Quote Generator v%s", __version__)
        logger.info("=" * 60)
        
        # Validate and parse episode selection
        episode_numbers: Optional[List[str]] = None
        
        if args.episode:
            # Single episode
            if not args.episode.isdigit():
                logger.error(f"Invalid episode number: {args.episode}")
                return 1
            episode_numbers = [args.episode]
            logger.info(f"Processing episode: {args.episode}")
            
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
        
        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")
        
        try:
            config = Config(args.config)
        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            return 1
        
        # Apply command-line overrides to configuration
        if args.output_dir:
            logger.info(f"Overriding output directory: {args.output_dir}")
            config.general_settings['output_dir'] = args.output_dir
        
        if args.quote_source:
            logger.info(f"Overriding quote source: {args.quote_source}")
            config.quote_settings.preferred_source = args.quote_source
        
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
