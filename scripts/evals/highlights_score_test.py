from elasticsearch import Elasticsearch
import pandas as pd
from contexttimer import Timer

df = pd.read_csv('https://raw.githubusercontent.com/zsozso21/soc_media/main/milqa_short_answers.csv',
                 names=['table_id', 'id', 'context', 'title', 'question', 'end', 'start', 'answer'],
                 header=1,
                 encoding='utf-8')

milqa_contexts_dict = dict()

counter = 0
for index, record in df.iterrows():
    replace_context = record['context']#.replace("\n", " ")
    question = record['question']
    if question not in milqa_contexts_dict:
        milqa_contexts_dict[question] = replace_context
    else:
        pass
    # if counter == 100:
    #     break
    # counter += 1

es = Elasticsearch(
    "http://rgai3.inf.u-szeged.hu:3427/",
    basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
    verify_certs=False
)

def get_highlights(es, size):
    with Timer() as t:
        result_dict = dict()
        error_counter = 0
        id = 0
        match_len = 0
        all_context = list()
        all_question = list()
        for key, value in milqa_contexts_dict.items():
            question = key
            context = value

            # query top 10 guesses
            body = {
                "size": size,
                "query": {
                    "match": {
                        "document": question
                    }
                }
            }
            s = es.search(index='milqa', body=body)

            result_contexts = list()
            for hit in s['hits']['hits']:
                result_contexts.append(hit["_source"]["document"])

            # error_dict = dict()
            result_contexts_set = set(single_context for single_context in result_contexts)
            if context in result_contexts_set:
                match_counter = 1
                result_number = 0
                for result_context in result_contexts:
                    if result_context == context:
                        result_number = match_counter
                        break
                    else:
                        match_counter += 1
                match_len += 1
                all_context.append(value)  # .replace("\n", " "))
                all_question.append(key)
            else:
                error_counter += 1
                result_number = 'Nincs benne'
                all_context.append(value)  # .replace("\n", " "))
                all_question.append(key)
                # error_dict[question] = [context]

            if isinstance(result_number, str):
                result_dict[id] = result_number
            else:
                result_dict[id] = (1/int(result_number))
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
        print("összes eltalált/összes eset: " + str(summary_counter/len(milqa_contexts_dict)))

        print("MMR: " + str(summary/len(milqa_contexts_dict)) + " | error counter: " + str(error_counter))# + "\n" + str(result_dict))# + "\n" + all_context[2] + "\n" + all_question[2])

    print(f"Time spent: {t.elapsed:.2f} seconds")

    return 0

if __name__ == '__main__':
    print(get_highlights(es, 10))
