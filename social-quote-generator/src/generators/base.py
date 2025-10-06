"""Base classes and data models for image generation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass
class GeneratedImage:
    """
    Data class representing a generated quote image.
    
    Attributes:
        file_path: Full path to the saved image file
        platform: Target platform (instagram, twitter, facebook, linkedin)
        episode_number: Episode number as string
        dimensions: Image dimensions as (width, height) tuple
        timestamp: When the image was generated
    """
    
    file_path: str
    platform: str
    episode_number: str
    dimensions: Tuple[int, int]
    timestamp: datetime
    
    def __str__(self) -> str:
        """String representation of the generated image."""
        return f"Image for Episode {self.episode_number} ({self.platform}): {self.file_path}"
