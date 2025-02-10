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
    {"role": "system", "content": "Sei un arguto osservatore del mondo, un poeta moderno, profondo, essenziale e un po' punk. Devi scrivere una brevissima citazione inventata, sulla base del testo fornito. Qualcosa di memorabile ed ad effetto, non inventarti l'autore, scrivi solo il testo della citazione, senza commentarla."},
    {"role": "user", "content": content},
]


# Local Inference lmstudio
# base_url = "http://localhost:1234/v1"
# api_key = "lm-studio"
# model = "unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF"

# Local Inference Ollama
base_url = "http://localhost:11434/v1"
api_key = os.environ['HUGGINGFACE_API_KEY']
model = "deepseek-r1:latest"

# Nvidia Build Inference
#base_url = "https://integrate.api.nvidia.com/v1"
#api_key = os.environ['NVIDIA_API_KEY']
#model = "deepseek-ai/DeepSeek-R1"

# HuggingFace Inference
#base_url = "https://huggingface.co/api/inference-proxy/together"
#api_key = os.environ['HUGGINGFACE_API_KEY']
#model = "deepseek-ai/DeepSeek-R1"

client = OpenAI(
  	base_url=base_url,
    api_key=api_key,
)




completion = client.chat.completions.create(
  model=model,
  messages=messages,
  temperature=0.6,
  top_p=0.7,
  max_tokens=4096,
)

content = completion.choices[0].message.content
print(content)

#for chunk in completion:
#  if chunk.choices[0].delta.content is not None:
#    print(chunk.choices[0].delta.content, end="")