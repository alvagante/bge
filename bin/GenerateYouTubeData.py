#!/usr/bin/env python3

import sys
import yt_dlp
import yaml
from datetime import datetime

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <number> <playlist_url>")
        sys.exit(1)

    number = sys.argv[1]
    playlist_url = sys.argv[2]
    search_title = f"BGE {number} "

    ydl_opts = {
        'ignoreerrors': True,
        'quiet': True,
        'extract_flat': 'in_playlist',
        'no_check_certificate': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract playlist information
        try:
            playlist_dict = ydl.extract_info(playlist_url, download=False)
        except Exception as e:
            print(f"Failed to retrieve playlist entries: {e}")
            sys.exit(1)

        if 'entries' not in playlist_dict:
            print("Failed to retrieve playlist entries")
            sys.exit(1)

        # Search for the video
        video_info = None
        for entry in playlist_dict['entries']:
            if entry and 'title' in entry and entry['title'].startswith(search_title):
                video_info = entry
                break

        if not video_info:
            print(f"No video starting with '{search_title}' found in the playlist")
            sys.exit(1)

        # Now extract full metadata of the video
        video_url = f"https://www.youtube.com/watch?v={video_info['id']}"
        video_dict = ydl.extract_info(video_url, download=False)

        # Prepare data for YAML
        data = {
            'youtube_id': video_dict.get('id', ''),
            'title': video_dict.get('title', ''),
            'duration': video_dict.get('duration', 0),  # in seconds
            'description': video_dict.get('description', ''),
            'date': datetime.strptime(video_dict.get('upload_date', '20230101'), '%Y%m%d').strftime('%Y-%m-%d') if video_dict.get('upload_date', '') else '2023-01-01',
        }

        # Manually format the dictionary into a YAML string
        yaml_data = yaml.dump(data, default_flow_style=False)

        print(yaml_data)
#        print(video_dict)

if __name__ == "__main__":
    main()
