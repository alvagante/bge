"""Quote extraction logic for BGE episodes."""

import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import frontmatter

from ..config import Config
from .base import EpisodeQuote


logger = logging.getLogger(__name__)


class QuoteExtractionError(Exception):
    """Raised when quote extraction fails."""
    pass


class QuoteExtractor:
    """
    Extracts quotes and metadata from BGE episode files.
    
    Supports extracting quotes from:
    - YAML frontmatter in episode markdown files
    - Separate text files in assets/texts/ directory
    
    Implements quote source selection based on configuration preferences.
    """
    
    def __init__(self, config: Config):
        """
        Initialize quote extractor with configuration.
        
        Args:
            config: Configuration object with episodes_dir, texts_dir, and quote settings
        """
        self.config = config
        self.episodes_dir = Path(config.episodes_dir)
        self.texts_dir = Path(config.texts_dir)
        
        # Validate directories exist
        if not self.episodes_dir.exists():
            logger.warning(f"Episodes directory not found: {self.episodes_dir}")
        if not self.texts_dir.exists():
            logger.warning(f"Texts directory not found: {self.texts_dir}")
    
    def extract_episode(self, episode_number: str) -> Optional[EpisodeQuote]:
        """
        Extract quote data for a specific episode.
        
        Args:
            episode_number: Episode number to extract
            
        Returns:
            EpisodeQuote object if successful, None if episode not found or extraction fails
        """
        episode_file = self.episodes_dir / f"{episode_number}.md"
        
        if not episode_file.exists():
            logger.error(f"Episode file not found: {episode_file}")
            return None
        
        try:
            episode_data = self._parse_episode_file(episode_file)
            
            # Select quote based on configuration
            quote, quote_source = self._select_quote(episode_number, episode_data)
            
            if not quote:
                logger.error(f"No quote found for episode {episode_number}")
                return None
            
            # Build EpisodeQuote object
            return self._build_episode_quote(episode_number, episode_data, quote, quote_source)
            
        except Exception as e:
            logger.error(f"Failed to extract episode {episode_number}: {e}", exc_info=True)
            return None
    
    def extract_all_episodes(self) -> List[EpisodeQuote]:
        """
        Extract quote data for all available episodes.
        
        Returns:
            List of EpisodeQuote objects for successfully extracted episodes
        """
        if not self.episodes_dir.exists():
            logger.error(f"Episodes directory not found: {self.episodes_dir}")
            return []
        
        episodes = []
        episode_files = sorted(self.episodes_dir.glob("*.md"), key=lambda p: self._extract_episode_number(p))
        
        logger.info(f"Found {len(episode_files)} episode files")
        
        for episode_file in episode_files:
            episode_number = episode_file.stem
            
            # Skip non-numeric episode files
            if not episode_number.isdigit():
                logger.debug(f"Skipping non-numeric episode file: {episode_file.name}")
                continue
            
            episode_quote = self.extract_episode(episode_number)
            if episode_quote:
                episodes.append(episode_quote)
                logger.debug(f"Successfully extracted episode {episode_number}")
            else:
                logger.warning(f"Failed to extract episode {episode_number}")
        
        logger.info(f"Successfully extracted {len(episodes)} episodes")
        return episodes
    
    def _extract_episode_number(self, path: Path) -> int:
        """
        Extract numeric episode number from file path for sorting.
        
        Args:
            path: Path to episode file
            
        Returns:
            Episode number as integer, or 0 if not numeric
        """
        try:
            return int(path.stem)
        except ValueError:
            return 0
    
    def _parse_episode_file(self, file_path: Path) -> Dict:
        """
        Parse YAML frontmatter from episode markdown file.
        
        Args:
            file_path: Path to episode markdown file
            
        Returns:
            Dictionary containing frontmatter data
            
        Raises:
            QuoteExtractionError: If file cannot be parsed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                return post.metadata
        except Exception as e:
            raise QuoteExtractionError(f"Failed to parse {file_path}: {e}")
    
    def _select_quote(self, episode_number: str, episode_data: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Select best quote based on configuration preferences.
        
        Selection logic:
        1. Try preferred source from frontmatter
        2. Try fallback sources from frontmatter
        3. Try loading from separate text files
        4. If preferred source is 'random', randomly select from available sources
        
        Args:
            episode_number: Episode number
            episode_data: Dictionary containing episode frontmatter
            
        Returns:
            Tuple of (quote_text, quote_source) or (None, None) if no quote found
        """
        preferred_source = self.config.quote_settings.preferred_source
        fallback_sources = self.config.quote_settings.fallback_sources
        
        # Handle random selection
        if preferred_source == "random":
            return self._select_random_quote(episode_number, episode_data)
        
        # Try preferred source first
        quote = self._get_quote_from_source(episode_number, episode_data, preferred_source)
        if quote:
            return quote, preferred_source
        
        # Try fallback sources
        for source in fallback_sources:
            quote = self._get_quote_from_source(episode_number, episode_data, source)
            if quote:
                logger.info(f"Using fallback source '{source}' for episode {episode_number}")
                return quote, source
        
        logger.warning(f"No quote found for episode {episode_number} from any source")
        return None, None
    
    def _select_random_quote(self, episode_number: str, episode_data: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Randomly select a quote from available sources.
        
        Args:
            episode_number: Episode number
            episode_data: Dictionary containing episode frontmatter
            
        Returns:
            Tuple of (quote_text, quote_source) or (None, None) if no quote found
        """
        available_sources = ["claude", "openai", "deepseek", "llama"]
        random.shuffle(available_sources)
        
        for source in available_sources:
            quote = self._get_quote_from_source(episode_number, episode_data, source)
            if quote:
                logger.info(f"Randomly selected source '{source}' for episode {episode_number}")
                return quote, source
        
        return None, None
    
    def _get_quote_from_source(self, episode_number: str, episode_data: Dict, source: str) -> Optional[str]:
        """
        Get quote from a specific source.
        
        Tries frontmatter first, then falls back to separate text file.
        
        Args:
            episode_number: Episode number
            episode_data: Dictionary containing episode frontmatter
            source: Quote source (claude, openai, deepseek, llama)
            
        Returns:
            Quote text if found, None otherwise
        """
        # Try frontmatter first
        frontmatter_key = f"quote_{source}"
        quote = episode_data.get(frontmatter_key)
        
        if quote and isinstance(quote, str) and quote.strip():
            # Clean up quote (remove extra whitespace and quotes)
            quote = quote.strip().strip('"').strip("'").strip()
            if quote:
                logger.debug(f"Found quote from frontmatter: {frontmatter_key}")
                return quote
        
        # Fall back to separate text file
        quote = self._load_quote_from_file(episode_number, source)
        if quote:
            logger.debug(f"Found quote from text file: {episode_number}_quote_{source}.txt")
            return quote
        
        return None
    
    def _load_quote_from_file(self, episode_number: str, source: str) -> Optional[str]:
        """
        Load quote from separate text file in assets/texts/ directory.
        
        Expected filename format: {episode_number}_quote_{source}.txt
        
        Args:
            episode_number: Episode number
            source: Quote source (claude, openai, deepseek, llama)
            
        Returns:
            Quote text if file exists and is readable, None otherwise
        """
        quote_file = self.texts_dir / f"{episode_number}_quote_{source}.txt"
        
        if not quote_file.exists():
            return None
        
        try:
            with open(quote_file, 'r', encoding='utf-8') as f:
                quote = f.read().strip().strip('"').strip("'").strip()
                if quote:
                    return quote
        except Exception as e:
            logger.warning(f"Failed to read quote file {quote_file}: {e}")
        
        return None
    
    def _build_episode_quote(
        self,
        episode_number: str,
        episode_data: Dict,
        quote: str,
        quote_source: str
    ) -> EpisodeQuote:
        """
        Build EpisodeQuote object from episode data.
        
        Args:
            episode_number: Episode number
            episode_data: Dictionary containing episode frontmatter
            quote: Selected quote text
            quote_source: Source of the quote
            
        Returns:
            EpisodeQuote object
        """
        # Extract required fields with defaults
        title = episode_data.get("title", f"Episode {episode_number}")
        titolo = episode_data.get("titolo", title)
        guests = episode_data.get("guests", [])
        date = episode_data.get("date", "")
        youtube_id = episode_data.get("youtube", "")
        tags = episode_data.get("tags", [])
        
        # Extract optional fields
        duration = episode_data.get("duration", 0)
        description = episode_data.get("description", "")
        host = episode_data.get("host", "")
        summary = episode_data.get("summary", [])
        
        # Ensure guests is a list
        if not isinstance(guests, list):
            guests = [guests] if guests else []
        
        # Ensure tags is a list
        if not isinstance(tags, list):
            tags = [tags] if tags else []
        
        # Ensure summary is a list
        if not isinstance(summary, list):
            summary = [summary] if summary else []
        
        # Convert date to string if needed
        if date:
            date = str(date)
        
        return EpisodeQuote(
            episode_number=episode_number,
            title=title,
            quote=quote,
            quote_source=quote_source,
            guests=guests,
            date=date,
            youtube_id=youtube_id,
            tags=tags,
            duration=duration,
            description=description,
            host=host,
            titolo=titolo,
            summary=summary
        )
