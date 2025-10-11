"""Base classes and data models for quote extraction."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EpisodeQuote:
    """
    Data class representing an episode with its quote and metadata.
    
    Attributes:
        episode_number: Episode number as string
        title: Full episode title
        quote: Selected quote text
        quote_source: Source of the quote (claude, openai, deepseek, llama)
        guests: List of guest names
        date: Publication date (YYYY-MM-DD format)
        youtube_id: YouTube video ID
        tags: List of topic tags
        duration: Episode duration in seconds
        description: Full episode description
        host: Host name
        titolo: Episode title without number prefix
        summary: List of key topics discussed
    """
    
    episode_number: str
    title: str
    quote: str
    quote_source: str
    guests: List[str]
    date: str
    youtube_id: str
    tags: List[str]
    duration: int = 0
    description: str = ""
    host: str = ""
    titolo: str = ""
    summary: List[str] = None
    
    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.summary is None:
            self.summary = []
    
    @property
    def youtube_url(self) -> str:
        """Get full YouTube URL for the episode."""
        return f"https://youtube.com/watch?v={self.youtube_id}"
    
    @property
    def formatted_guests(self) -> str:
        """Get comma-separated list of guest names."""
        return ", ".join(self.guests)
    
    @property
    def formatted_tags(self) -> List[str]:
        """Get formatted hashtags from episode tags."""
        return [f"#{tag}" for tag in self.tags]
    
    def __str__(self) -> str:
        """String representation of the episode quote."""
        return f"Episode {self.episode_number}: {self.titolo} - {self.quote_source}"
