# https://github.com/attardi/wikiextractor
# python -m wikiextractor.WikiExtractor data.xml
import pandas as pd
import os
import csv

df = pd.read_csv('../source_xml/world_war_II_subcategories.csv',
                 sep='\t',
                 names=['#', 'Title', 'Page ID', 'Namespace', 'Size (bytes)', 'Last change'],
                 encoding='utf-8')

IDs = set(df['Page ID'])

directory = '/home/gszabo/PycharmProjects/elasticsearch-8.5.2-linux-x86_64/source_xml/text'
line_counter = 0
lines_id = 0
wiki_data_with_id = dict()
subcontext = list()

for filename in os.listdir(directory):
    first_path = os.path.join(directory, filename)
    print(filename)
    print("dict len: " + str(len(wiki_data_with_id)))
    if os.path.isfile(first_path):
        pass
    else:
        for second_filename in os.listdir(first_path):
            second_path = os.path.join(first_path, second_filename)
            if os.path.isfile(second_path):
                # print(second_filename)
                with open(first_path + "/" + second_filename, "r") as f:
                    lines = f.readlines()

                for line in lines:
                    if line.startswith('<doc'):
                        lines_id = line.split('id="')[1].split('"')[0]
                        line_counter = 1
                        continue
                    if line_counter == 1:
                        subcontext.append(line)
                        line_counter += 1
                        continue
                    if line_counter == 2 and not line.startswith("\n") and not line.startswith("</doc"):
                        subcontext.append(line)
                    if line.startswith("</doc"):
                        context = "".join(subcontext)
                        if lines_id in IDs:
                            wiki_data_with_id[int(lines_id)] = context
                        subcontext = list()
                        context = ""
                        line_counter = 0

sorted_wiki_data_with_id = dict(sorted(wiki_data_with_id.items()))

with open('../source_xml/text/relevant_wikidump.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for row in sorted_wiki_data_with_id.items():
        writer.writerow(row)
