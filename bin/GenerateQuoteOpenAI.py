#!/usr/bin/env python3
import sys
import os
from openai import OpenAI

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

OpenAI.api_key = os.environ["OPENAI_API_KEY"]

#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
client = OpenAI()

completion = client.chat.completions.create(
#  model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf", 
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "Sei un arguto osservatore del mondo, un poeta moderno, profondo, essenziale e un po' punk. Devi scrive una brevissima citazione inventata, sulla base del testo fornito. Qualcosa di memorabile ed ad effetto, non inventarti l'autore, scrivi solo la citazione, senza commentarla."},
    {"role": "user", "content": content}
  ],
  temperature=0.7,
)

print(completion.choices[0].message.content)