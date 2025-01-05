#!/usr/bin/env python3
import sys
import os
import re
import yaml

# Python script that gets the list of Guests from for guest key in the *_manual.yaml
# files in the directory passed as first argument, and creates, ofr each guest
# a file named <guest>.md in the directory passed as second argument.
# The file contains the following information:
# name: the guest name
# episodes: the list of episodes in which the guest appears (based the *_manual.yaml files)
# where * is the episode number

if len(sys.argv) < 3:
    print("Please provide the source dir as first argument and the destination dir as second")
    sys.exit(1)

src_dir = sys.argv[1]
dest_dir = sys.argv[2]

# Get the list of files in the source directory
files = os.listdir(src_dir)

# Get the list of guests
guests = []
for file in files:
    if file.endswith("_manual.yaml"):
        with open(os.path.join(src_dir, file)) as f:
            manual_data = yaml.safe_load(f)
            for guest in manual_data["guests"]:
                if guest not in guests:
                    guests.append(guest)

# Create the guest files
for guest in guests:
    guest_file = os.path.join(dest_dir, guest + ".md")
    with open(guest_file, "w") as f:
        f.write(f"---\n")
        f.write(f"nome: {guest}\n")
        f.write(f"layout: 'geek'\n")
        f.write("episodi:\n")
        for file in files:
            if file.endswith("_manual.yaml"):
                with open(os.path.join(src_dir, file)) as f2:
                    manual_data = yaml.safe_load(f2)
                    if guest in manual_data["guests"]:
                        episode_number = re.search(r'(\d+)_manual.yaml', file).group(1)
                        f.write(f"  - {episode_number}\n")
        f.write(f"---\n")

print(f"Guest files created in {dest_dir}")
