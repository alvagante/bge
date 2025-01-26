#!/usr/bin/env python3
import sys
import os
import re
import yaml
from frontmatter import Frontmatter

if len(sys.argv) < 3:
    print("Please provide the source dir as first argument and the destination dir as second")
    sys.exit(1)

src_dir = sys.argv[1]
dest_dir = sys.argv[2]

files = os.listdir(src_dir)

guests = []
for file in files:
    if file.endswith("_manual.yaml"):
        with open(os.path.join(src_dir, file)) as f:
            manual_data = yaml.safe_load(f)
            for guest in manual_data["guests"]:
                if guest not in guests:
                    guests.append(guest)

for guest in guests:
    guest_file = os.path.join(dest_dir, guest + ".md")

    if os.path.exists(guest_file):
        frontmatter_data = Frontmatter.read_file(guest_file)
    else:
        frontmatter_data = {}

#    print(frontmatter_data['attributes'])
#    print(frontmatter_data['body'])
#    print(guest_file)

    existing_data = frontmatter_data['attributes'] if 'attributes' in frontmatter_data else {}
#    existing_data['nome'] = existing_data.get('nome', guest)
#    existing_data['layout'] = existing_data.get('layout', 'geek')
    
    current_episodes = existing_data.get('episodi', [])
    for file in files:
        if file.endswith("_manual.yaml"):
            with open(os.path.join(src_dir, file)) as f2:
                manual_data = yaml.safe_load(f2)
                if guest in manual_data["guests"]:
                    episode_number = int(re.search(r'(\d+)_manual.yaml', file).group(1))
                    if episode_number not in current_episodes:
                        current_episodes.append(episode_number)
    existing_data['episodi'] = sorted(list(current_episodes))

    with open(guest_file, "w") as f:
        f.write('---\n')
        yaml.dump(existing_data, f, default_flow_style=False)
        f.write('---\n')
        f.write(frontmatter_data['body'])

print(f"Guest files created in {dest_dir}")
