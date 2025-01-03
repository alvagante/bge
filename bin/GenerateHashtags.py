#!/usr/bin/env python3
import sys
import os
from openai import OpenAI

filename = sys.argv[1]

OpenAI.api_key = os.environ["OPENAI_API_KEY"]

# Read the input text from the file passed as argument
with open(filename, 'r') as file:
    content = file.read()

#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
client = OpenAI()

completion = client.chat.completions.create(
#  model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf", 
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "Fai un elenco di hashtag, separati da uno spazio, basati sul testo fornito"},
    {"role": "user", "content": content}
  ],
  temperature=0.7,
)

print(completion.choices[0].message.content)