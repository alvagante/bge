#!/usr/bin/env python3
# pip install google-api-python-client
import re
import sys
from googleapiclient.discovery import build

# Ensure a regular expression and playlist ID were passed as arguments
if len(sys.argv) < 3:
    print("Please provide a regular expression and a playlist ID as arguments.")
    sys.exit(1)

regexp = sys.argv[1]
playlist_id = sys.argv[2]

# Build the YouTube service
# Replace 'YOUR_API_KEY' with your actual YouTube Data API key. You can get this key from the Google Cloud Console.
youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')

# Fetch the playlist items
request = youtube.playlistItems().list(
    part='snippet',
    maxResults=50,
    playlistId=playlist_id
)
response = request.execute()

# Search for a video with a title matching the regular expression
for item in response['items']:
    title = item['snippet']['title']
    if re.search(regexp, title):
        print(f"Video ID: {item['snippet']['resourceId']['videoId']}")
        break
else:
    print("No matching video found.")