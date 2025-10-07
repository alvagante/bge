#!/usr/bin/env python3
"""Simple test script for validators."""

from src.utils.validators import (
    EpisodeValidator,
    PathValidator,
    ConfigValidator,
    TextValidator,
    CredentialValidator,
    RateLimitValidator,
    ValidationError
)


def test_episode_validator():
    """Test EpisodeValidator."""
    print("\n=== Testing EpisodeValidator ===")
    
    # Valid episode numbers
    try:
        result = EpisodeValidator.validate_episode_number("42")
        print(f"✓ Valid episode number '42' -> '{result}'")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Invalid episode number (non-numeric)
    try:
        EpisodeValidator.validate_episode_number("abc")
        print("✗ Should have rejected non-numeric episode")
    except ValidationError as e:
        print(f"✓ Rejected non-numeric episode: {e}")
    
    # Invalid episode number (negative)
    try:
        EpisodeValidator.validate_episode_number("-1")
        print("✗ Should have rejected negative episode")
    except ValidationError as e:
        print(f"✓ Rejected negative episode: {e}")
    
    # Invalid episode number (too large)
    try:
        EpisodeValidator.validate_episode_number("10001")
        print("✗ Should have rejected too large episode")
    except ValidationError as e:
        print(f"✓ Rejected too large episode: {e}")


def test_path_validator():
    """Test PathValidator."""
    print("\n=== Testing PathValidator ===")
    
    # Valid relative path
    try:
        result = PathValidator.validate_path("config/config.yaml")
        print(f"✓ Valid relative path accepted: {result}")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Invalid path (directory traversal)
    try:
        PathValidator.validate_path("../etc/passwd")
        print("✗ Should have rejected directory traversal")
    except ValidationError as e:
        print(f"✓ Rejected directory traversal: {e}")
    
    # Invalid path (absolute)
    try:
        PathValidator.validate_path("/etc/passwd")
        print("✗ Should have rejected absolute path")
    except ValidationError as e:
        print(f"✓ Rejected absolute path: {e}")


def test_config_validator():
    """Test ConfigValidator."""
    print("\n=== Testing ConfigValidator ===")
    
    # Valid dimensions
    try:
        result = ConfigValidator.validate_dimensions((1080, 1080))
        print(f"✓ Valid dimensions accepted: {result}")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Invalid dimensions (too large)
    try:
        ConfigValidator.validate_dimensions((20000, 1080))
        print("✗ Should have rejected too large dimensions")
    except ValidationError as e:
        print(f"✓ Rejected too large dimensions: {e}")
    
    # Valid color
    try:
        result = ConfigValidator.validate_color("#FFFFFF")
        print(f"✓ Valid color accepted: {result}")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Invalid color
    try:
        ConfigValidator.validate_color("white")
        print("✗ Should have rejected invalid color")
    except ValidationError as e:
        print(f"✓ Rejected invalid color: {e}")
    
    # Valid platform
    try:
        result = ConfigValidator.validate_platform("twitter")
        print(f"✓ Valid platform accepted: {result}")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Invalid platform
    try:
        ConfigValidator.validate_platform("tiktok")
        print("✗ Should have rejected invalid platform")
    except ValidationError as e:
        print(f"✓ Rejected invalid platform: {e}")


def test_text_validator():
    """Test TextValidator."""
    print("\n=== Testing TextValidator ===")
    
    # Sanitize text
    try:
        text = "Hello <script>alert('xss')</script> World"
        result = TextValidator.sanitize_text(text)
        print(f"✓ Text sanitized: '{text}' -> '{result}'")
        if "<script>" in result:
            print("✗ Warning: HTML not properly escaped")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Valid quote
    try:
        result = TextValidator.validate_quote("This is a valid quote from the episode.")
        print(f"✓ Valid quote accepted (length: {len(result)})")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Invalid quote (too short)
    try:
        TextValidator.validate_quote("Short")
        print("✗ Should have rejected too short quote")
    except ValidationError as e:
        print(f"✓ Rejected too short quote: {e}")


def test_credential_validator():
    """Test CredentialValidator."""
    print("\n=== Testing CredentialValidator ===")
    
    # Valid credential
    try:
        result = CredentialValidator.validate_credential("abc123def456ghi789", "API Key")
        print(f"✓ Valid credential accepted")
    except ValidationError as e:
        print(f"✗ Failed: {e}")
    
    # Invalid credential (placeholder)
    try:
        CredentialValidator.validate_credential("${TWITTER_API_KEY}", "API Key")
        print("✗ Should have rejected placeholder credential")
    except ValidationError as e:
        print(f"✓ Rejected placeholder credential: {e}")
    
    # Invalid credential (too short)
    try:
        CredentialValidator.validate_credential("abc123", "API Key")
        print("✗ Should have rejected too short credential")
    except ValidationError as e:
        print(f"✓ Rejected too short credential: {e}")


def test_rate_limit_validator():
    """Test RateLimitValidator."""
    print("\n=== Testing RateLimitValidator ===")
    
    # Under limit
    allowed, message = RateLimitValidator.check_rate_limit("twitter", 50, 24)
    if allowed and message is None:
        print(f"✓ Under rate limit: allowed={allowed}, message={message}")
    else:
        print(f"✗ Unexpected result: allowed={allowed}, message={message}")
    
    # Approaching limit
    allowed, message = RateLimitValidator.check_rate_limit("twitter", 250, 24)
    if allowed and message is not None:
        print(f"✓ Approaching rate limit: allowed={allowed}, message='{message}'")
    else:
        print(f"✗ Unexpected result: allowed={allowed}, message={message}")
    
    # Exceeded limit
    allowed, message = RateLimitValidator.check_rate_limit("twitter", 350, 24)
    if not allowed and message is not None:
        print(f"✓ Rate limit exceeded: allowed={allowed}, message='{message}'")
    else:
        print(f"✗ Unexpected result: allowed={allowed}, message={message}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Validator Tests")
    print("=" * 60)
    
    test_episode_validator()
    test_path_validator()
    test_config_validator()
    test_text_validator()
    test_credential_validator()
    test_rate_limit_validator()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
