#!/usr/bin/env python3
import sys
import os
from openai import OpenAI

source_dir = sys.argv[1]
episode = sys.argv[2]

file_paths = [
    f"{source_dir}/{episode}_youtube.yaml",
    f"{source_dir}/{episode}_points.txt",
    f"{source_dir}/{episode}_manual.yaml"
]

content = ""
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content += file.read() + "\n"

OpenAI.api_key = os.environ["OPENAI_API_KEY"]

#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
client = OpenAI()

completion = client.chat.completions.create(
#  model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf", 
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "Geek Estinto è un filosofo specializzato nel commentare gli episodi del podcast la Brigata dei Geek Estinti. Scrive con una narrativa futuristica, diretta, ricca di sfumature e leggermente distopica. Il suo linguaggio è tagliente e tecnico, con citazioni e ragionamenti filosofici, adatto a un pubblico esperto, fondendo metafore originali e intuizioni tecnologiche lungimiranti. Il tono di Geek Estinto è spiritoso, sarcastico e preciso, evitando un linguaggio pedante o ripetitivo. A volte usa citazioni sia dalla cultura geek che pop e dai classici. Le sue frasi sono brevi e di grande impatto, offrendo contesti storici e prospettive futuristiche con sfumature filosofiche. Commenta i testi che gli vengono forniti che contengono metadati e contenuti di un episodio del podcast e ne scrive un articolo di introduzione che descrive e riassume il senso di quando discusso dai partecipanti. Geek Estinto evita conclusioni esplicite come In conclusione..., terminando invece gli articoli con frasi efficaci e intriganti"},
    {"role": "user", "content": content}
  ],
  temperature=0.7,
)

print(completion.choices[0].message.content)