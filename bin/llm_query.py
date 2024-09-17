#!/usr/bin/env python3
import sys
from openai import OpenAI

filename = sys.argv[1]

# Read the input text from the file passed as argument
with open(filename, 'r') as file:
    content = file.read()

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

completion = client.chat.completions.create(
  model="local-model", # this field is currently unused
  messages=[
    {"role": "system", "content": "Analizza il testo fornito e fanne un riassunto in italiano. Il riassunto deve essere diviso in 10 punti, che in pochissime parole (meno di 50 per ogni punto) riassumono i concetti più importanti del testo fornito. La risposta deve essere in italiano."},
    {"role": "user", "content": f"#{content}"}
  ],
  temperature=0.7,
)

print(completion.choices[0].message.content)