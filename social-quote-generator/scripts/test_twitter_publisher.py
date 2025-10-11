"""Test script for Twitter publisher implementation."""

import logging
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import directly from modules
from src.config import Config
from src.extractors.base import EpisodeQuote
from src.publishers.twitter_publisher import TwitterPublisher
from src.publishers.base import PublishResult

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_caption_generation():
    """Test caption generation without publishing."""
    logger.info("=" * 60)
    logger.info("Testing Caption Generation")
    logger.info("=" * 60)
    
    try:
        # Load config
        config = Config("config/config.yaml")
        logger.info("✓ Configuration loaded successfully")
        
        # Create sample episode data
        sample_episode = EpisodeQuote(
            episode_number="42",
            title="BGE Episodio 42: Test Episode",
            titolo="Test Episode",
            quote="This is a test quote about DevOps and automation.",
            quote_source="claude",
            guests=["John Doe", "Jane Smith"],
            date="2025-01-10",
            youtube_id="dQw4w9WgXcQ",
            tags=["DevOps", "Automation", "Testing"],
            duration=3600,
            description="A test episode for the quote generator",
            host="Test Host"
        )
        
        # Create publisher
        publisher = TwitterPublisher(config)
        logger.info("✓ Twitter publisher created")
        
        # Generate caption
        caption = publisher._generate_caption(sample_episode)
        logger.info(f"\n📝 Generated Caption ({len(caption)} chars):")
        logger.info("-" * 60)
        logger.info(caption)
        logger.info("-" * 60)
        
        # Generate hashtags
        hashtags = publisher._generate_hashtags(sample_episode)
        logger.info(f"\n🏷️  Generated Hashtags:")
        logger.info(hashtags)
        
        logger.info("\n✓ Caption generation test passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Caption generation test failed: {e}", exc_info=True)
        return False


def test_dry_run_publish():
    """Test dry-run publish (no actual posting)."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Dry-Run Publish")
    logger.info("=" * 60)
    
    try:
        # Load config
        config = Config("config/config.yaml")
        
        # Create sample episode data
        sample_episode = EpisodeQuote(
            episode_number="1",
            title="BGE Episodio 1: Test",
            titolo="Test",
            quote="Test quote",
            quote_source="claude",
            guests=["Test Guest"],
            date="2025-01-10",
            youtube_id="test123",
            tags=["Test"],
            host="Test Host"
        )
        
        # Create publisher
        publisher = TwitterPublisher(config)
        
        # Test with a dummy image path (dry-run won't actually access it)
        # In real usage, this would be a generated image
        dummy_image = "output/images/test.png"
        
        # Dry run publish
        result = publisher.publish(
            image_path=dummy_image,
            quote_data=sample_episode,
            dry_run=True
        )
        
        logger.info(f"\n📊 Publish Result:")
        logger.info(f"  Success: {result.success}")
        logger.info(f"  Platform: {result.platform}")
        logger.info(f"  URL: {result.post_url}")
        logger.info(f"  Timestamp: {result.timestamp}")
        
        if result.success:
            logger.info("\n✓ Dry-run publish test passed!")
            return True
        else:
            logger.error(f"\n✗ Dry-run publish failed: {result.error}")
            return False
        
    except Exception as e:
        logger.error(f"✗ Dry-run publish test failed: {e}", exc_info=True)
        return False


def test_credential_validation():
    """Test credential validation."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Credential Validation")
    logger.info("=" * 60)
    
    try:
        # Load config
        config = Config("config/config.yaml")
        
        # Check for credential warnings
        warnings = config.validate_credentials()
        
        if warnings:
            logger.warning("\n⚠️  Credential Warnings:")
            for warning in warnings:
                logger.warning(f"  {warning}")
            logger.info("\n💡 This is expected if you haven't configured real credentials yet.")
        else:
            logger.info("\n✓ All credentials are configured!")
        
        # Try to create publisher
        try:
            publisher = TwitterPublisher(config)
            logger.info("✓ Twitter publisher created (credentials present)")
            
            # Try to authenticate (will fail with placeholder credentials)
            try:
                publisher.authenticate()
                logger.info("✓ Authentication successful!")
            except ValueError as e:
                logger.warning(f"⚠️  Authentication failed (expected with placeholder credentials): {e}")
                logger.info("💡 Configure real Twitter API credentials to test authentication.")
                
        except ValueError as e:
            logger.warning(f"⚠️  Publisher creation failed: {e}")
            logger.info("💡 This is expected if Twitter is not enabled in config.")
        
        logger.info("\n✓ Credential validation test completed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Credential validation test failed: {e}", exc_info=True)
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("Twitter Publisher Test Suite")
    logger.info("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Caption Generation", test_caption_generation()))
    results.append(("Credential Validation", test_credential_validation()))
    results.append(("Dry-Run Publish", test_dry_run_publish()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed!")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
