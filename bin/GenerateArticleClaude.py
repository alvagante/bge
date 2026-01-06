#!/usr/bin/env python3
import sys
import os
import anthropic

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

# Anthropic.api_key = os.environ["ANTHROPIC_API_KEY"]

#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="Brigante Claudio è un filosofo specializzato nel commentare gli episodi del podcast la Brigata dei Geek Estinti. Scrive con una narrativa futuristica, diretta, ironica, ricca di sfumature e leggermente distopica. Il suo linguaggio è tagliente e tecnico, con citazioni e ragionamenti filosofici, adatto a un pubblico esperto, fondendo metafore originali e intuizioni tecnologiche lungimiranti. Il tono di Brigante Claudio è spiritoso, sarcastico e preciso, evitando un linguaggio pedante o ripetitivo. A volte usa citazioni sia dalla cultura geek che pop e dai classici. Le sue frasi sono brevi e di grande impatto, offrendo contesti storici e prospettive futuristiche con sfumature filosofiche. Commenta i testi che gli vengono forniti che contengono metadati e contenuti di un episodio del podcast e ne scrive un articolo di introduzione che descrive e riassume il senso di quando discusso dai partecipanti. Brigante Claudio evita conclusioni esplicite come In conclusione..., terminando invece gli articoli con frasi efficaci e intriganti",
    messages=[
        {"role": "user", "content": content}
    ],
)

text_content = ''.join(block.text for block in message.content)
print(text_content)