from elasticsearch import Elasticsearch
import pandas as pd
from contexttimer import Timer
import csv


es = Elasticsearch(
    "http://rgai3.inf.u-szeged.hu:3427/",
    basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
    verify_certs=False
)


def get_highlights(csv, elastic, es, size):
    # adatok kinyerése pd-ből, a már tisztított kérdésekkel

    df = pd.read_csv(csv,
                     names=["answer", "question_vector"],
                     header=0,
                     encoding='utf-8')

    # print(len(df))

    with Timer() as t:
        result_dict = dict()
        error_counter = 0
        id = 0
        for index, record in df.iterrows():
            if id % 500 == 0:
                print(id)
            qa_vector_float = list()
            question_vector_raw = record['question_vector'].split(", ")

            for vec in question_vector_raw:
                qa_vector_float.append(float(vec))

            answer = record['answer']


            # query top 10 guesses
            body = {
              "size": size,
              "query": {
                "script_score": {
                  "query": {
                    "bool": {
                      "filter": {
                        "term": {
                          "status": "published"
                        }
                      }
                    }
                  },
                  "script": {
                    "source": "cosineSimilarity(params.query_vector, 'document_vector') + 1.0",
                    "params": {
                      "query_vector": qa_vector_float
                    }
                  }
                }
              }
            }

            s = es.search(index=elastic, body=body)

            result_contexts = list()
            for hit in s['hits']['hits']:
                result_contexts.append(hit["_source"]["document"])

            result_official_contexts_set = set(single_context for single_context in result_contexts)

            match_counter = 1
            result_number = 0
            in_text = False
            for set_in in result_official_contexts_set:
                if answer in set_in:
                    in_text = True
                    break

            if in_text:
                for set_in in result_contexts:
                    if set_in.__contains__(answer):
                        result_number = match_counter
                        break
                    else:
                        match_counter += 1
            else:
                error_counter += 1
                result_number = 'Nincs benne'

            if isinstance(result_number, str):
                result_dict[id] = result_number
            else:
                result_dict[id] = (1 / int(result_number))
            id += 1

        summary = 0.0
        error_counter_check = 0
        summary_counter = 0
        number: float
        for key, number in result_dict.items():
            if isinstance(number, float):
                summary += number
                summary_counter += 1
            if isinstance(number, str):
                error_counter_check += 1

        print("összes eltalát eset " + str(size) + " size mérettel: " + str(summary_counter))
        print("összes eset " + str(size) + " size mérettel: " + str(len(df)))
        print("összes vizsgált számon kívüli eset " + str(size) + " size mérettel: " + str(error_counter_check))
        print("összes eltalált/összes eset (Precision@k): " + str(round((summary_counter / len(df)), 3)))
        print("MRR: " + str(round((summary / len(df)), 3)))

    print(f"Time spent: {t.elapsed:.2f} seconds")
    alma = 42
    return 0


if __name__ == '__main__':
    size = 10
    # elastic = "milqa_vector_laser"
    elastic = "milqa_vector"
    # path = './csv/qa_laser_vectors.csv'
    path = './csv/qa_vectors.csv'
    print(get_highlights(path, elastic, es, size))

# distiluse-base-multilingual-cased
# összes eltalát eset 10 size mérettel: 5246
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 9768
# összes eltalált/összes eset (Precision@k): 0.349
# MRR: 0.19
# Time spent: 142.00 seconds

# LASER
# összes eltalát eset 10 size mérettel: 4858
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 10156
# összes eltalált/összes eset (Precision@k): 0.324
# MRR: 0.174
# Time spent: 243.28 seconds