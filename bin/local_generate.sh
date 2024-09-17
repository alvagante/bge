#!/bin/bash

echo "Removing /Users/al/OneDrive/BGE/Episodes/*.md" 
rm  /Users/al/OneDrive/BGE/Episodes/*.md
echo
echo "Generating /Users/al/OneDrive/BGE/Episodes/*.md"
/Users/al/OneDrive/GITHUB/bge.github.io/bin/GenerateFrontmatters.sh /Users/al/OneDrive/BGE/Episodes
echo
echo "Copying /Users/al/OneDrive/BGE/Episodes/*.md to /Users/al/OneDrive/GITHUB/brigata-geek-estinti/content/episodes/"
cp -a /Users/al/OneDrive/BGE/Episodes/*.md /Users/al/OneDrive/GITHUB/brigata-geek-estinti/content/episodes/
