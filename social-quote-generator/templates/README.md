# Templates Directory

This directory contains default templates and assets for generating social media quote images.

## Template Images

### default_square.png (1080x1080)
- **Platform**: Instagram
- **Dimensions**: 1080x1080 pixels (1:1 aspect ratio)
- **Description**: Default square template with a subtle dark gradient background
- **Usage**: Used as the base image for Instagram posts

### default_landscape.png (1200x675)
- **Platform**: Twitter/X, Facebook, LinkedIn
- **Dimensions**: 1200x675 pixels (16:9 aspect ratio)
- **Description**: Default landscape template with a subtle dark gradient background
- **Usage**: Used as the base image for Twitter, Facebook, and LinkedIn posts

## Fonts

### fonts/OpenSans-Regular.ttf
- **Font**: Open Sans Regular
- **License**: Apache License 2.0 (open-source)
- **Source**: Google Fonts via Fontsource CDN
- **Usage**: Default font for rendering quote text on images

## Customization

You can customize these templates by:

1. **Replacing template images**: Create your own PNG files with the same dimensions and filenames
2. **Adding custom fonts**: Place TTF font files in the `fonts/` directory and update `config.yaml`
3. **Creating platform-specific templates**: Add new template files and reference them in the configuration

### Custom Template Requirements

- **Format**: PNG with transparency support
- **Dimensions**: Match the platform requirements (see above)
- **Color depth**: RGB or RGBA
- **Recommended**: Include branding elements, but leave space for text overlay

## Template Design Guidelines

When creating custom templates:

- Leave adequate space in the center for quote text (approximately 60-70% of image width)
- Ensure sufficient contrast between background and text color
- Consider text readability on mobile devices
- Include branding elements (logo, colors) in non-intrusive positions
- Test with various quote lengths (short, medium, long)

## Font Guidelines

When adding custom fonts:

- Use TTF or OTF format
- Ensure the font license allows commercial use
- Choose highly readable fonts for quote text
- Consider fonts that support Italian characters and special symbols
- Test font rendering at different sizes
