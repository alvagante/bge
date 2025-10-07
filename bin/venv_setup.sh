#!/bin/bash
python -m venv .venv
source .venv/bin/activate

pip install pipx
pip install openai vosk yt-dlp pyyaml frontmatter anthropic
pipx install unsilence

brew install ffmpeg