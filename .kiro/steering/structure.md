# Project Structure

## Root Configuration

- `_config.yml` - Main Jekyll configuration (site metadata, collections, navigation)
- `_config_dev.yml` - Development overrides
- `Gemfile` - Ruby dependencies
- `.prettierrc` - Code formatting rules
- `sitemap.xml` - SEO sitemap
- `robots.txt` - Search engine directives
- `CNAME` - Custom domain configuration

## Collections

### `_episodes/`
Numbered markdown files (1.md, 2.md, etc.) containing episode metadata and content.

**Required frontmatter fields:**
- `number` - Episode number (string)
- `title` - Full title with episode number
- `titolo` - Episode title without number
- `description` - Full episode description
- `duration` - Duration in seconds
- `youtube` - YouTube video ID
- `date` - Publication date (YYYY-MM-DD)
- `guests` - Array of guest names
- `host` - Host name
- `tags` - Array of topic tags
- `summary` - Array of key topics discussed
- `quote_claude`, `quote_openai`, `quote_deepseek`, `quote_llama` - AI-generated quotes
- `quote_deepseek_reasoning` - Reasoning behind DeepSeek quote
- `claude_article` - AI-generated article content

### `_geeks/`
Profile pages for podcast participants. Filename format: `[Full Name].md`

**Required frontmatter:**
- `nome` - Full name
- `episodi` - Array of episode numbers where they appeared
- `layout: geek`

## Layouts & Includes

- `_layouts/` - Page templates (home, episode, geek, tag)
- `_includes/` - Reusable components:
  - `episode_detail.html` - Episode page layout
  - `episode_list.html` - Episode listing
  - `geek_detail.html` - Geek profile
  - `geek_list.html` - Geek directory
  - `home_episodes.html`, `home_splash.html` - Homepage sections
  - `header.html`, `footer.html`, `head.html` - Page structure
  - `analytics.html`, `iubenda_*.html` - Third-party integrations

## Assets Organization

### `assets/covers/`
Episode cover images: `BGE [number].png` (e.g., `BGE 1.png`)

### `assets/texts/`
Episode-related text files with naming pattern `[number]_[type].[ext]`:
- `*_manual.yaml` - Manual metadata
- `*_article.txt` - Generated articles
- `*_claude.txt`, `*_points.txt`, `*_hashtags.txt` - AI-generated content
- `*_quote_*.txt` - Quotes from different AI models
- `*_timebolted.txt` - Timestamp data
- `*_youtube.yaml` - YouTube metadata

### `assets/fonts/`
Custom web fonts (TTF, WOFF, WOFF2)

### `assets/images/`
Site graphics (logo, banner, social icons)

### `assets/favicons/`
Favicon files in multiple formats

## Static Pages

- `index.html` - Homepage
- `episodi/index.html` - Episode archive
- `geeks/index.html` - Geek directory
- `legal/index.html` - Legal information
- `media/index.html` - Media page
- `wtf/index.html` - WTF section
- `404.html` - Error page

## Custom Plugins

`_plugins/general_tags.rb` - Generates dynamic tag pages at `/tags/[tag]/`

## Naming Conventions

- Episodes: Numbered sequentially (1, 2, 3...)
- Geeks: Full name with proper capitalization
- Assets: Lowercase with underscores or spaces depending on type
- URLs: SEO-friendly permalinks (`/ep/[title]/`, `/geek/[name]/`)

## Kiro summaries
All the summaries genertaed by kiro MUST be placed under the .kiro/summaries directory, with information about date and related tasks