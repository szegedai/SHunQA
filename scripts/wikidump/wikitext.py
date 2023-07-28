# This script is used to extract the raw text from the wikitext file and store it in elasticsearch

from elasticsearch import Elasticsearch
import mwparserfromhell

with open("../data.txt", "r") as f:
    file = f.readlines()

counter = 0
raw_text_list = list()
raw_text = ""

for line in file:
    if line.startswith("-----"):
        counter += 1
    if counter == 1:
        if line.startswith("----"):
            continue
        raw_text += line
    if counter == 2:
        counter = 1
        raw_text_list.append(raw_text)
        raw_text = ""

wikicode = mwparserfromhell.parse(raw_text_list[4])
print(wikicode.strip_code())

textfield = wikicode.strip_code()

textfield_list = textfield.split("\n")

textfield_wo_ws = ""

for line in textfield_list:
    if line.startswith(" "):
        textfield_wo_ws += line.lstrip() + "\n"
        continue
    if len(line) == 0:
        continue
    textfield_wo_ws += line + "\n"

es = Elasticsearch( # usual auth is needed here
    "https://localhost:9200",
    ca_certs="/path/to/http_ca.crt",
    basic_auth=("elastic", "facebook"),
    verify_certs=False
)

doc = {
    'field1': textfield_wo_ws
}
resp = es.index(index="test", id=2, document=doc)
print(resp['result'])


