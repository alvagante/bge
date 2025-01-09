#!/usr/bin/env python3

import os
import requests
import sys
import json
prompt_source = sys.argv[1]
filename = sys.argv[2]

def generate_midjourney_image(prompt_file):
    # Read prompt from file
    with open(prompt_file, 'r') as file:
        prompt = file.read().strip()

    # Get API key from environment variable
    api_key = os.getenv('MINAI_API_KEY')
    if not api_key:
        raise ValueError("MINAI_API_KEY environment variable not set")

    # API endpoint
      url = "https://api.1min.ai/api/features"

    # Prepare headers and payload
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
    "type": "IMAGE_GENERATOR",
    "model": "midjourney_6_1",
    "promptObject": {
        "imageUrl": "development/images/2024_09_30_13_41_50_758_2023_11_10_16_27_12_416_208054.png", // Absolute URL OR "asset.key" of Asset API
        "mode": "fast",
        "n": 4,
        "isNiji6": false,
        "aspect_width": 1,
        "aspect_height": 1,
        "maintainModeration": true
    }

        'prompt': prompt,
        'version': 'v6'  # You can adjust the Midjourney version as needed
    }

    try:
        # Send request to 1MinAI API
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract image URL
        image_url = result.get('image_url')
        if not image_url:
            raise ValueError("No image URL found in the response")
        
        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Save the image
        with open(filename, 'wb') as f:
            f.write(image_response.content)
        
        print(f"Image successfully downloaded: {filename}")
        return filename

    except requests.exceptions.RequestException as e:
        print(f"Error generating or downloading image: {e}")
        return None

def main():
    # Path to the prompt file
    prompt_file = prompt_source
    
    # Generate and download image
    generate_midjourney_image(prompt_file)

if __name__ == "__main__":
    main()
