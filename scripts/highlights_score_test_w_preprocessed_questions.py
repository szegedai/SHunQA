from elasticsearch import Elasticsearch
import pandas as pd
from contexttimer import Timer

# huspacy-vel a kérdések/adatok előfeldolgozása/tisztása

import spacy

# pip install https://huggingface.co/huspacy/hu_core_news_trf/resolve/main/hu_core_news_trf-any-py3-none-any.whl
# nlp = spacy.load("hu_core_news_trf")
#
# nlp.remove_pipe('experimental_arc_predicter')
# nlp.remove_pipe('experimental_arc_labeler')
# nlp.remove_pipe('ner')
#
# df = pd.read_csv('https://raw.githubusercontent.com/zsozso21/soc_media/main/milqa_short_answers.csv',
#                  names=['table_id', 'id', 'context', 'title', 'question', 'end', 'start', 'answer'],
#                  header=1,
#                  encoding='utf-8')
#
# milqa_contexts_dict = dict()
# clean_tokens = list()
#
# counter = 0
# for index, record in df.iterrows():
#     context = record['context']
#     question = record['question']
#     doc = nlp(question)
#
#     for token in doc:
#         # print(token.text, token.pos_, token.dep_)
#         if token.pos_ not in ['DET', 'ADV', 'PRON', 'PUNCT']:
#             clean_tokens.append(token.text)
#
#     clean_question = " ".join(clean_tokens)
#
#     if clean_question not in milqa_contexts_dict:
#         milqa_contexts_dict[clean_question] = context
#         clean_question = ""
#         clean_tokens = list()
#     else:
#         clean_question = ""
#         clean_tokens = list()
#     if counter == 100:
#         break
#     counter += 1

# adatok kinyerése pd-ből, a már tisztított kérdésekkel

df = pd.read_csv('my_file.csv',
                 names=['question', 'context'],
                 header=1,
                 encoding='utf-8')

milqa_contexts_dict = dict()

clean_question = ""
context = ""
counter = 0

for index, record in df.iterrows():
    clean_question = record['question']
    context = record['context']

    if clean_question not in milqa_contexts_dict:
        milqa_contexts_dict[clean_question] = context
    else:
        pass
    # if counter == 100:
    #     print(42)
    #     break
    # counter += 1


    # adatok kinyerése, ha txt fájlból kell kiszedni az adatokat
    # if line.startswith("\n"):
    #     if clean_question not in milqa_contexts_dict:
    #         context = " ".join(context_list)
    #         milqa_contexts_dict[clean_question] = context
    #         clean_question = ""
    #         context = ""
    #     else:
    #         clean_question = ""
    #         context = ""
    #     continue
    #
    # if len(line.split(":")) > 1:
    #     clean_question = line.split(":")[0]
    #     context_list.append(line.split(":")[1][1:])
    #
    # if len(line.split(":")) == 1:
    #     context_list.append(line)




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
            s = es.search(index='milqa_w_lemma', body=body)

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
        print("összes eltalált/összes eset: " + str(summary_counter / len(milqa_contexts_dict)))

        print("MRR: " + str(summary / len(milqa_contexts_dict)) + " | error counter: " + str(
            error_counter))  # + "\n" + str(result_dict))# + "\n" + all_context[2] + "\n" + all_question[2])

    print(f"Time spent: {t.elapsed:.2f} seconds")

    return 0


if __name__ == '__main__':
    print(get_highlights(es, 1))
