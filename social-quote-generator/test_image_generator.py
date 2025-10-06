"""Quick test for ImageGenerator functionality."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from extractors.base import EpisodeQuote
from generators.image_generator import ImageGenerator


def test_image_generator():
    """Test basic image generation functionality."""
    
    print("Testing ImageGenerator...")
    
    # Check if config exists
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        print("   Please create config.yaml from config.example.yaml")
        return False
    
    try:
        # Load configuration
        print("✓ Loading configuration...")
        config = Config(config_path)
        
        # Create test episode quote
        print("✓ Creating test episode data...")
        test_quote = EpisodeQuote(
            episode_number="1",
            title="BGE Episodio 1: Test Episode",
            quote="Questa è una citazione di test per verificare il funzionamento del generatore di immagini. Include caratteri italiani come à, è, ì, ò, ù e simboli speciali!",
            quote_source="claude",
            guests=["Guest One", "Guest Two"],
            date="2024-01-01",
            youtube_id="test123",
            tags=["test", "devops", "tech"],
            duration=3600,
            description="Test episode description",
            host="Test Host",
            titolo="Test Episode",
            summary=["Test topic 1", "Test topic 2"]
        )
        
        # Initialize generator
        print("✓ Initializing ImageGenerator...")
        generator = ImageGenerator(config)
        
        # Test image generation for Instagram
        print("✓ Generating test image for Instagram...")
        result = generator.generate(test_quote, platform="instagram")
        
        print(f"\n✅ Success! Image generated:")
        print(f"   File: {result.file_path}")
        print(f"   Platform: {result.platform}")
        print(f"   Episode: {result.episode_number}")
        print(f"   Dimensions: {result.dimensions}")
        print(f"   Timestamp: {result.timestamp}")
        
        # Check if file exists
        if os.path.exists(result.file_path):
            file_size = os.path.getsize(result.file_path)
            print(f"   File size: {file_size:,} bytes")
            print(f"\n✅ Image file created successfully!")
            return True
        else:
            print(f"\n❌ Image file not found: {result.file_path}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_image_generator()
    sys.exit(0 if success else 1)
