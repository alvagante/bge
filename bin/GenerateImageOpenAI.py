#!/usr/bin/env python3
import sys
import os
import requests
from openai import OpenAI

source_dir = sys.argv[1]
episode = sys.argv[2]

file_paths = [
    f"{source_dir}/{episode}_quote.txt",
]

content = ""
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content += file.read() + "\n"
content = content.strip('"\'')

OpenAI.api_key = os.environ["OPENAI_API_KEY"]

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt=content,
    size="1024x1024",
    style="vivid",
    quality="hd",
    n=1,
)

image_url = response.data[0].url

# Download the image and save it to the specified path
image_response = requests.get(image_url)
if image_response.status_code == 200:
    image_path = f"{source_dir}/{episode}_dall-e.png"
    with open(image_path, 'wb') as image_file:
        image_file.write(image_response.content)
    print(f"Image saved to {image_path}")
else:
    print("Failed to download the image")