from elasticsearch import Elasticsearch
import pandas as pd
from contexttimer import Timer

es = Elasticsearch(
    "http://rgai3.inf.u-szeged.hu:3427/",
    basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
    verify_certs=False
)


def get_highlights(csv, es, size):
    # adatok kinyerése pd-ből, a már tisztított kérdésekkel

    df = pd.read_csv(csv,
                     names=['question', 'context'],
                     header=1,
                     encoding='utf-8')

    milqa_contexts_dict = dict()

    for index, record in df.iterrows():
        clean_question = record['question']
        context = record['context']

        if clean_question not in milqa_contexts_dict:
            milqa_contexts_dict[clean_question] = context
        else:
            pass

    with Timer() as t:
        result_dict = dict()
        error_counter = 0
        id = 0
        match_len = 0
        all_context = list()
        all_question = list()
        for key, value in milqa_contexts_dict.items():
            question = key
            official_context = value.split("|||")[1]

            # query top 10 guesses
            body = {
                "size": size,
                "query": {
                    "match": {
                        "document": question
                    }
                }
            }
            s = es.search(index='milqa_w_lemma_w_official_context', body=body)

            result_contexts = list()
            result_official_contexts = list()
            for hit in s['hits']['hits']:
                result_contexts.append(hit["_source"]["document"])
                result_official_contexts.append(hit["_source"]["official_document"])

            # error_dict = dict()
            result_official_contexts_set = set(single_context for single_context in result_official_contexts)
            if official_context in result_official_contexts_set:
                match_counter = 1
                result_number = 0
                for result_official_context in result_official_contexts:
                    if result_official_context == official_context:
                        result_number = match_counter
                        break
                    else:
                        match_counter += 1
                match_len += 1
                all_context.append(value)
                all_question.append(key)
            else:
                error_counter += 1
                result_number = 'Nincs benne'
                all_context.append(value)
                all_question.append(key)

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
        print("összes eset " + str(size) + " size mérettel: " + str(len(milqa_contexts_dict)))
        print("összes vizsgált számon kívüli eset " + str(size) + " size mérettel: " + str(error_counter_check))
        print("összes eltalált/összes eset (Precision@k): " + str(summary_counter / len(milqa_contexts_dict)))

        print("MRR: " + str(summary / len(milqa_contexts_dict)) + " | error counter: " + str(
            error_counter))  # + "\n" + str(result_dict))# + "\n" + all_context[2] + "\n" + all_question[2])

    print(f"Time spent: {t.elapsed:.2f} seconds")

    return 0


if __name__ == '__main__':
    csv = 'q_wPoS_wLemma_c_wLemma_c_wOfficial.csv'
    # csv = 'q_wLemma_c_wLemma_c_wOfficial.csv'
    print(get_highlights(csv, es, 300))

# posLemma: 12769 lemma: 12845

# 1 pos lemma:
# összes eltalát eset 1 size mérettel: 8393
# összes eset 1 size mérettel: 12769
# összes vizsgált számon kívüli eset 1 size mérettel: 4376
# összes eltalált/összes eset (Precision@k): 0.657295011355627
# MRR: 0.657295011355627 | error counter: 4376
# Time spent: 75.06 seconds
#
# 300 pos lemma:
# összes eltalát eset 300 size mérettel: 12559
# összes eset 300 size mérettel: 12769
# összes vizsgált számon kívüli eset 300 size mérettel: 210
# összes eltalált/összes eset (Precision@k): 0.9835539196491503
# MRR: 0.7494510958150116 | error counter: 210
# Time spent: 480.42 seconds
#
# 300 lemma:
# összes eltalát eset 300 size mérettel: 12638
# összes eset 300 size mérettel: 12845
# összes vizsgált számon kívüli eset 300 size mérettel: 207
# összes eltalált/összes eset (Precision@k): 0.9838847800700662
# MRR: 0.7403596956400766 | error counter: 207
# Time spent: 599.05 seconds
#
# 1 lemma
# összes eltalát eset 1 size mérettel: 8315
# összes eset 1 size mérettel: 12845
# összes vizsgált számon kívüli eset 1 size mérettel: 4530
# összes eltalált/összes eset (Precision@k): 0.64733359283768
# MRR: 0.64733359283768 | error counter: 4530
# Time spent: 80.92 seconds