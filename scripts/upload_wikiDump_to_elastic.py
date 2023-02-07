from elasticsearch import Elasticsearch
import pandas as pd

# wiki subcategories from root (domain) category https://petscan.wmflabs.org/
df = pd.read_csv('/home/gszabo/PycharmProjects/elasticsearch-8.5.2-linux-x86_64/source_xml/text/relevant_wikidump.csv',
                 names=['id', 'context'],
                 encoding='utf-8')


wikidump_contexts_set = set()

for index, record in df.iterrows():
    replace = record['context']
    wikidump_contexts_set.add(replace)

wikidump_contexts = list(wikidump_contexts_set)


es = Elasticsearch(
    "http://rgai3.inf.u-szeged.hu:3427/",
    basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
    verify_certs=False
)


for i in range(len(wikidump_contexts)):

    doc = {
        'document': wikidump_contexts[i],
    }

    resp = es.index(index="word_war_2_wikidump", id=str(i), document=doc)
    # print(resp['result'])
    # if i == 15:
    #     break

print("done")
