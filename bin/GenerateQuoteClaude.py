#!/usr/bin/env python3
import sys
import os
import anthropic

source_dir = sys.argv[1]
episode = sys.argv[2]

file_paths = [
    f"{source_dir}/{episode}_youtube.yaml",
    f"{source_dir}/{episode}_points.txt",
    f"{source_dir}/{episode}_manual.yaml"
]

content = ""
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content += file.read() + "\n"

# Anthropic.api_key = os.environ["ANTHROPIC_API_KEY"]

#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="Sei un arguto osservatore del mondo, un poeta moderno, profondo, essenziale e un po' punk. Devi scrive una brevissima citazione inventata, sulla base del testo fornito. Qualcosa di memorabile ed ad effetto, non inventarti l'autore, scrivi solo la citazione, senza commentarla.",
    messages=[
        {"role": "user", "content": content}
    ],
)

text_content = ''.join(block.text for block in message.content)
print(text_content)