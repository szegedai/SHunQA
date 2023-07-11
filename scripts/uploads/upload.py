import pandas as pd

df = pd.read_csv("result.csv",
                 sep=',',
                 index_col=0,
                 na_filter=False,
                 encoding='utf-8')

skip = False
paragraphs = set()
paragraph_w_row = list()
paragraph_wall = list()

chapters = set()

for index, record in df.iterrows():
    # paragraph_temp = record['text'].split("\n")
    chapters_temp = record['text'].split("\n\n")

    # for one_paragraph in paragraph_temp:
        # print(one_paragh)
        # if one_paragraph == "":
        #     skip = True
        #     continue
        # if skip:
        #     skip = False
        #     continue

        # if one_paragraph not in paragraphs:
        #     paragraphs.add(one_paragraph)

            # paragraph_w_row.append(record['question'])
            # paragraph_w_row.append(record['official_text'])
            # paragraph_w_row.append(one_paragh)
            #
            # paragraphs.add(one_paragh)
            #
            # paragraph_wall.append(paragraph_w_row)
            #
            # paragraph_w_row = list()

    for one_chapter in chapters_temp:
        if not one_chapter.__contains__("\n"):
            continue

        if one_chapter not in chapters:
            chapters.add(one_chapter)

    break

alma = 42
