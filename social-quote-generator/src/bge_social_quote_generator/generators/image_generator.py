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
            logger.debug(f"Platform dimensions: {dimensions}")
            
            # Load or create background template with author-specific color
            image = self._load_template(platform, dimensions, quote_data.quote_source)
            
            # Check if landscape layout (width > height)
            is_landscape = dimensions[0] > dimensions[1]
            logger.debug(f"Is landscape: {is_landscape} (width={dimensions[0]}, height={dimensions[1]})")
            
            if is_landscape:
                # Use new 3-column layout for landscape
                logger.info(f"Using new 3-column landscape layout for {platform}")
                image = self._render_landscape_layout(image, quote_data, dimensions)
            else:
                # Use original layout for square/portrait
                # Add episode cover
                image = self._add_episode_cover(image, quote_data.episode_number, dimensions)
                
                # Render quote text with author
                image = self._render_quote(image, quote_data.quote, quote_data.quote_source, dimensions)
                
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
            file_path = self._save_image(image, quote_data.episode_number, platform, quote_data.quote_source)
            
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
    
    def _load_template(self, platform: str, dimensions: Tuple[int, int], quote_source: str = None) -> Image.Image:
        """
        Load background template for platform or create solid color background.
        Supports author-specific template images.
        
        Args:
            platform: Target platform
            dimensions: Image dimensions (width, height)
            quote_source: Source of the quote (for author-specific backgrounds)
            
        Returns:
            PIL Image object
        """
        # Check cache first
        cache_key = f"{platform}_{dimensions[0]}x{dimensions[1]}_{quote_source}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key].copy()
        
        # Try to load author-specific template first
        author_template_path = self._get_author_template_path(platform, quote_source)
        
        if author_template_path and os.path.exists(author_template_path):
            try:
                logger.debug(f"Loading author-specific template from {author_template_path}")
                image = Image.open(author_template_path).convert("RGB")
                
                # Resize if dimensions don't match
                if image.size != dimensions:
                    logger.debug(f"Resizing template from {image.size} to {dimensions}")
                    image = image.resize(dimensions, Image.Resampling.LANCZOS)
                
                # Cache the template
                self._template_cache[cache_key] = image.copy()
                return image
                
            except Exception as e:
                logger.warning(f"Failed to load author template {author_template_path}: {e}. Trying default template.")
        
        # Fall back to default platform template
        template_path = self.image_settings.get_platform_template(platform)
        
        if template_path and os.path.exists(template_path):
            try:
                logger.debug(f"Loading default template from {template_path}")
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
        
        # Create solid color background with author-specific color
        logger.debug(f"Creating solid color background ({dimensions})")
        bg_color = self._get_background_color_for_author(quote_source)
        image = Image.new("RGB", dimensions, bg_color)
        
        # Cache the background
        self._template_cache[cache_key] = image.copy()
        return image
    
    def _get_author_template_path(self, platform: str, quote_source: str) -> Optional[str]:
        """
        Get path to author-specific template image.
        
        Args:
            platform: Target platform
            quote_source: Source of the quote (claude, openai, llama, deepseek)
            
        Returns:
            Path to author-specific template or None
        """
        if not quote_source:
            return None
        
        templates_dir = self.image_settings.templates_dir
        
        # Determine if landscape or square based on platform
        is_landscape = platform in ['twitter', 'facebook', 'linkedin']
        layout = 'landscape' if is_landscape else 'square'
        
        # Try author-specific template: {author}_{layout}.png
        # e.g., claude_landscape.png, openai_square.png
        author_template = f"{quote_source.lower()}_{layout}.png"
        author_template_path = os.path.join(templates_dir, author_template)
        
        if os.path.exists(author_template_path):
            return author_template_path
        
        return None
    
    def _get_background_color_for_author(self, quote_source: str) -> Tuple[int, int, int]:
        """
        Get background color based on quote author.
        
        Args:
            quote_source: Source of the quote (claude, openai, llama, deepseek)
            
        Returns:
            RGB tuple for background color
        """
        # Author-specific background colors
        author_colors = {
            'claude': '#1a2332',      # Dark blue-grey
            'openai': '#2d1a2e',      # Dark purple
            'llama': '#1a2e1a',       # Dark green
            'deepseek': '#2e1a1a'     # Dark red
        }
        
        hex_color = author_colors.get(quote_source.lower() if quote_source else None, self.image_settings.background_color)
        return self._hex_to_rgb(hex_color)
    
    def _render_landscape_layout(
        self,
        image: Image.Image,
        quote_data: EpisodeQuote,
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """
        Render landscape layout with 3-column grid:
        - Left column: logo, guests, episode cover
        - Right 2 columns: episode title/number at top, quote box below
        
        Args:
            image: PIL Image object
            quote_data: Episode quote data
            dimensions: Image dimensions (width, height)
            
        Returns:
            Modified PIL Image object
        """
        width, height = dimensions
        
        # Define column widths (left column ~25%, right 2 columns ~75%)
        left_col_width = width // 4
        right_cols_width = width - left_col_width
        
        padding = 30
        
        # === LEFT COLUMN ===
        left_x = padding
        current_y = padding
        
        # 1. Add logo at top (preserve aspect ratio)
        logo_path = self.image_settings.logo_path
        logo_height = 0
        if os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert("RGBA")
                
                # Calculate size preserving aspect ratio
                max_logo_width = left_col_width - padding * 2
                original_width, original_height = logo.size
                aspect_ratio = original_height / original_width
                logo_width = max_logo_width
                logo_height = int(logo_width * aspect_ratio)
                
                logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                image.paste(logo, (left_x, current_y), logo)
                image = image.convert("RGB")
                
                current_y += logo_height + padding
            except Exception as e:
                logger.warning(f"Failed to add logo: {e}")
        
        # Recreate draw object after image mode conversions
        draw = ImageDraw.Draw(image)
        
        # 2. Add guests with bigger font
        if quote_data.formatted_guests:
            guests_font_size = 32
            guests_font = self._load_font(self.image_settings.default_font, guests_font_size)
            guests_color = self._hex_to_rgb("#FFFFFF")
            
            # Wrap guests text to fit left column
            guests_text = f"con {quote_data.formatted_guests}"
            guests_lines = self._wrap_text_to_width(guests_text, guests_font, left_col_width - padding * 2, draw)
            
            for line in guests_lines:
                draw.text((left_x, current_y), line, font=guests_font, fill=guests_color)
                current_y += guests_font_size + 10
            
            current_y += padding
        
        # 3. Add episode cover at bottom of left column
        covers_dir = self.image_settings.cover.get('covers_dir', 'assets/covers') if hasattr(self.image_settings, 'cover') else 'assets/covers'
        cover_filename = f"BGE {quote_data.episode_number}.png"
        cover_path = os.path.join(covers_dir, cover_filename)
        
        if os.path.exists(cover_path):
            try:
                cover = Image.open(cover_path).convert("RGBA")
                cover_width = left_col_width - padding * 2
                
                # Preserve aspect ratio for cover
                original_width, original_height = cover.size
                aspect_ratio = original_height / original_width
                cover_height = int(cover_width * aspect_ratio)
                
                cover = cover.resize((cover_width, cover_height), Image.Resampling.LANCZOS)
                
                # Position at bottom of left column
                cover_y = height - cover_height - padding
                
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                image.paste(cover, (left_x, cover_y), cover)
                image = image.convert("RGB")
            except Exception as e:
                logger.warning(f"Failed to add episode cover: {e}")
        
        # Recreate draw object after image mode conversions
        draw = ImageDraw.Draw(image)
        
        # === RIGHT COLUMNS (2 & 3) ===
        right_x = left_col_width + padding
        right_width = right_cols_width - padding * 2
        
        # 1. Episode title and number at top
        title_font_size = 48
        title_font = self._load_font(self.image_settings.default_font, title_font_size)
        title_color = self._hex_to_rgb("#FFFFFF")
        
        title_text = f"BGE {quote_data.episode_number}: {quote_data.titolo}"
        title_lines = self._wrap_text_to_width(title_text, title_font, right_width, draw)
        
        title_y = padding
        for line in title_lines:
            draw.text((right_x, title_y), line, font=title_font, fill=title_color)
            title_y += title_font_size + 10
        
        title_y += padding
        
        # 2. Quote box with adaptive text size
        quote_box_y = title_y
        quote_box_height = height - quote_box_y - padding
        
        image = self._render_adaptive_quote_box(
            image,
            quote_data.quote,
            quote_data.quote_source,
            right_x,
            quote_box_y,
            right_width,
            quote_box_height
        )
        
        return image
    
    def _wrap_text_to_width(
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
            font: Font to use
            max_width: Maximum width in pixels
            draw: ImageDraw object
            
        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _render_adaptive_quote_box(
        self,
        image: Image.Image,
        quote: str,
        quote_source: str,
        x: int,
        y: int,
        box_width: int,
        box_height: int
    ) -> Image.Image:
        """
        Render quote box with adaptive text size to fill the box nicely.
        
        Args:
            image: PIL Image object
            quote: Quote text
            quote_source: Source of the quote
            x: X position of box
            y: Y position of box
            box_width: Width of box
            box_height: Height of box
            
        Returns:
            Modified PIL Image object
        """
        draw = ImageDraw.Draw(image)
        
        # Box styling
        box_color = self._hex_to_rgb(self.image_settings.text.get('box_color', '#000000'))
        box_opacity = self.image_settings.text.get('box_opacity', 180)
        box_padding = self.image_settings.text.get('box_padding', 40)
        corner_radius = self.image_settings.text.get('box_corner_radius', 20)
        
        # Draw rounded rectangle background
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        box_color_rgba = box_color + (box_opacity,)
        overlay_draw.rounded_rectangle(
            [(x, y), (x + box_width, y + box_height)],
            radius=corner_radius,
            fill=box_color_rgba
        )
        
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        image = Image.alpha_composite(image, overlay)
        image = image.convert('RGB')
        
        # Calculate adaptive font size
        available_width = box_width - box_padding * 2
        available_height = box_height - box_padding * 2
        
        # Reserve space for author
        author_font_size = self.image_settings.text.get('author_font_size', 32)
        author_space = author_font_size + 20
        available_height -= author_space
        
        # Find optimal font size
        quote_font_name = self.image_settings.text.get('quote_font', self.image_settings.default_font)
        optimal_font_size = self._find_optimal_font_size(
            quote,
            quote_font_name,
            available_width,
            available_height,
            draw
        )
        
        # Render quote text
        quote_font = self._load_font(quote_font_name, optimal_font_size)
        quote_color = self._hex_to_rgb(self.image_settings.quote_color)
        
        lines = self._wrap_text_to_width(quote, quote_font, available_width, draw)
        
        # Calculate line height and total height
        line_height = optimal_font_size + 10
        total_text_height = len(lines) * line_height
        
        # Center text vertically in available space
        text_y = y + box_padding + (available_height - total_text_height) // 2
        
        # Draw each line
        draw = ImageDraw.Draw(image)
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=quote_font)
            text_width = bbox[2] - bbox[0]
            text_x = x + box_padding + (available_width - text_width) // 2
            line_y = text_y + i * line_height
            
            draw.text((text_x, line_y), line, font=quote_font, fill=quote_color)
        
        # Add author attribution
        author_name = self._get_author_name(quote_source)
        author_font = self._load_font(quote_font_name, author_font_size)
        author_color = self._hex_to_rgb(self.image_settings.text.get('author_color', '#CCCCCC'))
        author_prefix = self.image_settings.text.get('author_prefix', '— ')
        
        author_text = f"{author_prefix}{author_name}"
        bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = bbox[2] - bbox[0]
        
        author_x = x + box_width - box_padding - author_width
        author_y = y + box_height - box_padding - author_font_size
        
        draw.text((author_x, author_y), author_text, font=author_font, fill=author_color)
        
        return image
    
    def _find_optimal_font_size(
        self,
        text: str,
        font_name: str,
        max_width: int,
        max_height: int,
        draw: ImageDraw.ImageDraw,
        min_size: int = 20,
        max_size: int = 60
    ) -> int:
        """
        Find optimal font size that fills the box nicely.
        
        Args:
            text: Text to render
            font_name: Font filename
            max_width: Maximum width available
            max_height: Maximum height available
            draw: ImageDraw object
            min_size: Minimum font size
            max_size: Maximum font size
            
        Returns:
            Optimal font size
        """
        # Binary search for optimal size
        best_size = min_size
        
        for size in range(max_size, min_size - 1, -2):
            font = self._load_font(font_name, size)
            lines = self._wrap_text_to_width(text, font, max_width, draw)
            
            line_height = size + 10
            total_height = len(lines) * line_height
            
            if total_height <= max_height:
                best_size = size
                break
        
        return best_size
    
    def _render_quote(
        self, 
        image: Image.Image, 
        quote: str,
        quote_source: str,
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """
        Render centered quote text on image with text wrapping and author attribution.
        
        Args:
            image: PIL Image object
            quote: Quote text to render
            quote_source: Source of the quote (claude, openai, llama, deepseek)
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
        
        # Load quote font (use quote_font if specified, otherwise default_font)
        quote_font_name = self.image_settings.text.get('quote_font', self.image_settings.default_font)
        font = self._load_font(quote_font_name, font_size)
        
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
        
        # Get author name based on quote source
        author_name = self._get_author_name(quote_source)
        
        # Calculate author text dimensions if enabled
        author_enabled = self.image_settings.text.get('author_enabled', True)
        author_height = 0
        if author_enabled and author_name:
            author_font_size = self.image_settings.text.get('author_font_size', 28)
            author_height = author_font_size + 20  # Add spacing
        
        # Draw background box if enabled
        box_enabled = self.image_settings.text.get('box_enabled', False)
        if box_enabled:
            self._draw_text_box(image, lines, font, start_y, line_height, width, dimensions, author_height)
            # Redraw after adding box
            draw = ImageDraw.Draw(image)
        
        # Render each line centered horizontally
        quote_color = self._hex_to_rgb(self.image_settings.quote_color)
        
        for i, line in enumerate(lines):
            # Get text bounding box for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Center horizontally
            x = (width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Draw text (no shadow when using box background)
            if not box_enabled:
                shadow_offset = 2
                shadow_color = (0, 0, 0)
                draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=shadow_color)
            draw.text((x, y), line, font=font, fill=quote_color)
        
        # Add author attribution if enabled
        if author_enabled and author_name:
            self._render_author(image, author_name, start_y + total_height + 10, width)
        
        return image
    
    def _get_author_name(self, quote_source: str) -> str:
        """
        Get author name based on quote source.
        
        Args:
            quote_source: Source of the quote (claude, openai, llama, deepseek)
            
        Returns:
            Author name string
        """
        author_map = {
            'claude': 'Brigante Claudio',
            'openai': 'Geek Estinto',
            'llama': 'Metante',
            'deepseek': 'Deep Geek'
        }
        return author_map.get(quote_source.lower(), 'Geek Anonimo')
    
    def _render_author(
        self,
        image: Image.Image,
        author_name: str,
        y_position: int,
        width: int
    ) -> None:
        """
        Render author attribution at the bottom right of the quote.
        
        Args:
            image: PIL Image object
            author_name: Name of the author
            y_position: Y position to render author
            width: Image width
        """
        draw = ImageDraw.Draw(image)
        
        # Get author settings
        author_font_size = self.image_settings.text.get('author_font_size', 28)
        author_color = self._hex_to_rgb(self.image_settings.text.get('author_color', '#CCCCCC'))
        author_prefix = self.image_settings.text.get('author_prefix', '— ')
        
        # Load font (use quote font for consistency)
        quote_font_name = self.image_settings.text.get('quote_font', self.image_settings.default_font)
        author_font = self._load_font(quote_font_name, author_font_size)
        
        # Format author text
        author_text = f"{author_prefix}{author_name}"
        
        # Calculate position (right-aligned within quote area)
        bbox = draw.textbbox((0, 0), author_text, font=author_font)
        text_width = bbox[2] - bbox[0]
        
        # Position on the right side with some padding
        max_width = min(self.image_settings.quote_max_width, width - 100)
        x = ((width - max_width) // 2) + max_width - text_width
        
        # Draw author text
        draw.text((x, y_position), author_text, font=author_font, fill=author_color)
    
    def _draw_text_box(
        self,
        image: Image.Image,
        lines: List[str],
        font: ImageFont.FreeTypeFont,
        start_y: int,
        line_height: int,
        width: int,
        dimensions: Tuple[int, int],
        author_height: int = 0
    ) -> None:
        """
        Draw a rounded rectangle background box behind the text.
        
        Args:
            image: PIL Image object
            lines: List of text lines
            font: Font used for text
            start_y: Starting Y position of text
            line_height: Height of each line
            width: Image width
            dimensions: Image dimensions
            author_height: Additional height for author attribution
        """
        # Get box settings from config
        box_color = self._hex_to_rgb(self.image_settings.text.get('box_color', '#000000'))
        box_opacity = self.image_settings.text.get('box_opacity', 180)
        box_padding = self.image_settings.text.get('box_padding', 40)
        corner_radius = self.image_settings.text.get('box_corner_radius', 20)
        
        # Calculate the bounding box for all text
        temp_draw = ImageDraw.Draw(image)
        max_text_width = 0
        
        for line in lines:
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            max_text_width = max(max_text_width, text_width)
        
        # Calculate box dimensions (include author height if present)
        total_text_height = len(lines) * line_height + author_height
        box_width = max_text_width + (box_padding * 2)
        box_height = total_text_height + (box_padding * 2)
        
        # Calculate box position (centered)
        box_x1 = (width - box_width) // 2
        box_y1 = start_y - box_padding
        box_x2 = box_x1 + box_width
        box_y2 = box_y1 + box_height
        
        # Create a transparent overlay for the box
        overlay = Image.new('RGBA', dimensions, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Draw rounded rectangle with transparency
        box_color_rgba = box_color + (box_opacity,)
        overlay_draw.rounded_rectangle(
            [(box_x1, box_y1), (box_x2, box_y2)],
            radius=corner_radius,
            fill=box_color_rgba
        )
        
        # Composite the overlay onto the original image
        if image.mode != 'RGBA':
            image_rgba = image.convert('RGBA')
        else:
            image_rgba = image
        
        image_rgba = Image.alpha_composite(image_rgba, overlay)
        
        # Convert back to RGB
        rgb_image = image_rgba.convert('RGB')
        image.paste(rgb_image)
    
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
    
    def _add_episode_cover(
        self,
        image: Image.Image,
        episode_number: str,
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """
        Add episode cover image overlay.
        
        Args:
            image: PIL Image object
            episode_number: Episode number
            dimensions: Image dimensions (width, height)
            
        Returns:
            Modified PIL Image object
        """
        # Check if cover is enabled
        cover_settings = self.image_settings.cover if hasattr(self.image_settings, 'cover') else {}
        if not cover_settings.get('enabled', True):
            return image
        
        # Build cover path: assets/covers/BGE {number}.png
        covers_dir = cover_settings.get('covers_dir', 'assets/covers')
        cover_filename = f"BGE {episode_number}.png"
        cover_path = os.path.join(covers_dir, cover_filename)
        
        # Check if cover file exists
        if not os.path.exists(cover_path):
            logger.warning(f"Episode cover not found: {cover_path}. Skipping cover overlay.")
            return image
        
        try:
            # Load cover image
            cover = Image.open(cover_path).convert("RGBA")
            
            # Resize cover to configured size
            cover_size = tuple(cover_settings.get('size', [200, 200]))
            cover = cover.resize(cover_size, Image.Resampling.LANCZOS)
            
            # Calculate position based on configuration
            position = self._calculate_cover_position(
                dimensions,
                cover_size,
                cover_settings.get('position', 'top-left'),
                cover_settings.get('padding', 20)
            )
            
            # Convert base image to RGBA for transparency support
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            # Paste cover with transparency
            image.paste(cover, position, cover)
            
            # Convert back to RGB
            image = image.convert("RGB")
            
            logger.debug(f"Added episode cover at position {position}")
            
        except Exception as e:
            logger.warning(f"Failed to add episode cover: {e}")
        
        return image
    
    def _calculate_cover_position(
        self,
        image_dimensions: Tuple[int, int],
        cover_size: Tuple[int, int],
        position: str,
        padding: int
    ) -> Tuple[int, int]:
        """
        Calculate cover position based on configuration.
        
        Args:
            image_dimensions: Image dimensions (width, height)
            cover_size: Cover dimensions (width, height)
            position: Position string (top-left, top-right, bottom-left, bottom-right, center-left, center-right)
            padding: Padding from edges in pixels
            
        Returns:
            (x, y) coordinates for cover placement
        """
        img_width, img_height = image_dimensions
        cover_width, cover_height = cover_size
        
        if position == "top-left":
            return (padding, padding)
        elif position == "top-right":
            return (img_width - cover_width - padding, padding)
        elif position == "bottom-left":
            return (padding, img_height - cover_height - padding)
        elif position == "bottom-right":
            return (img_width - cover_width - padding, img_height - cover_height - padding)
        elif position == "center-left":
            return (padding, (img_height - cover_height) // 2)
        elif position == "center-right":
            return (img_width - cover_width - padding, (img_height - cover_height) // 2)
        else:
            # Default to top-left
            logger.warning(f"Unknown cover position: {position}. Using top-left.")
            return (padding, padding)
    
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
        platform: str,
        quote_source: str
    ) -> str:
        """
        Save image with naming convention: bge_{episode_number}_{author}_{platform}_{timestamp}.png
        
        Args:
            image: PIL Image object to save
            episode_number: Episode number
            platform: Target platform
            quote_source: Source of the quote (claude, openai, deepseek, llama)
            
        Returns:
            Full path to saved image file
            
        Raises:
            ImageGenerationError: If save fails
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bge_{episode_number}_{quote_source}_{platform}_{timestamp}.png"
            
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
