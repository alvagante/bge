#!/usr/bin/env python3
"""Test script for pipeline orchestrator."""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config
from src.orchestrator import PipelineOrchestrator


def setup_logging():
    """Configure logging for test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_orchestrator_initialization():
    """Test that orchestrator can be initialized."""
    print("\n" + "=" * 60)
    print("Test: Orchestrator Initialization")
    print("=" * 60)
    
    try:
        config = Config("config/config.yaml")
        orchestrator = PipelineOrchestrator(config)
        
        print("✓ Orchestrator initialized successfully")
        print(f"  - Extractor: {orchestrator.extractor.__class__.__name__}")
        print(f"  - Generator: {orchestrator.generator.__class__.__name__}")
        print(f"  - Publishers: {len(orchestrator.publishers)} initialized")
        
        return True
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extract_episodes():
    """Test episode extraction."""
    print("\n" + "=" * 60)
    print("Test: Episode Extraction")
    print("=" * 60)
    
    try:
        config = Config("config/config.yaml")
        orchestrator = PipelineOrchestrator(config)
        
        # Test extracting a single episode
        episodes = orchestrator._extract_episodes(["1"])
        
        if episodes:
            print(f"✓ Successfully extracted {len(episodes)} episode(s)")
            for ep in episodes:
                print(f"  - Episode {ep.episode_number}: {ep.titolo}")
                print(f"    Quote source: {ep.quote_source}")
                print(f"    Quote: {ep.quote[:50]}...")
        else:
            print("⚠ No episodes extracted (this may be expected if episode 1 doesn't exist)")
        
        return True
    except Exception as e:
        print(f"✗ Failed to extract episodes: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_determine_platforms():
    """Test platform determination."""
    print("\n" + "=" * 60)
    print("Test: Platform Determination")
    print("=" * 60)
    
    try:
        config = Config("config/config.yaml")
        orchestrator = PipelineOrchestrator(config)
        
        # Test with no specific platforms (should use all configured)
        platforms = orchestrator._determine_platforms(None)
        print(f"✓ Configured platforms: {', '.join(platforms)}")
        
        # Test with specific platform
        specific = orchestrator._determine_platforms(["instagram"])
        print(f"✓ Specific platform request: {', '.join(specific)}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to determine platforms: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dry_run():
    """Test dry-run mode."""
    print("\n" + "=" * 60)
    print("Test: Dry Run Mode")
    print("=" * 60)
    
    try:
        config = Config("config/config.yaml")
        orchestrator = PipelineOrchestrator(config)
        
        # Run pipeline in dry-run mode for episode 1
        result = orchestrator.run(
            episode_numbers=["1"],
            platforms=["instagram"],
            publish=False,
            dry_run=True
        )
        
        print(f"\n✓ Dry run completed")
        print(f"  - Episodes processed: {result.total_episodes}")
        print(f"  - Images generated: {result.successful_images}")
        print(f"  - Duration: {result.duration:.2f}s")
        
        if result.results:
            for ep_result in result.results:
                print(f"\n  Episode {ep_result.episode_number}:")
                print(f"    - Images: {ep_result.images_generated}")
                print(f"    - Errors: {len(ep_result.errors)}")
                if ep_result.errors:
                    for error in ep_result.errors:
                        print(f"      • {error}")
        
        return True
    except Exception as e:
        print(f"✗ Dry run failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    setup_logging()
    
    print("\n" + "=" * 60)
    print("Pipeline Orchestrator Test Suite")
    print("=" * 60)
    
    tests = [
        ("Initialization", test_orchestrator_initialization),
        ("Episode Extraction", test_extract_episodes),
        ("Platform Determination", test_determine_platforms),
        ("Dry Run", test_dry_run),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
