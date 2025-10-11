"""Test script for quote extractor functionality."""

import sys
import os
from pathlib import Path

# Get paths
script_dir = Path(__file__).parent
repo_root = script_dir.parent

# Add script directory to path
sys.path.insert(0, str(script_dir))

# Change to repository root so relative paths in config work
os.chdir(repo_root)

# Import modules
from src.config import Config
from src.extractors import QuoteExtractor

# Config path relative to repo root
CONFIG_PATH = "social-quote-generator/config/config.yaml"


def test_single_episode():
    """Test extracting a single episode."""
    print("=" * 60)
    print("Testing single episode extraction (Episode 1)")
    print("=" * 60)
    
    try:
        # Load configuration
        config = Config(CONFIG_PATH)
        
        # Create extractor
        extractor = QuoteExtractor(config)
        
        # Extract episode 1
        episode = extractor.extract_episode("1")
        
        if episode:
            print(f"\n✓ Successfully extracted episode {episode.episode_number}")
            print(f"  Title: {episode.titolo}")
            print(f"  Quote: {episode.quote[:100]}..." if len(episode.quote) > 100 else f"  Quote: {episode.quote}")
            print(f"  Source: {episode.quote_source}")
            print(f"  Guests: {episode.formatted_guests}")
            print(f"  Date: {episode.date}")
            print(f"  YouTube: {episode.youtube_url}")
            print(f"  Tags: {', '.join(episode.tags[:5])}" + ("..." if len(episode.tags) > 5 else ""))
            print(f"  Duration: {episode.duration}s")
            return True
        else:
            print("\n✗ Failed to extract episode 1")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_episodes():
    """Test extracting multiple episodes."""
    print("\n" + "=" * 60)
    print("Testing multiple episode extraction (first 5 episodes)")
    print("=" * 60)
    
    try:
        # Load configuration
        config = Config(CONFIG_PATH)
        
        # Create extractor
        extractor = QuoteExtractor(config)
        
        # Extract first 5 episodes
        success_count = 0
        for i in range(1, 6):
            episode = extractor.extract_episode(str(i))
            if episode:
                print(f"\n✓ Episode {episode.episode_number}: {episode.titolo[:50]}...")
                print(f"  Quote source: {episode.quote_source}")
                success_count += 1
            else:
                print(f"\n✗ Failed to extract episode {i}")
        
        print(f"\n{success_count}/5 episodes extracted successfully")
        return success_count > 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_episodes():
    """Test extracting all episodes."""
    print("\n" + "=" * 60)
    print("Testing all episodes extraction")
    print("=" * 60)
    
    try:
        # Load configuration
        config = Config(CONFIG_PATH)
        
        # Create extractor
        extractor = QuoteExtractor(config)
        
        # Extract all episodes
        episodes = extractor.extract_all_episodes()
        
        print(f"\n✓ Successfully extracted {len(episodes)} episodes")
        
        if episodes:
            print(f"\nFirst episode: {episodes[0].episode_number} - {episodes[0].titolo[:50]}...")
            print(f"Last episode: {episodes[-1].episode_number} - {episodes[-1].titolo[:50]}...")
            
            # Show quote source distribution
            sources = {}
            for ep in episodes:
                sources[ep.quote_source] = sources.get(ep.quote_source, 0) + 1
            
            print("\nQuote source distribution:")
            for source, count in sorted(sources.items()):
                print(f"  {source}: {count}")
        
        return len(episodes) > 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quote_sources():
    """Test different quote source preferences."""
    print("\n" + "=" * 60)
    print("Testing different quote source preferences")
    print("=" * 60)
    
    try:
        config = Config(CONFIG_PATH)
        extractor = QuoteExtractor(config)
        
        # Test each source
        sources = ["claude", "openai", "deepseek", "llama"]
        
        for source in sources:
            config.override_quote_source(source)
            episode = extractor.extract_episode("1")
            
            if episode:
                print(f"\n✓ {source}: {episode.quote[:80]}...")
            else:
                print(f"\n✗ {source}: No quote found")
        
        # Test random
        print("\n\nTesting random source selection:")
        config.override_quote_source("random")
        for i in range(3):
            episode = extractor.extract_episode("1")
            if episode:
                print(f"  Attempt {i+1}: {episode.quote_source}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BGE Quote Extractor Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Single Episode", test_single_episode()))
    results.append(("Multiple Episodes", test_multiple_episodes()))
    results.append(("All Episodes", test_all_episodes()))
    results.append(("Quote Sources", test_quote_sources()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    print(f"\n{passed_count}/{len(results)} tests passed")
    
    sys.exit(0 if passed_count == len(results) else 1)
