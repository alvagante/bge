# BGE Social Quote Generator

Automated Python tool that generates visually appealing images from BGE (Brigata dei Geek Estinti) episode quotes and publishes them to social media platforms.

## Features

- Extract quotes from BGE episode files (supports multiple AI sources: Claude, OpenAI, DeepSeek, Llama)
- Generate branded quote images for different social media platforms
- Automated publishing to Twitter, Instagram, Facebook, and LinkedIn
- Configurable templates, fonts, and branding
- Dry-run mode for testing without publishing
- Comprehensive error handling and logging

## Requirements

- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd social-quote-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Quick Start

1. Copy the example configuration:
```bash
cp config/config.example.yaml config/config.yaml
```

2. Set up your API credentials in a `.env` file:
```bash
cp .env.example .env
# Edit .env with your actual API credentials
```

3. Run a test generation (dry-run mode):
```bash
python src/main.py --episode 1 --dry-run
```

## Project Structure

```
social-quote-generator/
├── src/                    # Source code
│   ├── extractors/        # Quote extraction modules
│   ├── generators/        # Image generation modules
│   ├── publishers/        # Social media publishing modules
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── templates/             # Image templates and fonts
├── output/                # Generated images and logs
│   ├── images/
│   └── logs/
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
└── README.md             # This file
```

## Usage

See the full documentation for detailed usage instructions and examples.

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src/ tests/
```

Lint code:
```bash
flake8 src/ tests/
```

## Security

**Important**: Never commit API credentials or `.env` files to version control. The `.gitignore` file is configured to exclude these files, but always verify before committing.

### Best Practices:
- Store all API keys and secrets in the `.env` file
- Use environment-specific `.env` files for different deployments
- Rotate credentials regularly
- Use read-only or limited-scope API tokens when possible
- **Instagram Warning**: Instagram requires username/password authentication, which is less secure than OAuth. Consider:
  - Using a dedicated account with limited permissions
  - Enabling 2FA and handling it appropriately
  - Being aware of Instagram's rate limits and terms of service

### Path Security:
- All configured paths are validated to prevent directory traversal attacks
- Absolute paths and `..` patterns are not allowed in configuration

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
