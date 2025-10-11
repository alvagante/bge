"""LinkedIn publisher implementation."""

import logging
from typing import Optional
import requests
import json

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


class LinkedInPublisher(BasePublisher):
    """
    Publisher for LinkedIn platform.
    
    Uses LinkedIn API v2 to authenticate and post images with text.
    Implements retry logic with exponential backoff for transient errors.
    
    Note: LinkedIn API requires OAuth 2.0 authentication and specific permissions.
    """
    
    def __init__(self, config: Config):
        """
        Initialize LinkedIn publisher.
        
        Args:
            config: Configuration object with LinkedIn credentials
            
        Raises:
            ValueError: If LinkedIn is not configured or enabled
        """
        super().__init__(config)
        
        self.access_token: Optional[str] = None
        self.person_urn: Optional[str] = None
        self._authenticated = False
        
        # LinkedIn API endpoints
        self.api_base = "https://api.linkedin.com/v2"
    
    def _get_platform_name(self) -> str:
        """Get platform name."""
        return "linkedin"
    
    def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn API.
        
        Uses OAuth 2.0 access token authentication.
        Requires an access token with 'w_member_social' permission.
        
        Returns:
            True if authentication succeeded
            
        Raises:
            requests.HTTPError: If authentication fails
            ValueError: If credentials are missing or invalid
        """
        credentials = self.platform_settings.credentials
        
        # Validate credentials are present
        required_creds = ["access_token"]
        missing_creds = []
        
        for cred in required_creds:
            value = credentials.get(cred, "")
            if not value or value.startswith("${") or value.startswith("your_"):
                missing_creds.append(cred)
        
        if missing_creds:
            raise ValueError(
                f"LinkedIn credentials missing or not configured: {', '.join(missing_creds)}. "
                f"Please set them in your configuration file or environment variables. "
                f"You need an OAuth 2.0 access token with 'w_member_social' permission."
            )
        
        try:
            self.access_token = credentials["access_token"]
            
            # Get person URN (user profile identifier)
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Get authenticated user's profile
            response = requests.get(
                f"{self.api_base}/me",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 401:
                raise ValueError(
                    "LinkedIn authentication failed: Invalid or expired access token. "
                    "Please generate a new access token."
                )
            
            response.raise_for_status()
            user_data = response.json()
            
            # Extract person URN
            user_id = user_data.get("id")
            if not user_id:
                raise ValueError("Could not retrieve user ID from LinkedIn API")
            
            self.person_urn = f"urn:li:person:{user_id}"
            
            # Get user's name for logging
            first_name = user_data.get("localizedFirstName", "")
            last_name = user_data.get("localizedLastName", "")
            full_name = f"{first_name} {last_name}".strip() or "Unknown"
            
            logger.info(f"✓ Authenticated with LinkedIn as {full_name} (URN: {self.person_urn})")
            
            self._authenticated = True
            return True
            
        except requests.HTTPError as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            raise ValueError(
                f"LinkedIn authentication failed: {e}. "
                f"Please check your access token and permissions."
            ) from e
            
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            raise
    
    def _register_image(self, image_path: str) -> dict:
        """
        Register image upload with LinkedIn API.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with upload URL and asset URN
            
        Raises:
            requests.HTTPError: If registration fails
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Register upload
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self.person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{self.api_base}/assets?action=registerUpload",
            headers=headers,
            json=register_payload,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()
    
    def _upload_image_binary(self, upload_url: str, image_path: str) -> None:
        """
        Upload image binary to LinkedIn.
        
        Args:
            upload_url: Upload URL from registration
            image_path: Path to image file
            
        Raises:
            requests.HTTPError: If upload fails
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        with open(image_path, "rb") as image_file:
            response = requests.put(
                upload_url,
                headers=headers,
                data=image_file,
                timeout=60
            )
            response.raise_for_status()
    
    @retry(
        retry=retry_if_exception_type(requests.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _create_post_with_retry(self, caption: str, asset_urn: str) -> dict:
        """
        Create LinkedIn post with image and retry logic.
        
        Args:
            caption: Post text
            asset_urn: URN of uploaded image asset
            
        Returns:
            Response dict with post information
            
        Raises:
            requests.HTTPError: If post creation fails after retries
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Create post (UGC post)
        post_payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": caption
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "BGE Episode Quote"
                            },
                            "media": asset_urn,
                            "title": {
                                "text": "BGE Quote"
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(
            f"{self.api_base}/ugcPosts",
            headers=headers,
            json=post_payload,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()
    
    def publish(
        self,
        image_path: str,
        quote_data: EpisodeQuote,
        dry_run: bool = False
    ) -> PublishResult:
        """
        Publish image with caption to LinkedIn.
        
        Workflow:
        1. Generate caption from template
        2. (Dry-run mode: skip remaining steps)
        3. Validate image file exists
        4. Authenticate if not already authenticated
        5. Register image upload with LinkedIn
        6. Upload image binary
        7. Create post with image and caption
        8. Return result with post URL
        
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
            
            # Check caption length (LinkedIn limit is 3,000 characters for posts)
            if len(caption) > 3000:
                logger.warning(
                    f"Caption exceeds LinkedIn's 3,000 character limit ({len(caption)} chars). "
                    f"It will be truncated."
                )
                caption = caption[:2997] + "..."
            
            # Dry run mode - don't actually publish
            if dry_run:
                logger.info(f"[DRY RUN] Would publish to LinkedIn:")
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
            
            # Upload image and create post
            try:
                # Step 1: Register image upload
                logger.debug("Registering image upload with LinkedIn...")
                register_response = self._register_image(image_path)
                
                # Extract upload URL and asset URN
                upload_url = register_response["value"]["uploadMechanism"][
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
                ]["uploadUrl"]
                asset_urn = register_response["value"]["asset"]
                
                # Step 2: Upload image binary
                logger.debug(f"Uploading image binary to LinkedIn...")
                self._upload_image_binary(upload_url, image_path)
                
                # Step 3: Create post with image
                logger.debug("Creating LinkedIn post...")
                post_response = self._create_post_with_retry(caption, asset_urn)
                
                # Extract post ID and construct URL
                post_id = post_response.get("id")
                if post_id:
                    # LinkedIn post URL format varies, use activity URN
                    # Extract activity ID from URN (format: urn:li:share:1234567890)
                    activity_id = post_id.split(":")[-1]
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
                else:
                    post_url = "https://www.linkedin.com/feed/"
                
                logger.info(f"✓ Successfully published to LinkedIn: {post_url}")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    post_url=post_url
                )
                
            except requests.HTTPError as e:
                error_msg = f"Failed to publish to LinkedIn: {e}"
                logger.error(error_msg)
                
                # Provide helpful error messages for common issues
                if e.response is not None:
                    if e.response.status_code == 401:
                        error_msg += " (Access token expired or invalid)"
                    elif e.response.status_code == 403:
                        error_msg += " (Insufficient permissions - need 'w_member_social')"
                    elif e.response.status_code == 429:
                        error_msg += " (Rate limit exceeded - try again later)"
                
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
