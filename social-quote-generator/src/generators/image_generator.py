"""Image generation module for BGE Social Quote Generator."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from ..config import Config
from ..extractors.base import EpisodeQuote
from .base import GeneratedImage


logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """Raised when image generation fails."""
    pass


class ImageGenerator:
    """
    Generates branded quote images for social media platforms.
    
    Uses Pillow (PIL) to create images with quotes, branding, and metadata.
    Supports multiple platforms with different dimensions and templates.
    """
    
    def __init__(self, config: Config):
        """
        Initialize image generator with configuration.
        
        Args:
            config: Configuration object with image settings
        """
        self.config = config
        self.image_settings = config.image_settings
        
        # Cache for loaded fonts and templates
        self._font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}
        self._template_cache: Dict[str, Image.Image] = {}
        
        # Ensure output directory exists
        os.makedirs(config.output_dir, exist_ok=True)
        
        logger.info(f"ImageGenerator initialized with output dir: {config.output_dir}")
    
    def generate(
        self, 
        quote_data: EpisodeQuote, 
        platform: str = "instagram"
    ) -> GeneratedImage:
        """
        Generate image for specified platform.
        
        Args:
            quote_data: Episode quote data
            platform: Target platform (instagram, twitter, facebook, linkedin)
            
        Returns:
            GeneratedImage object with file path and metadata
            
        Raises:
            ImageGenerationError: If image generation fails
        """
        try:
            logger.info(f"Generating image for episode {quote_data.episode_number} ({platform})")
            
            # Get platform dimensions
            dimensions = self.image_settings.get_platform_dimensions(platform)
            
            # Load or create background template
            image = self._load_template(platform, dimensions)
            
            # Render quote text
            image = self._render_quote(image, quote_data.quote, dimensions)
            
            # Add logo overlay
            image = self._add_logo(image, dimensions)
            
            # Render episode metadata
            metadata = {
                "episode_number": quote_data.episode_number,
                "guests": quote_data.formatted_guests,
                "title": quote_data.titolo
            }
            image = self._render_metadata(image, metadata, dimensions)
            
            # Save image
            file_path = self._save_image(image, quote_data.episode_number, platform)
            
            logger.info(f"Successfully generated image: {file_path}")
            
            return GeneratedImage(
                file_path=file_path,
                platform=platform,
                episode_number=quote_data.episode_number,
                dimensions=dimensions,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Failed to generate image for episode {quote_data.episode_number} ({platform}): {e}"
            logger.error(error_msg)
            raise ImageGenerationError(error_msg) from e
    
    def _load_template(self, platform: str, dimensions: Tuple[int, int]) -> Image.Image:
        """
        Load background template for platform or create solid color background.
        
        Args:
            platform: Target platform
            dimensions: Image dimensions (width, height)
            
        Returns:
            PIL Image object
        """
        # Check cache first
        cache_key = f"{platform}_{dimensions[0]}x{dimensions[1]}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key].copy()
        
        # Try to load template file
        template_path = self.image_settings.get_platform_template(platform)
        
        if template_path and os.path.exists(template_path):
            try:
                logger.debug(f"Loading template from {template_path}")
                image = Image.open(template_path).convert("RGB")
                
                # Resize if dimensions don't match
                if image.size != dimensions:
                    logger.debug(f"Resizing template from {image.size} to {dimensions}")
                    image = image.resize(dimensions, Image.Resampling.LANCZOS)
                
                # Cache the template
                self._template_cache[cache_key] = image.copy()
                return image
                
            except Exception as e:
                logger.warning(f"Failed to load template {template_path}: {e}. Using solid color background.")
        
        # Create solid color background
        logger.debug(f"Creating solid color background ({dimensions})")
        bg_color = self._hex_to_rgb(self.image_settings.background_color)
        image = Image.new("RGB", dimensions, bg_color)
        
        # Cache the background
        self._template_cache[cache_key] = image.copy()
        return image
    
    def _render_quote(
        self, 
        image: Image.Image, 
        quote: str, 
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """
        Render centered quote text on image with text wrapping.
        
        Args:
            image: PIL Image object
            quote: Quote text to render
            dimensions: Image dimensions (width, height)
            
        Returns:
            Modified PIL Image object
        """
        draw = ImageDraw.Draw(image)
        width, height = dimensions
        
        # Calculate max width for text (with padding)
        max_width = min(self.image_settings.quote_max_width, width - 100)
        
        # Determine font size (with dynamic adjustment for long quotes)
        base_font_size = self.image_settings.quote_font_size
        font_size = self._calculate_font_size(quote, base_font_size, max_width)
        
        # Load font
        font = self._load_font(self.image_settings.default_font, font_size)
        
        # Wrap text to fit within max width
        lines = self._wrap_text(quote, font, max_width, draw)
        
        # Calculate total text block height
        line_height = font_size + 10  # Add some line spacing
        total_height = len(lines) * line_height
        
        # Calculate starting Y position to center text vertically
        # Leave space at top for logo and bottom for metadata
        available_height = height - 200  # Reserve 100px top and 100px bottom
        start_y = (height - total_height) // 2
        start_y = max(120, min(start_y, height - total_height - 120))  # Clamp to safe range
        
        # Render each line centered horizontally
        quote_color = self._hex_to_rgb(self.image_settings.quote_color)
        
        for i, line in enumerate(lines):
            # Get text bounding box for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Center horizontally
            x = (width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Draw text with slight shadow for better readability
            shadow_offset = 2
            shadow_color = (0, 0, 0)
            draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=shadow_color)
            draw.text((x, y), line, font=font, fill=quote_color)
        
        return image
    
    def _calculate_font_size(
        self, 
        text: str, 
        base_size: int, 
        max_width: int
    ) -> int:
        """
        Calculate appropriate font size for text, reducing for long quotes.
        
        Args:
            text: Text to render
            base_size: Base font size from configuration
            max_width: Maximum width available for text
            
        Returns:
            Adjusted font size
        """
        # Simple heuristic: reduce font size for very long quotes
        text_length = len(text)
        
        if text_length <= 100:
            return base_size
        elif text_length <= 200:
            return int(base_size * 0.9)
        elif text_length <= 300:
            return int(base_size * 0.8)
        else:
            return int(base_size * 0.7)
    
    def _wrap_text(
        self, 
        text: str, 
        font: ImageFont.FreeTypeFont, 
        max_width: int,
        draw: ImageDraw.ImageDraw
    ) -> List[str]:
        """
        Wrap text to fit within max width.
        
        Args:
            text: Text to wrap
            font: Font to use for measuring
            max_width: Maximum width in pixels
            draw: ImageDraw object for text measurement
            
        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Try adding word to current line
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _add_logo(
        self, 
        image: Image.Image, 
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """
        Add BGE logo overlay with transparency and configurable positioning.
        
        Args:
            image: PIL Image object
            dimensions: Image dimensions (width, height)
            
        Returns:
            Modified PIL Image object
        """
        logo_path = self.image_settings.logo_path
        
        # Check if logo file exists
        if not os.path.exists(logo_path):
            logger.warning(f"Logo file not found: {logo_path}. Skipping logo overlay.")
            return image
        
        try:
            # Load logo with transparency
            logo = Image.open(logo_path).convert("RGBA")
            
            # Resize logo to configured size
            logo_size = self.image_settings.logo_size
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
            
            # Calculate position based on configuration
            position = self._calculate_logo_position(
                dimensions, 
                logo_size, 
                self.image_settings.logo_position
            )
            
            # Convert base image to RGBA for transparency support
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            # Paste logo with transparency
            image.paste(logo, position, logo)
            
            # Convert back to RGB
            image = image.convert("RGB")
            
            logger.debug(f"Added logo at position {position}")
            
        except Exception as e:
            logger.warning(f"Failed to add logo: {e}")
        
        return image
    
    def _calculate_logo_position(
        self, 
        image_dimensions: Tuple[int, int], 
        logo_size: Tuple[int, int], 
        position: str
    ) -> Tuple[int, int]:
        """
        Calculate logo position based on configuration.
        
        Args:
            image_dimensions: Image dimensions (width, height)
            logo_size: Logo dimensions (width, height)
            position: Position string (top-left, top-right, bottom-left, bottom-right)
            
        Returns:
            (x, y) coordinates for logo placement
        """
        img_width, img_height = image_dimensions
        logo_width, logo_height = logo_size
        padding = 20  # Padding from edges
        
        if position == "top-left":
            return (padding, padding)
        elif position == "top-right":
            return (img_width - logo_width - padding, padding)
        elif position == "bottom-left":
            return (padding, img_height - logo_height - padding)
        elif position == "bottom-right":
            return (img_width - logo_width - padding, img_height - logo_height - padding)
        else:
            # Default to top-right
            logger.warning(f"Unknown logo position: {position}. Using top-right.")
            return (img_width - logo_width - padding, padding)
    
    def _render_metadata(
        self, 
        image: Image.Image, 
        metadata: Dict[str, str], 
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """
        Render episode metadata at bottom of image.
        
        Args:
            image: PIL Image object
            metadata: Dictionary with episode_number, guests, title
            dimensions: Image dimensions (width, height)
            
        Returns:
            Modified PIL Image object
        """
        draw = ImageDraw.Draw(image)
        width, height = dimensions
        
        # Load metadata font
        font_size = self.image_settings.metadata_font_size
        font = self._load_font(self.image_settings.default_font, font_size)
        
        # Format metadata text
        episode_text = f"Episodio {metadata['episode_number']}"
        
        # Add guests if available
        if metadata.get('guests'):
            guests_text = f"con {metadata['guests']}"
        else:
            guests_text = ""
        
        # Calculate positions (bottom of image with padding)
        padding = 30
        metadata_color = self._hex_to_rgb(self.image_settings.metadata_color)
        
        # Render episode number
        bbox = draw.textbbox((0, 0), episode_text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height - padding - font_size - 10
        
        draw.text((x, y), episode_text, font=font, fill=metadata_color)
        
        # Render guests below episode number if available
        if guests_text:
            bbox = draw.textbbox((0, 0), guests_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height - padding
            
            draw.text((x, y), guests_text, font=font, fill=metadata_color)
        
        return image
    
    def _save_image(
        self, 
        image: Image.Image, 
        episode_number: str, 
        platform: str
    ) -> str:
        """
        Save image with naming convention: bge_{episode_number}_{platform}_{timestamp}.png
        
        Args:
            image: PIL Image object to save
            episode_number: Episode number
            platform: Target platform
            
        Returns:
            Full path to saved image file
            
        Raises:
            ImageGenerationError: If save fails
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bge_{episode_number}_{platform}_{timestamp}.png"
            
            # Full path
            file_path = os.path.join(self.config.output_dir, filename)
            
            # Save image
            image.save(file_path, "PNG", optimize=True)
            
            logger.debug(f"Saved image to {file_path}")
            
            return file_path
            
        except Exception as e:
            raise ImageGenerationError(f"Failed to save image: {e}") from e
    
    def _load_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """
        Load font with caching. Falls back to default font if not found.
        
        Args:
            font_name: Font filename
            size: Font size in points
            
        Returns:
            ImageFont object
        """
        # Check cache
        cache_key = (font_name, size)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # Try to load custom font
        font_path = os.path.join(self.image_settings.fonts_dir, font_name)
        
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, size)
                logger.debug(f"Loaded font: {font_path} (size {size})")
            else:
                # Try system font paths
                logger.warning(f"Font not found at {font_path}, trying system fonts")
                font = ImageFont.truetype(font_name, size)
        except Exception as e:
            # Fall back to default PIL font
            logger.warning(f"Failed to load font {font_name}: {e}. Using default font.")
            font = ImageFont.load_default()
        
        # Cache the font
        self._font_cache[cache_key] = font
        
        return font
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string (e.g., "#FFFFFF")
            
        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
