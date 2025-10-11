"""Instagram publisher implementation."""

import logging
from typing import Optional

from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    ChallengeRequired,
    TwoFactorRequired,
    BadPassword,
    ClientError
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from ..config import Config
from ..extractors.base import EpisodeQuote
from .base import BasePublisher, PublishResult


logger = logging.getLogger(__name__)


class InstagramPublisher(BasePublisher):
    """
    Publisher for Instagram platform.
    
    Uses instagrapi library to authenticate and post photos with captions.
    Implements retry logic with exponential backoff for transient errors.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Instagram publisher.
        
        Args:
            config: Configuration object with Instagram credentials
            
        Raises:
            ValueError: If Instagram is not configured or enabled
        """
        super().__init__(config)
        
        self.client: Optional[Client] = None
        self._authenticated = False
    
    def _get_platform_name(self) -> str:
        """Get platform name."""
        return "instagram"
    
    def authenticate(self) -> bool:
        """
        Authenticate with Instagram API.
        
        Uses username and password authentication.
        Note: Instagram may require 2FA or challenge verification.
        
        Returns:
            True if authentication succeeded
            
        Raises:
            LoginRequired: If login fails
            ChallengeRequired: If Instagram requires challenge verification
            TwoFactorRequired: If 2FA is enabled
            ValueError: If credentials are missing or invalid
        """
        credentials = self.platform_settings.credentials
        
        # Validate credentials are present
        required_creds = ["username", "password"]
        missing_creds = []
        
        for cred in required_creds:
            value = credentials.get(cred, "")
            if not value or value.startswith("${") or value.startswith("your_"):
                missing_creds.append(cred)
        
        if missing_creds:
            raise ValueError(
                f"Instagram credentials missing or not configured: {', '.join(missing_creds)}. "
                f"Please set them in your configuration file or environment variables."
            )
        
        try:
            # Create Instagram client
            self.client = Client()
            
            # Optional: Load session if available to avoid repeated logins
            # This helps avoid Instagram's rate limiting and suspicious activity detection
            session_file = credentials.get("session_file")
            if session_file:
                try:
                    self.client.load_settings(session_file)
                    logger.debug(f"Loaded Instagram session from {session_file}")
                except Exception as e:
                    logger.debug(f"Could not load session file: {e}")
            
            # Login to Instagram
            username = credentials["username"]
            password = credentials["password"]
            
            logger.info(f"Authenticating with Instagram as {username}...")
            self.client.login(username, password)
            
            # Save session for future use
            if session_file:
                try:
                    self.client.dump_settings(session_file)
                    logger.debug(f"Saved Instagram session to {session_file}")
                except Exception as e:
                    logger.warning(f"Could not save session file: {e}")
            
            # Verify authentication by getting user info
            user_id = self.client.user_id
            logger.info(f"✓ Authenticated with Instagram (User ID: {user_id})")
            
            self._authenticated = True
            return True
            
        except BadPassword as e:
            logger.error(f"Instagram authentication failed: Invalid password")
            raise ValueError(
                f"Instagram authentication failed: Invalid password. "
                f"Please check your credentials."
            ) from e
            
        except TwoFactorRequired as e:
            logger.error(f"Instagram authentication failed: 2FA required")
            raise ValueError(
                f"Instagram authentication failed: Two-factor authentication is enabled. "
                f"Please provide 2FA code or use an app-specific password."
            ) from e
            
        except ChallengeRequired as e:
            logger.error(f"Instagram authentication failed: Challenge required")
            raise ValueError(
                f"Instagram authentication failed: Instagram requires challenge verification. "
                f"Please verify your account through the Instagram app first."
            ) from e
            
        except LoginRequired as e:
            logger.error(f"Instagram authentication failed: {e}")
            raise ValueError(
                f"Instagram authentication failed. Please check your credentials."
            ) from e
            
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            raise
    
    @retry(
        retry=retry_if_exception_type(ClientError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _upload_photo_with_retry(self, image_path: str, caption: str) -> dict:
        """
        Upload photo to Instagram with retry logic.
        
        Args:
            image_path: Path to image file
            caption: Photo caption
            
        Returns:
            Media dict with post information
            
        Raises:
            ClientError: If upload fails after retries
        """
        logger.debug(f"Uploading photo: {image_path}")
        media = self.client.photo_upload(image_path, caption)
        logger.debug(f"Photo uploaded successfully: {media.pk}")
        return media
    
    def publish(
        self,
        image_path: str,
        quote_data: EpisodeQuote,
        dry_run: bool = False
    ) -> PublishResult:
        """
        Publish image with caption to Instagram.
        
        Workflow:
        1. Generate caption from template
        2. (Dry-run mode: skip remaining steps)
        3. Validate image file exists
        4. Authenticate if not already authenticated
        5. Upload photo with caption
        6. Return result with post URL
        
        Args:
            image_path: Path to image file to publish
            quote_data: Episode quote data for caption generation
            dry_run: If True, generate caption but don't actually publish
            
        Returns:
            PublishResult with success status and post URL or error
        """
        try:
            # Generate caption
            caption = self._generate_caption(quote_data)
            logger.info(f"Generated caption ({len(caption)} chars): {caption[:100]}...")
            
            # Check caption length (Instagram limit is 2,200 characters)
            if len(caption) > 2200:
                logger.warning(
                    f"Caption exceeds Instagram's 2,200 character limit ({len(caption)} chars). "
                    f"It will be truncated."
                )
                caption = caption[:2197] + "..."
            
            # Dry run mode - don't actually publish
            if dry_run:
                logger.info(f"[DRY RUN] Would publish to Instagram:")
                logger.info(f"  Image: {image_path}")
                logger.info(f"  Caption: {caption}")
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    post_url="[DRY RUN - not published]"
                )
            
            # Validate image file (only when actually publishing)
            self._validate_image_path(image_path)
            
            # Authenticate if not already authenticated
            if not self._authenticated:
                self.authenticate()
            
            # Upload photo with caption
            try:
                media = self._upload_photo_with_retry(image_path, caption)
                
                # Construct post URL
                post_code = media.code
                post_url = f"https://www.instagram.com/p/{post_code}/"
                
                logger.info(f"✓ Successfully published to Instagram: {post_url}")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    post_url=post_url
                )
                
            except ClientError as e:
                error_msg = f"Failed to upload photo: {e}"
                logger.error(error_msg)
                return PublishResult(
                    success=False,
                    platform=self.platform_name,
                    error=error_msg
                )
        
        except FileNotFoundError as e:
            error_msg = f"Image file not found: {e}"
            logger.error(error_msg)
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error=error_msg
            )
        
        except ValueError as e:
            error_msg = f"Configuration or validation error: {e}"
            logger.error(error_msg)
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg, exc_info=True)
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error=error_msg
            )
