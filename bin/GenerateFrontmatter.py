#!/usr/bin/env python3
import sys
import os
import re
import yaml
from datetime import date

if len(sys.argv) < 3:
    print("Please provide a number as first argument and the destination dir as second")
    sys.exit(1)

file_number = sys.argv[1]
dest_dir = sys.argv[2]


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


# Read the YAML file

youtube_file = file_number + "_youtube.yaml"
if not os.path.isfile(youtube_file):
    print(f"Note: File {youtube_file} does not exist.")
    youtube_data = {}
else:
    with open(youtube_file) as f:
        youtube_data = yaml.safe_load(f)

manual_file = file_number + "_manual.yaml"
if not os.path.isfile(manual_file):
    print(f"Note: File {manual_file} does not exist.")
    manual_data = {}
else:
    with open(manual_file) as f:
        manual_data = yaml.safe_load(f)

summary_file = file_number + "_points.txt"
if not os.path.isfile(summary_file):
    print(f"Note: File {summary_file} does not exist.")
    summary_data = []
else:
    with open(summary_file, 'r') as file:
        summary_data = [line.lstrip('- ').strip() for line in file]

# Create keys_list dictionary
keys_list = {
    'number': number,
    'layout': 'episode',
    'titolo': re.sub(r'BGE \d+ - ', '', youtube_data.get('title', 'NA')),
    'description': youtube_data.get('description', 'NA'),
    'duration': youtube_data.get('duration', 'NA'),
    'youtube': youtube_data.get('youtube_id', 'NA'),
    'tags': [tag.strip() for tag in read_file(file_number + "_hashtags.txt").split("#") if tag.strip()],
    'date': youtube_data.get('date', '1970-06-06'),
    'summary': summary_data,
    'guests': manual_data.get('guests', 'NA'),
    'host': manual_data.get('host', 'Alessandro Franceschi'),
    'links': manual_data.get('links', 'NA'),
    'quote': read_file(file_number + "_quote.txt"),
    'claude_article': read_file(file_number + "_claude.txt"),
}

# Debugging
#print(keys_list)
#print(youtube_data)
#print(manual_data)

article_content = read_file(file_number + "_article.txt")
output_file = f"{dest_dir}/{number}.md"

with open(output_file, 'w') as outfile:
    outfile.write("---\n")
    yaml.dump(keys_list, outfile, default_flow_style=False, sort_keys=False)
    outfile.write("---\n")
    outfile.write(article_content)

