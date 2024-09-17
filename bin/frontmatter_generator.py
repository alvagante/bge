#!/usr/bin/env python3
import sys
import os
import re
from datetime import date

# Ensure a number was passed as an argument
if len(sys.argv) < 2:
  print("Please provide a number as an argument.")
  sys.exit(1)

# Get file name from the command line argument
file_number = sys.argv[1]

# Get the number from the end of file name
# Take the last digits of the file name
# Use regex replace to remove the last digits
number = os.path.basename(file_number)

def read_file(file):
  # Check if the file exists
  if not os.path.isfile(file):
    print(f"Error: The file {file} does not exist.")
    return "Nofile"
  else:
    try:
      with open(file, 'r') as src_file:
        content = src_file.read()
        # Check if the file is empty
        if content == "":
          print(f"Error: The file {file} is empty.")
          return "Nocontent"
        else:
          return content
    except Exception as e:
      print(f"Error: An error occurred while reading the file {file}: {e}")
      return None

#title: "Episode 1: The Geek Awakens"
#date: 2024-01-01
#description: "In this episode, we discuss the resurgence of retro gaming."
#audio: "https://example.com/episode1.mp3"
#duration: "35:20"
#tags: ["retro gaming", "geek culture"]
# Define the source files and the output file
keys_list = {
  'number': number, 
  'layout': read_file(file_number + "_layout.txt"),
  'title': read_file(file_number + "_title.txt"),
  'date': '6000',
  'host': 'Alessandro Franceschi',
#  'description': read_file(file_number + "_points.txt"),
  'file': 'https://example.com/episode{file_number}.mp3',
  'duration': '6000',
  'guests': read_file(file_number + "_speakers.txt"),
  'youtube_id': "YouTubeVideoID1",
  'tags': read_file(file_number + "_hashtags.txt").split("#"),
#  'summary': read_file(file_number + "_points.txt"),
}
article_content = read_file(file_number + "_article.txt")
output_file = f"{file_number}.md"

# Read the content of the source files and write to the output file
with open(output_file, 'w') as file:
  file.write("---\n")
  for key, content in keys_list.items():
    # Format content based of data type:
    # When ia one line string put write key: value
    if isinstance(content, str):
      content = content.strip()
      if content.__sizeof__() > 80:
        file.write(f"{key}: |\n")
        file.write(f"  {content}\n")      
      else:
        file.write(f"{key}: '{content}'\n")
    # When list, build an array of strings and write to file
    elif isinstance(content, list):
      file.write(f"{key}:\n")
      for item in content:
        file.write(f"  - {item}\n")
    else:
      file.write(f"{key}: |\n")
      file.write(f"{content}\n")
  file.write("---\n")
  file.write(f"{article_content}\n")
  file.write("...\n")

print(f"Frontmatter file {output_file} has been generated.")

