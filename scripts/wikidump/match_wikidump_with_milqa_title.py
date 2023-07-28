# Description: This script matches the milqa dataset with the wikidump dataset.

import os
import pandas as pd
import csv
import json


def match_wikidump_with_milqa():
    df = pd.read_csv("../source_xml/short.csv",
                     sep=';',
                     index_col=0,
                     na_filter=False,
                     encoding='utf-8')

    milqa_titles = set(df['title'].unique())

    directory = '/home/gszabo/PycharmProjects/elasticsearch-8.5.2-linux-x86_64/text'
    # line_counter = 0
    # lines_id = 0
    # wiki_data_with_id = dict()
    relevant_text = list()
    relevant_text_list = list()

    counter = 0
    relevant_counter = 0
    len_counter = 0
    len_counter_set = 0
    file_counter = 1
    json_texts_split_set = set()

    skip = False

    unique_dict = dict()
    for index, record in df.iterrows():
        question = record['question']
        context = record['context']
        title = record['title']
        answer = record["answer"]

        if question not in unique_dict:
            unique_dict[question] = (context, title, answer)
        else:
            pass

    print(len(unique_dict))

    for filename in os.listdir(directory):
        first_path = os.path.join(directory, filename)
        print(filename)
        print(file_counter) # 15
        # print("dict len: " + str(len(wiki_data_with_id)))
        if os.path.isfile(first_path):
            pass
        else:
            for second_filename in os.listdir(first_path):
                second_path = os.path.join(first_path, second_filename)
                if os.path.isfile(second_path):
                    # print(second_filename)
                    with open(first_path + "/" + second_filename, "r", encoding="utf-8") as f:
                        # lines = f.readlines()

                        for line in f.readlines():
                            json_line = json.loads(line)
                            alma = 42

                            if json_line["title"] in milqa_titles:
                                for key, value in unique_dict.items():
                                    if json_line["title"] == value[1]:
                                        relevant_text.append(json_line["id"])
                                        relevant_text.append(json_line["title"])
                                        relevant_text.append(json_line["url"])
                                        relevant_text.append(key)
                                        relevant_text.append(value[0])
                                        relevant_text.append(value[2])
                                        relevant_text.append(json_line["text"].replace("||||||", "\n"))

                                        relevant_text_list.append(relevant_text)
                                        relevant_text = list()
                            else:
                                if counter % 100 == 0 and counter < 800000:
                                    relevant_text.append(json_line["id"])
                                    relevant_text.append(json_line["title"])
                                    relevant_text.append(json_line["url"])
                                    relevant_text.append("-")
                                    relevant_text.append("--")
                                    relevant_text.append("---")
                                    relevant_text.append(json_line["text"].replace("||||||", "\n"))

                                    json_texts = json_line["text"].replace("||||||", "\n")
                                    len_counter += len(json_texts.split("\n"))
                                    json_texts_split = json_texts.split("\n")
                                    for text in json_texts_split:
                                        # if text == "":
                                        #     # print("-------------------------------------------------------")
                                        #     continue
                                        if text == "":
                                            skip = True
                                            continue
                                        if skip:
                                            skip = False
                                            continue
                                        json_texts_split_set.add(text)
                                        len_counter_set += 1

                                    #TODO mehet több pages így, mert +5k sor nem sok


                                    relevant_text_list.append(relevant_text)
                                    relevant_text = list()

                                    relevant_counter += 1

                                    if counter % 5000 == 0:
                                        print(counter)
                                counter += 1
        file_counter += 1
    print("relevant counter: ", relevant_counter)
    print("len_counter: ", len_counter)
    print("len_counter_set: ", len_counter_set)
    print("len_counter_set_len: ", len(json_texts_split_set))
    alma = 42
    fields = ["id", "title", "url", "question", "official_text", "answer", "text"]

    with open("milqaWiki_with_some_random_wikidump.csv", "w", encoding="utf-8") as f:
        write = csv.writer(f)

        write.writerow(fields)
        write.writerows(relevant_text_list)

def check_df(csv):
    df_old = pd.read_csv(csv[0],
                     sep=',',
                     names=["id", "title", "url", "question", "official_text", "answer", "text"],
                     header=0,
                     encoding='utf-8')

    df_new = pd.read_csv(csv[1],
                     sep=',',
                     names=["id", "title", "url", "question", "official_text", "answer", "text"],
                     header=0,
                     encoding='utf-8')

    print("result_1: ", len(df_old))
    print("new: ", len(df_new))

if __name__ == '__main__':
    # csv = "milqaWiki_with_some_random_wikidump.csv"
    csv = ["result_1.csv", "milqaWiki_with_some_random_wikidump.csv"]
    check_df(csv)
    # match_wikidump_with_milqa()
