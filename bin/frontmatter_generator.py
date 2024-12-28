#!/usr/bin/env python3
import sys
import os
import re
from datetime import date

# Ensure a number was passed as an argument
if len(sys.argv) < 2:
    print("Please provide a number as an argument.")
    sys.exit(1)

# Get file number from the command line argument
file_number = sys.argv[1]

# Get the number from the end of file name
number = os.path.basename(file_number)

def read_file(file):
    # Check if the file exists
    if not os.path.isfile(file):
        print(f"Error: The file {file} does not exist.")
        return "NA"
    else:
        try:
            with open(file, 'r') as src_file:
                content = src_file.read()
                # Check if the file is empty
                if content == "":
                    print(f"Error: The file {file} is empty.")
                    return "NA"
                else:
                    return content
        except Exception as e:
            print(f"Error: An error occurred while reading the file {file}: {e}")
            return None

def parse_yaml(yaml_content):
    # Manually parse the YAML content into a dictionary
    data = {}
    lines = yaml_content.split('\n')
    for line in lines:
        if line.strip() and ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data

# Read the YAML file

yaml_content = read_file(file_number + "_youtube.yaml")
if yaml_content == "NA":
    yaml_data = {}
else:
    yaml_data = parse_yaml(yaml_content)

# Create keys_list dictionary
keys_list = {
    'number': number,
    'layout': 'episode',
    'title': yaml_data.get('title', 'NA'), 
    'date': yaml_data.get('date', 'NA'), 
    'description': yaml_data.get('description', 'NA'),
    'duration': yaml_data.get('duration', 'NA'),
    'youtube_id': yaml_data.get('youtube_id', 'NA'),
    'tags': [tag for tag in read_file(file_number + "_hashtags.txt").split("#") if tag],
    'summary': read_file(file_number + "_points.txt"),
}

# Add parsed YAML data to keys_list
# keys_list.update(yaml_data)

# Print keys_list for debugging
# print(keys_list)

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
      if content.__sizeof__() > 160:
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

