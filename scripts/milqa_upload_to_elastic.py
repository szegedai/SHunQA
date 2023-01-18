from elasticsearch import Elasticsearch
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/zsozso21/soc_media/main/milqa_short_answers.csv',
                 names=['table_id', 'id', 'context', 'title', 'question', 'end', 'start', 'answer'],
                 header=1,
                 encoding='utf-8')

milqa_contexts = list()

for index, record in df.iterrows():
    # print(record['context'])
    replace = record['context'].replace("\n", "")
    milqa_contexts.append(replace)

es = Elasticsearch(
    # "https://localhost:9200",
    "http://rgai3.inf.u-szeged.hu:3427/",
    # ca_certs="/path/to/http_ca.crt",
    basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
    verify_certs=False
)

for i in range(len(milqa_contexts)):

    doc = {
        'document': milqa_contexts[i]
    }

    resp = es.index(index="milqa", id=i, document=doc)
    # print(resp['result'])
    # if i == 15:
    #     break

print("done")
