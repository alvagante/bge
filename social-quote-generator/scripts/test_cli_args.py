#!/usr/bin/env python3
"""
Test script to verify CLI argument parsing without dependencies.
"""

import sys
import argparse
from io import StringIO


def create_parser():
    """Create the argument parser (copied from main.py)."""
    parser = argparse.ArgumentParser(
        prog='bge-quote-generator',
        description='Generate and publish quote images from BGE podcast episodes',
        epilog='For more information, see the README.md file.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    episode_group = parser.add_mutually_exclusive_group(required=True)
    episode_group.add_argument('--episode', '-e', type=str, metavar='N',
                               help='Process a single episode by number')
    episode_group.add_argument('--episodes', type=str, metavar='N,M,P',
                               help='Process multiple episodes (comma-separated)')
    episode_group.add_argument('--all', '-a', action='store_true',
                               help='Process all available episodes')
    
    parser.add_argument('--platform', '-p', type=str, metavar='PLATFORM',
                        help='Generate images for specific platform')
    
    publish_group = parser.add_mutually_exclusive_group()
    publish_group.add_argument('--publish', action='store_true',
                               help='Publish generated images to social media')
    publish_group.add_argument('--dry-run', action='store_true',
                               help='Generate images without publishing')
    
    parser.add_argument('--config', '-c', type=str, default='config/config.yaml',
                        metavar='PATH', help='Path to configuration file')
    parser.add_argument('--output-dir', '-o', type=str, metavar='PATH',
                        help='Override output directory')
    parser.add_argument('--quote-source', type=str, metavar='SOURCE',
                        help='Preferred quote source')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    
    return parser


def test_cli_arguments():
    """Test various CLI argument combinations."""
    parser = create_parser()
    
    test_cases = [
        # Basic episode selection
        (['--episode', '1'], "Single episode"),
        (['-e', '42'], "Single episode (short form)"),
        (['--episodes', '1,5,10'], "Multiple episodes"),
        (['--all'], "All episodes"),
        (['-a'], "All episodes (short form)"),
        
        # With platform
        (['--episode', '1', '--platform', 'instagram'], "Episode with platform"),
        (['-e', '1', '-p', 'twitter'], "Episode with platform (short form)"),
        
        # With publishing options
        (['--episode', '1', '--publish'], "Episode with publish"),
        (['--episode', '1', '--dry-run'], "Episode with dry-run"),
        
        # With config options
        (['--episode', '1', '--config', 'custom.yaml'], "Custom config"),
        (['-e', '1', '-c', 'custom.yaml'], "Custom config (short form)"),
        (['--episode', '1', '--output-dir', '/tmp/output'], "Custom output dir"),
        (['-e', '1', '-o', '/tmp/output'], "Custom output dir (short form)"),
        
        # With quote source
        (['--episode', '1', '--quote-source', 'claude'], "With quote source"),
        
        # With verbose
        (['--episode', '1', '--verbose'], "With verbose"),
        (['-e', '1', '-v'], "With verbose (short form)"),
        
        # Complex combinations
        (['-e', '1', '-p', 'instagram', '--publish', '-v'], "Complex combination"),
        (['--all', '--platform', 'twitter', '--dry-run', '--verbose'], "All episodes complex"),
    ]
    
    print("Testing CLI Argument Parsing")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for args, description in test_cases:
        try:
            parsed = parser.parse_args(args)
            print(f"✓ {description}: {' '.join(args)}")
            passed += 1
        except SystemExit as e:
            if e.code == 0:
                print(f"✓ {description}: {' '.join(args)}")
                passed += 1
            else:
                print(f"✗ {description}: {' '.join(args)}")
                failed += 1
        except Exception as e:
            print(f"✗ {description}: {' '.join(args)} - {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    # Test error cases
    print("\nTesting Error Cases (should fail)")
    print("=" * 60)
    
    error_cases = [
        ([], "No arguments"),
        (['--episode', '1', '--all'], "Conflicting episode selection"),
        (['--episode', '1', '--publish', '--dry-run'], "Conflicting publish options"),
    ]
    
    for args, description in error_cases:
        try:
            parsed = parser.parse_args(args)
            print(f"✗ {description} should have failed: {' '.join(args)}")
        except SystemExit:
            print(f"✓ {description} correctly rejected: {' '.join(args)}")
    
    print("=" * 60)
    
    # Test help output
    print("\nHelp Output:")
    print("=" * 60)
    t
_arguments()    test_cli':
__ain_m== '___name__ f 


i      passt:
  t SystemExi    exceplp'])
-heargs(['-ser.parse_     parry:
   