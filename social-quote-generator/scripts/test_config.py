#!/usr/bin/env python3
"""Test script to validate configuration setup."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config, ConfigurationError


def test_config():
    """Test configuration loading and validation."""
    print("🔍 Testing BGE Social Quote Generator Configuration\n")
    
    try:
        # Try to load configuration
        print("📝 Loading configuration from config/config.yaml...")
        config = Config("config/config.yaml")
        print("✅ Configuration loaded successfully!\n")
        
        # Display general settings
        print("⚙️  General Settings:")
        print(f"   Episodes directory: {config.episodes_dir}")
        print(f"   Texts directory: {config.texts_dir}")
        print(f"   Output directory: {config.output_dir}")
        print(f"   Log level: {config.log_level}\n")
        
        # Display quote settings
        print("💬 Quote Settings:")
        print(f"   Preferred source: {config.quote_settings.preferred_source}")
        print(f"   Fallback sources: {', '.join(config.quote_settings.fallback_sources)}")
        print(f"   Max length: {config.quote_settings.max_length}\n")
        
        # Display image settings
        print("🖼️  Image Settings:")
        print(f"   Templates directory: {config.image_settings.templates_dir}")
        print(f"   Default font: {config.image_settings.default_font}")
        print(f"   Platforms configured: {', '.join(config.image_settings.platforms.keys())}\n")
        
        # Display social media settings
        print("📱 Social Media Settings:")
        print(f"   Enabled platforms: {', '.join(config.social_media_settings.enabled_platforms)}")
        
        for platform in config.social_media_settings.enabled_platforms:
            settings = config.social_media_settings.get_platform(platform)
            if settings:
                status = "✅ enabled" if settings.enabled else "❌ disabled"
                print(f"   {platform}: {status}")
        print()
        
        # Validate credentials
        print("🔐 Validating Credentials:")
        warnings = config.validate_credentials()
        
        if warnings:
            print("   Found issues with credentials:")
            for warning in warnings:
                print(f"   {warning}")
            print("\n   ℹ️  These are warnings, not errors. The tool will work in dry-run mode.")
            print("   ℹ️  To enable publishing, configure credentials in your .env file.")
        else:
            print("   ✅ All enabled platforms have credentials configured!")
        
        print("\n✨ Configuration test completed successfully!")
        return 0
        
    except ConfigurationError as e:
        print(f"❌ Configuration Error:\n{e}\n")
        print("💡 Tips:")
        print("   1. Make sure config/config.yaml exists (copy from config.example.yaml)")
        print("   2. Check that all required fields are present")
        print("   3. Verify color codes are in hex format (#RRGGBB)")
        print("   4. Ensure paths don't contain '..' or absolute paths")
        return 1
        
    except FileNotFoundError as e:
        print(f"❌ File Not Found:\n{e}\n")
        print("💡 Tips:")
        print("   1. Copy config.example.yaml to config/config.yaml")
        print("   2. Run: cp config/config.example.yaml config/config.yaml")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected Error:\n{e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_config())
