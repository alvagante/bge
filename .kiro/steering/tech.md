# Technology Stack

## Static Site Generator

**Jekyll 4.3.4** - Ruby-based static site generator

## Dependencies

- **jekyll-feed** - RSS feed generation
- **jekyll-seo-tag** - SEO metadata
- **minima** theme (base)

## Build & Development Commands

```bash
# Install dependencies
bundle install

# Run local development server
bundle exec jekyll serve

# Build for production
bundle exec jekyll build

# Development with draft config
bundle exec jekyll serve --config _config.yml,_config_dev.yml
```

## Custom Plugins

- `_plugins/general_tags.rb` - Generates tag pages dynamically

## Frontend

- **Bootstrap** - CSS framework (responsive grid, components)
- **Custom CSS** - `css/bge.css` with custom fonts and styling
- **YouTube iframe embeds** - Video player integration

## Custom Fonts

- Peace Sans (headings)
- Kanit (body text)
- Caveat (blockquotes)
- IndieFlower
- OpenDyslexic (accessibility)

## Deployment

Static site hosted on GitHub Pages (based on CNAME file presence).

## Content Format

- Episodes: Markdown files in `_episodes/` with YAML frontmatter
- Geeks: Markdown files in `_geeks/` with YAML frontmatter
- Assets: Organized in `assets/` (covers, fonts, images, texts)
