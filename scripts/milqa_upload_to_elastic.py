from elasticsearch import Elasticsearch
import pandas as pd
import os

# df = pd.read_csv('https://raw.githubusercontent.com/zsozso21/soc_media/main/milqa_short_answers.csv',
#                  names=['table_id', 'id', 'context', 'title', 'question', 'end', 'start', 'answer'],
#                  header=1,
#                  encoding='utf-8')

df = pd.read_csv('/home/gszabo/PycharmProjects/elasticsearch-8.5.2-linux-x86_64/scripts/my_file.csv',
                 names=['question', 'context'],
                 header=1,
                 encoding='utf-8')


milqa_contexts_set = set()

for index, record in df.iterrows():
    replace = record['context']
    milqa_contexts_set.add(replace)

milqa_contexts = list(milqa_contexts_set)


es = Elasticsearch(
    "http://rgai3.inf.u-szeged.hu:3427/",
    basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
    verify_certs=False
)


for i in range(len(milqa_contexts)):

    doc = {
        'document': milqa_contexts[i].split("|||")[0],
        'official_document': milqa_contexts[i].split("|||")[1]
    }

    resp = es.index(index="milqa_w_lemma_w_official_context", id=str(i), document=doc)
    # print(resp['result'])
    # if i == 15:
    #     break

print("done")
