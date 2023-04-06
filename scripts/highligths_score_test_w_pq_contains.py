from elasticsearch import Elasticsearch
import pandas as pd
from contexttimer import Timer
import csv


es = Elasticsearch(
    "http://rgai3.inf.u-szeged.hu:3427/",
    basic_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
    verify_certs=False
)


def get_highlights(csv, fields, virgin, es, size):
    # adatok kinyerése pd-ből, a már tisztított kérdésekkel

    if virgin:
        df = pd.read_csv(csv,
                         sep=";",
                         index_col=0,
                         na_filter=False,
                         encoding='utf-8')

        # df = pd.read_csv(csv,
        #                  names=["question", "context"],
        #                  encoding='utf-8')
    else:
        df = pd.read_csv(csv,
                         names=fields,
                         header=0,
                         encoding='utf-8')

    with Timer() as t:
        result_dict = dict()
        error_counter = 0
        id = 0
        match_len = 0
        all_context = list()
        all_question = list()
        for index, record in df.iterrows():
            if id % 500 == 0:
                print(id)
            if not virgin:
                question = record['question']
                # official_context = record[fields[2]]
                answer = record["answer"]
            else:
                question = record['question']
                # official_context = record[fields[1]]
                answer = record["answer"]


            # query top 10 guesses
            body = {
                "size": size,
                "query": {
                    "match": {
                        "official_document": question
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
            # result_official_contexts_set = set(single_context for single_context in result_official_contexts)
            # if official_context in result_official_contexts_set:
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

            result_official_contexts_set = set(single_context for single_context in result_official_contexts)

            match_counter = 1
            result_number = 0
            in_text = False
            for set_in in result_official_contexts_set:
                if answer in set_in:
                    in_text = True
                    break

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

    return 0


if __name__ == '__main__':
    preck = 10
    # Virgin
    # PoS and Lemma
    # Lemma
    # main_list = list(['csv/virgin_database_unique.csv', ["question", "context"], True])
    # main_list = list(['csv/q_woPoSAndwLemma_c_wLemma_c_wOfficial.csv', ["PoSLemmatizedQuestion", "lemmatizedContext", "officialContext"], False])
    # main_list = list(['csv/q_wLemma_c_wLemma_c_wOfficial.csv', ["LemmatizedQuestion", "lemmatizedContext", "officialContext"], False])
    # main_list = list(['csv/q_woPoS_c_wLemma_c_wOfficial.csv', ["PoSQuestion", "lemmatizedContext", "officialContext"], False])
    # print(get_highlights(main_list[0], main_list[1], main_list[2], es, preck))
    print(get_highlights("../source_xml/short.csv", [], True, es, preck))



# virgin
# 1
# összes eltalát eset 1 size mérettel: 5632
# összes eset 1 size mérettel: 12851
# összes vizsgált számon kívüli eset 1 size mérettel: 7219
# összes eltalált/összes eset (Precision@k): 0.4382538323865847
# MRR: 0.4382538323865847 | error counter: 7219
# Time spent: 48.40 seconds

# 3
# összes eltalát eset 3 size mérettel: 7644
# összes eset 3 size mérettel: 12851
# összes vizsgált számon kívüli eset 3 size mérettel: 5207
# összes eltalált/összes eset (Precision@k): 0.594817523928099
# MRR: 0.5074183591419569 | error counter: 5207
# Time spent: 50.68 seconds

# 4
# összes eltalát eset 4 size mérettel: 8063
# összes eset 4 size mérettel: 12851
# összes vizsgált számon kívüli eset 4 size mérettel: 4788
# összes eltalált/összes eset (Precision@k): 0.6274219905065753
# MRR: 0.5155694757865761 | error counter: 4788
# Time spent: 55.88 seconds

# 5
# összes eltalát eset 5 size mérettel: 8414
# összes eset 5 size mérettel: 12851
# összes vizsgált számon kívüli eset 5 size mérettel: 4437
# összes eltalált/összes eset (Precision@k): 0.6547350400747024
# MRR: 0.5210320857001981 | error counter: 4437
# Time spent: 55.40 seconds

# 10
# összes eltalát eset 10 size mérettel: 9374
# összes eset 10 size mérettel: 12851
# összes vizsgált számon kívüli eset 10 size mérettel: 3477
# összes eltalált/összes eset (Precision@k): 0.7294373978678702
# MRR: 0.5310991794845159 | error counter: 3477
# Time spent: 60.04 seconds

# 300
# összes eltalát eset 300 size mérettel: 11517
# összes eset 300 size mérettel: 12851
# összes vizsgált számon kívüli eset 300 size mérettel: 1334
# összes eltalált/összes eset (Precision@k): 0.8961948486499105
# MRR: 0.5378575104288472 | error counter: 1334
# Time spent: 466.17 seconds

# --------------------------------------------------------------------------------------------

# pos
# 1
# összes eltalát eset 1 size mérettel: 5757
# összes eset 1 size mérettel: 12851
# összes vizsgált számon kívüli eset 1 size mérettel: 7094
# összes eltalált/összes eset (Precision@k): 0.44798070189090344
# MRR: 0.44798070189090344 | error counter: 7094
# Time spent: 40.58 seconds

# 3
# összes eltalát eset 3 size mérettel: 7750
# összes eset 3 size mérettel: 12851
# összes vizsgált számon kívüli eset 3 size mérettel: 5101
# összes eltalált/összes eset (Precision@k): 0.6030659092677613
# MRR: 0.5165486473166774 | error counter: 5101
# Time spent: 41.66 seconds

# 4
# összes eltalát eset 4 size mérettel: 8170
# összes eset 4 size mérettel: 12851
# összes vizsgált számon kívüli eset 4 size mérettel: 4681
# összes eltalált/összes eset (Precision@k): 0.6357481908022722
# MRR: 0.5247192177003049 | error counter: 4681
# Time spent: 44.22 seconds

# 5
# összes eltalát eset 5 size mérettel: 8547
# összes eset 5 size mérettel: 12851
# összes vizsgált számon kívüli eset 5 size mérettel: 4304
# összes eltalált/összes eset (Precision@k): 0.6650844292272975
# MRR: 0.5305864653853066 | error counter: 4304
# Time spent: 45.70 seconds

# 10
# összes eltalát eset 10 size mérettel: 9522
# összes eset 10 size mérettel: 12851
# összes vizsgált számon kívüli eset 10 size mérettel: 3329
# összes eltalált/összes eset (Precision@k): 0.7409540113609836
# MRR: 0.5407869562371119 | error counter: 3329
# Time spent: 55.58 seconds

# 300
# összes eltalát eset 300 size mérettel: 11281
# összes eset 300 size mérettel: 12851
# összes vizsgált számon kívüli eset 300 size mérettel: 1570
# összes eltalált/összes eset (Precision@k): 0.8778305190257567
# MRR: 0.547150855314735 | error counter: 1570
# Time spent: 262.25 seconds

# --------------------------------------------------------------------------------------------

# 1 lemma
# összes eltalát eset 1 size mérettel: 8318
# összes eset 1 size mérettel: 12851
# összes vizsgált számon kívüli eset 1 size mérettel: 4533
# összes eltalált/összes eset (Precision@k): 0.6472648042953856
# MRR: 0.6472648042953856 | error counter: 4533
# Time spent: 65.46 seconds

# 3 lemma:
# összes eltalát eset 3 size mérettel: 10375
# összes eset 3 size mérettel: 12851
# összes vizsgált számon kívüli eset 3 size mérettel: 2476
# összes eltalált/összes eset (Precision@k): 0.8073301688584545
# MRR: 0.718491427385675 | error counter: 2476
# Time spent: 72.92 seconds

# 4 lemma:
# összes eltalát eset 4 size mérettel: 10737
# összes eset 4 size mérettel: 12851
# összes vizsgált számon kívüli eset 4 size mérettel: 2114
# összes eltalált/összes eset (Precision@k): 0.8354991829429617
# MRR: 0.7255336809068018 | error counter: 2114
# Time spent: 74.60 seconds

# 5 lemma:
# összes eltalát eset 5 size mérettel: 11029
# összes eset 5 size mérettel: 12851
# összes vizsgált számon kívüli eset 5 size mérettel: 1822
# összes eltalált/összes eset (Precision@k): 0.8582211501050502
# MRR: 0.7300780743392186 | error counter: 1822
# Time spent: 75.99 seconds

# 10 lemma:
# összes eltalát eset 10 size mérettel: 11672
# összes eset 10 size mérettel: 12851
# összes vizsgált számon kívüli eset 10 size mérettel: 1179
# összes eltalált/összes eset (Precision@k): 0.9082561668352658
# MRR: 0.7368711964852331 | error counter: 1179
# Time spent: 86.01 seconds

# 300 lemma:
# összes eltalát eset 300 size mérettel: 12644
# összes eset 300 size mérettel: 12851
# összes vizsgált számon kívüli eset 300 size mérettel: 207
# összes eltalált/összes eset (Precision@k): 0.9838923041008482
# MRR: 0.7403155622517146 | error counter: 207
# Time spent: 505.53 seconds

# --------------------------------------------------------------------------------------------

# 1 pos lemma:
# összes eltalát eset 1 size mérettel: 8429
# összes eset 1 size mérettel: 12851
# összes vizsgált számon kívüli eset 1 size mérettel: 4422
# összes eltalált/összes eset (Precision@k): 0.6559022644152206
# MRR: 0.6559022644152206 | error counter: 4422
# Time spent: 54.69 seconds

# 3 pos lemma:
# összes eltalát eset 3 size mérettel: 10456
# összes eset 3 size mérettel: 12851
# összes vizsgált számon kívüli eset 3 size mérettel: 2395
# összes eltalált/összes eset (Precision@k): 0.8136331802972532
# MRR: 0.7264155837418601 | error counter: 2395
# Time spent: 55.59 seconds

# 4 pos lemma:
# összes eltalát eset 4 size mérettel: 10841
# összes eset 4 size mérettel: 12851
# összes vizsgált számon kívüli eset 4 size mérettel: 2010
# összes eltalált/összes eset (Precision@k): 0.8435919383705548
# MRR: 0.7339052732601855 | error counter: 2010
# Time spent: 57.25 seconds

# 5 pos lemma:
# összes eltalát eset 5 size mérettel: 11125
# összes eset 5 size mérettel: 12851
# összes vizsgált számon kívüli eset 5 size mérettel: 1726
# összes eltalált/összes eset (Precision@k): 0.865691385884367
# MRR: 0.7383251627629475 | error counter: 1726
# Time spent: 54.04 seconds

# 10 pos lemma
# összes eltalát eset 10 size mérettel: 11768
# összes eset 10 size mérettel: 12851
# összes vizsgált számon kívüli eset 10 size mérettel: 1083
# összes eltalált/összes eset (Precision@k): 0.9157264026145825
# MRR: 0.7451624109296655 | error counter: 1083
# Time spent: 61.27 seconds

# 300 pos lemma:
# összes eltalát eset 300 size mérettel: 12640
# összes eset 300 size mérettel: 12851
# összes vizsgált számon kívüli eset 300 size mérettel: 211
# összes eltalált/összes eset (Precision@k): 0.98358104427671
# MRR: 0.7484266314959167 | error counter: 211
# Time spent: 385.31 seconds

