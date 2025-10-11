"""Tests for input validation and security measures."""

import pytest
from pathlib import Path

from src.utils.validators import (
    EpisodeValidator,
    PathValidator,
    ConfigValidator,
    TextValidator,
    CredentialValidator,
    RateLimitValidator,
    ValidationError
)


class TestEpisodeValidator:
    """Tests for EpisodeValidator."""
    
    def test_valid_episode_number(self):
        """Test validation of valid episode numbers."""
        assert EpisodeValidator.validate_episode_number("1") == "1"
        assert EpisodeValidator.validate_episode_number("42") == "42"
        assert EpisodeValidator.validate_episode_number("100") == "100"
    
    def test_invalid_episode_number_non_numeric(self):
        """Test validation fails for non-numeric episode numbers."""
        with pytest.raises(ValidationError, match="must be numeric"):
            EpisodeValidator.validate_episode_number("abc")
        
        with pytest.raises(ValidationError, match="must be numeric"):
            EpisodeValidator.validate_episode_number("1a")
    
    def test_invalid_episode_number_negative(self):
        """Test validation fails for negative episode numbers."""
        with pytest.raises(ValidationError, match="must be positive"):
            EpisodeValidator.validate_episode_number("-1")
        
        with pytest.raises(ValidationError, match="must be positive"):
            EpisodeValidator.validate_episode_number("0")
    
    def test_invalid_episode_number_too_large(self):
        """Test validation fails for unreasonably large episode numbers."""
        with pytest.raises(ValidationError, match="too large"):
            EpisodeValidator.validate_episode_number("10001")
    
    def test_invalid_episode_number_empty(self):
        """Test validation fails for empty episode numbers."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            EpisodeValidator.validate_episode_number("")
        
        with pytest.raises(ValidationError, match="cannot be empty"):
            EpisodeValidator.validate_episode_number("   ")
    
    def test_validate_episode_list(self):
        """Test validation of episode lists."""
        result = EpisodeValidator.validate_episode_list(["1", "5", "10"])
        assert result == ["1", "5", "10"]
    
    def test_validate_episode_list_invalid(self):
        """Test validation fails for invalid episode lists."""
        with pytest.raises(ValidationError):
            EpisodeValidator.validate_episode_list(["1", "abc", "10"])


class TestPathValidator:
    """Tests for PathValidator."""
    
    def test_valid_relative_path(self):
        """Test validation of valid relative paths."""
        path = PathValidator.validate_path("config/config.yaml")
        assert isinstance(path, Path)
        assert str(path) == "config/config.yaml"
    
    def test_invalid_path_directory_traversal(self):
        """Test validation fails for directory traversal attempts."""
        with pytest.raises(ValidationError, match="directory traversal"):
            PathValidator.validate_path("../etc/passwd")
        
        with pytest.raises(ValidationError, match="directory traversal"):
            PathValidator.validate_path("config/../../etc/passwd")
    
    def test_invalid_path_absolute(self):
        """Test validation fails for absolute paths."""
        with pytest.raises(ValidationError, match="absolute paths not allowed"):
            PathValidator.validate_path("/etc/passwd")
    
    def test_invalid_path_null_byte(self):
        """Test validation fails for paths with null bytes."""
        with pytest.raises(ValidationError, match="null bytes"):
            PathValidator.validate_path("config\x00/file.txt")
    
    def test_invalid_path_empty(self):
        """Test validation fails for empty paths."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            PathValidator.validate_path("")


class TestConfigValidator:
    """Tests for ConfigValidator."""
    
    def test_valid_dimensions(self):
        """Test validation of valid dimensions."""
        dims = ConfigValidator.validate_dimensions((1080, 1080))
        assert dims == (1080, 1080)
        
        dims = ConfigValidator.validate_dimensions([1200, 675])
        assert dims == (1200, 675)
    
    def test_invalid_dimensions_negative(self):
        """Test validation fails for negative dimensions."""
        with pytest.raises(ValidationError, match="must be positive"):
            ConfigValidator.validate_dimensions((1080, -100))
    
    def test_invalid_dimensions_too_large(self):
        """Test validation fails for unreasonably large dimensions."""
        with pytest.raises(ValidationError, match="too large"):
            ConfigValidator.validate_dimensions((20000, 1080))
    
    def test_invalid_dimensions_too_small(self):
        """Test validation fails for too small dimensions."""
        with pytest.raises(ValidationError, match="too small"):
            ConfigValidator.validate_dimensions((50, 1080))
    
    def test_valid_color(self):
        """Test validation of valid hex colors."""
        assert ConfigValidator.validate_color("#FFFFFF") == "#FFFFFF"
        assert ConfigValidator.validate_color("#000000") == "#000000"
        assert ConfigValidator.validate_color("#ff00ff") == "#ff00ff"
    
    def test_invalid_color(self):
        """Test validation fails for invalid colors."""
        with pytest.raises(ValidationError, match="must be hex color"):
            ConfigValidator.validate_color("white")
        
        with pytest.raises(ValidationError, match="must be hex color"):
            ConfigValidator.validate_color("#FFF")
        
        with pytest.raises(ValidationError, match="must be hex color"):
            ConfigValidator.validate_color("#GGGGGG")
    
    def test_valid_font_size(self):
        """Test validation of valid font sizes."""
        assert ConfigValidator.validate_font_size(48) == 48
        assert ConfigValidator.validate_font_size(12) == 12
    
    def test_invalid_font_size(self):
        """Test validation fails for invalid font sizes."""
        with pytest.raises(ValidationError, match="must be positive"):
            ConfigValidator.validate_font_size(0)
        
        with pytest.raises(ValidationError, match="too large"):
            ConfigValidator.validate_font_size(600)
        
        with pytest.raises(ValidationError, match="too small"):
            ConfigValidator.validate_font_size(5)
    
    def test_valid_platform(self):
        """Test validation of valid platforms."""
        assert ConfigValidator.validate_platform("twitter") == "twitter"
        assert ConfigValidator.validate_platform("INSTAGRAM") == "instagram"
    
    def test_invalid_platform(self):
        """Test validation fails for invalid platforms."""
        with pytest.raises(ValidationError, match="Invalid platform"):
            ConfigValidator.validate_platform("tiktok")
    
    def test_valid_quote_source(self):
        """Test validation of valid quote sources."""
        assert ConfigValidator.validate_quote_source("claude") == "claude"
        assert ConfigValidator.validate_quote_source("RANDOM") == "random"
    
    def test_invalid_quote_source(self):
        """Test validation fails for invalid quote sources."""
        with pytest.raises(ValidationError, match="Invalid quote source"):
            ConfigValidator.validate_quote_source("gpt4")


