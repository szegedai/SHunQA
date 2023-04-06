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
                     names=["clean_question", "answer"],
                     header=0,
                     encoding='utf-8')

    print(len(df))

    with Timer() as t:
        result_dict = dict()
        error_counter = 0
        id = 0
        match_len = 0

        all_context = list()
        all_answer = list()

        all_question = list()
        for index, record in df.iterrows():
            if id % 500 == 0:
                print(id)
            clean_question = record['clean_question']
            answer = record['answer']

            # TODO kérdés mondat vector lekérés -> body-t átírni a megfelelő formra és elvileg done

            # query top 10 guesses
            body = {
                "size": size,
                "query": {
                    "match": {
                        "document": clean_question
                    }
                }
            }
            s = es.search(index=elastic, body=body)

            result_contexts = list()
            result_official_contexts = list()
            for hit in s['hits']['hits']:
                result_contexts.append(hit["_source"]["document"])
                result_official_contexts.append(hit["_source"]["official_document"])

            # error_dict = dict()
            result_official_contexts_set = set(single_context for single_context in result_official_contexts)

            match_counter = 1
            result_number = 0
            in_text = False
            for set_in in result_official_contexts_set:
                if answer in set_in:
                    in_text = True
                    break
                # else:
                #     result_number = 'Nincs benne'
                #     all_answer.append(answer)
                #     all_question.append(question)

            if in_text:
                for set_in in result_official_contexts:
                    if set_in.__contains__(answer):
                        result_number = match_counter
                        break
                    else:
                        match_counter += 1
            else:
                error_counter += 1
                result_number = 'Nincs benne'


            # if answer in result_official_contexts_set:
            #     match_counter = 1
            #     result_number = 0
            #     for result_official_context in result_official_contexts:
            #         if result_official_context == official_context:
            #             result_number = match_counter
            #             break
            #         else:
            #             match_counter += 1
            #     match_len += 1
            #     all_context.append(official_context)
            #     all_question.append(question)
            # else:
            #     error_counter += 1
            #     result_number = 'Nincs benne'
            #     all_context.append(official_context)
            #     all_question.append(question)

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
        # print("összes eltalált/összes eset (Precision@k): " + str(summary_counter / len(df)))
        print("összes eltalált/összes eset (Precision@k): " + str(round((summary_counter / len(df)), 3)))
        # print("MRR: " + str(summary / len(df)))
        print("MRR: " + str(round((summary / len(df)), 3)))

    print(f"Time spent: {t.elapsed:.2f} seconds")
    alma = 42
    return 0


if __name__ == '__main__':
    size = 10
    # elastic = "milqa_w_lemma_w_official_context"
    # elastic = "milqa_paragraphs_extended"
    # elastic = "milqa_chapters_extended"
    elastic = "milqa_pages_extended"
    path = './csv/questionPoSLemma_answer.csv'
    print(get_highlights(path, elastic, es, size))


# MRR: 0.7388659473380436




# paragraph 10 wo PoSLemma
# összes eltalát eset 10 size mérettel: 3387
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 11627
# összes eltalált/összes eset (Precision@k): 0.22558944984680965
# MRR: 0.0767441921931065
# Time spent: 98.13 seconds

# chapters 10 wo PoSLemma
# összes eltalát eset 10 size mérettel: 4064
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 10950
# összes eltalált/összes eset (Precision@k): 0.27068069801518585
# MRR: 0.10082179912504875
# Time spent: 97.36 seconds

# page 10 wo PoSLemma
# összes eltalát eset 10 size mérettel: 4757
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 10257
# összes eltalált/összes eset (Precision@k): 0.3168376182229919
# MRR: 0.1310298747623896
# Time spent: 426.57 seconds



# TODO megnézni ezzel a módszerrel, hogy mennyire más, mint az előző megoldással (kvázi ugyan azzal a file-al megnézni így, ahogy akkor volt)

# paragraph question wo poslemma 10
# összes eltalát eset 10 size mérettel: 11051
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 3963
# összes eltalált/összes eset (Precision@k): 0.7360463567337152
# MRR: 0.23797910310165635
# Time spent: 70.90 seconds

# chapters question wo poslemma 10
# összes eltalát eset 10 size mérettel: 12571
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 2443
# összes eltalált/összes eset (Precision@k): 0.8372852004795525
# MRR: 0.2972758758492119
# Time spent: 92.64 seconds

# pages question wo poslemma 10
# összes eltalát eset 10 size mérettel: 13447
# összes eset 10 size mérettel: 15014
# összes vizsgált számon kívüli eset 10 size mérettel: 1567
# összes eltalált/összes eset (Precision@k): 0.8956307446383376
# MRR: 0.33397622536425986
# Time spent: 436.23 seconds
