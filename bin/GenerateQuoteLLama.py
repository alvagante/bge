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

messages = [
    # "detailed thinking off" keeps the NVIDIA Nemotron models from emitting a
    # <think> reasoning block; harmless for the plain Meta Llama models.
    {"role": "system", "content": "detailed thinking off"},
    {"role": "system", "content": "Sei un arguto osservatore del mondo, un poeta moderno, profondo, essenziale e un po' punk. Devi scrive una brevissima citazione inventata, sulla base del testo fornito. Qualcosa di memorabile ed ad effetto, non inventarti l'autore, scrivi solo la citazione, senza commentarla."},
    {"role": "user", "content": content},
]


# Local Inference
# base_url = "http://localhost:1234/v1"
# api_key = "lm-studio"
# model = "unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF"

# Ollama Cloud inference (OpenAI-compatible endpoint).
# Auth: set OLLAMA_API_KEY to a key from https://ollama.com/settings/keys
# Cloud model tags carry a "-cloud" suffix; catalog: https://ollama.com/search?c=cloud
# Ollama Cloud does not host a Meta Llama model, so the primary is gpt-oss:120b
# with Llama-derived Nemotron tags as fallbacks. The list is tried in order and
# the next entry is used when one is retired (404/410).
base_url = "https://ollama.com/v1"
api_key = os.environ['OLLAMA_API_KEY']
models = [
    "gpt-oss:120b-cloud",
    "gpt-oss:20b-cloud",
    "nemotron-3-super:cloud",
]
client = OpenAI(
  	base_url=base_url,
    api_key=api_key,
)

completion = None
for model in models:
    try:
        completion = client.chat.completions.create(
          model=model,
          messages=messages,
          temperature=0.6,
          top_p=0.7,
          max_tokens=4096,
          stream=True
        )
        break
    except Exception as err:
        status = getattr(err, "status_code", None)
        if status in (404, 410):
            print(f"Model {model} unavailable ({status}), trying next", file=sys.stderr)
            continue
        raise

if completion is None:
    raise SystemExit("No available model on Ollama Cloud")

#content = completion.choices[0].message.content
#print(content)

buffer = ""
seen_think_close = False
for chunk in completion:
  # Some providers emit terminal/usage stream events with no choices.
  choices = getattr(chunk, "choices", None) or []
  if len(choices) == 0:
    continue

  delta = getattr(choices[0], "delta", None)
  if delta is None:
    continue

  text = getattr(delta, "content", None)
  if text is None:
    continue

  # If a reasoning model still slips in a <think>...</think> block, drop
  # everything up to and including the closing tag.
  if not seen_think_close:
    buffer += text
    if "</think>" in buffer:
      seen_think_close = True
      print(buffer.split("</think>", 1)[1].lstrip(), end="")
    continue

  print(text, end="")

# No </think> was ever seen: the whole stream was the answer.
if not seen_think_close:
  print(buffer, end="")