class TestTextValidator:
    """Tests for TextValidator."""
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        text = TextValidator.sanitize_text("Hello <script>alert('xss')</script> World")
        assert "<script>" not in text
        assert "alert" in text  # Content is escaped, not removed
    
    def test_sanitize_text_null_bytes(self):
        """Test null bytes are removed."""
        text = TextValidator.sanitize_text("Hello\x00World")
        assert "\x00" not in text
        assert text == "HelloWorld"
    
    def test_sanitize_text_max_length(self):
        """Test max length enforcement."""
        with pytest.raises(ValidationError, match="too long"):
            TextValidator.sanitize_text("a" * 1000, max_length=100)
    
    def test_validate_quote(self):
        """Test quote validation."""
        quote = TextValidator.validate_quote("This is a valid quote from the episode.")
        assert len(quote) >= 10
    
    def test_validate_quote_too_short(self):
        """Test validation fails for too short quotes."""
        with pytest.raises(ValidationError, match="too short"):
            TextValidator.validate_quote("Short")
    
    def test_validate_quote_empty(self):
        """Test validation fails for empty quotes."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            TextValidator.validate_quote("")
    
    def test_validate_caption(self):
        """Test caption validation."""
        caption = TextValidator.validate_caption("Episode 42: DevOps Best Practices\n\n#BGE #DevOps")
        assert len(caption) > 0


class TestCredentialValidator:
    """Tests for CredentialValidator."""
    
    def test_valid_credential(self):
        """Test validation of valid credentials."""
        cred = CredentialValidator.validate_credential("abc123def456ghi789", "API Key")
        assert cred == "abc123def456ghi789"
    
    def test_invalid_credential_placeholder(self):
        """Test validation fails for placeholder credentials."""
        with pytest.raises(ValidationError, match="placeholder"):
            CredentialValidator.validate_credential("${TWITTER_API_KEY}", "API Key")
        
        with pytest.raises(ValidationError, match="placeholder"):
            CredentialValidator.validate_credential("your_api_key_here", "API Key")
        
        with pytest.raises(ValidationError, match="placeholder"):
            CredentialValidator.validate_credential("<your_key>", "API Key")
    
    def test_invalid_credential_too_short(self):
        """Test validation fails for too short credentials."""
        with pytest.raises(ValidationError, match="too short"):
            CredentialValidator.validate_credential("abc123", "API Key")
    
    def test_invalid_credential_empty(self):
        """Test validation fails for empty credentials."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            CredentialValidator.validate_credential("", "API Key")
    
    def test_valid_credential_allow_empty(self):
        """Test validation allows empty when specified."""
        cred = CredentialValidator.validate_credential("", "API Key", allow_empty=True)
        assert cred is None
    
    def test_validate_twitter_credentials(self):
        """Test Twitter credentials validation."""
        creds = CredentialValidator.validate_twitter_credentials(
            "api_key_1234567890",
            "api_secret_1234567890",
            "access_token_1234567890",
            "access_secret_1234567890"
        )
        assert len(creds) == 4
    
    def test_validate_instagram_credentials(self):
        """Test Instagram credentials validation."""
        creds = CredentialValidator.validate_instagram_credentials(
            "test_user",
            "password123456"
        )
        assert creds[0] == "test_user"
    
    def test_validate_instagram_credentials_invalid_username(self):
        """Test validation fails for invalid Instagram username."""
        with pytest.raises(ValidationError, match="can only contain"):
            CredentialValidator.validate_instagram_credentials(
                "test user!",
                "password123456"
            )


class TestRateLimitValidator:
    """Tests for RateLimitValidator."""
    
    def test_rate_limit_ok(self):
        """Test rate limit check when under limit."""
        allowed, message = RateLimitValidator.check_rate_limit("twitter", 50, 24)
        assert allowed is True
        assert message is None
    
    def test_rate_limit_warning(self):
        """Test rate limit check when approaching limit."""
        allowed, message = RateLimitValidator.check_rate_limit("twitter", 250, 24)
        assert allowed is True
        assert message is not None
        assert "Approaching" in message
    
    def test_rate_limit_exceeded(self):
        """Test rate limit check when limit exceeded."""
        allowed, message = RateLimitValidator.check_rate_limit("twitter", 350, 24)
        assert allowed is False
        assert message is not None
        assert "exceeded" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
