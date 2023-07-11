import spacy
import re
import os
import pandas as pd
from tqdm import tqdm
from elasticsearch import Elasticsearch

from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph

ES = Elasticsearch(
        "http://localhost:3427/",
        basic_auth=("elastic", "7ZQhi+zIL357DgjIjyi0"),
        verify_certs=False
    )

nlp = spacy.load("hu_core_news_trf")

nlp.remove_pipe('experimental_arc_predicter')
nlp.remove_pipe('experimental_arc_labeler')
nlp.remove_pipe('ner')
    

def iter_block_items(parent):
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    elif isinstance(parent, _Row):
        parent_elm = parent._tr
    else:
        raise ValueError("something's not right")
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)
            
def get_text(filename:str):
    """
    Extracts the text and headings from a given Microsoft Word document.

    :param filename: name of the file duh
    :returns    return_full_text: The full text of the document, including inserted headings for later splits.
              like: Heading 1, Heading 2, Heading 3
                return_headings: A dictionary with three keys ('Heading 1', 'Heading 2', 'Heading 3')
              representing the extracted headings. The values are lists of the corresponding heading texts.
    """
    #Reading the docx file
    doc = Document(filename)
    full_text = []
    return_headings = {
        "Heading 1": list(),
        "Heading 2": list(),
        "Heading 3": list()
    }
    #block is the yielded object from iter_block_items
    for block in iter_block_items(doc):
        # We check if what instance is the block if it is paragraph, we append the "Heading 1", "Heading 2", "Heading 3"
        # strings, so later we can split by that. For every run we gather the name of the headings, so we can put them into the full_text later
        if isinstance(block, Paragraph):
            if block.style.name == "Heading 1":
                full_text.append(" Heading 1 " + block.text)
                return_headings["Heading 1"].append(block.text)
            elif block.style.name == "Heading 2":
                full_text.append(" Heading 2 " + block.text)
                return_headings["Heading 2"].append(block.text)
            elif block.style.name == "Heading 3":
                full_text.append(" Heading 3 " + block.text)
                return_headings["Heading 3"].append(block.text)
            else:
                full_text.append(block.text)
        elif isinstance(block, Table):
            for row in block.rows:
                row_data = []
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        row_data.append(paragraph.text)
                full_text.append("\t".join(row_data))

    return_full_text = '\n'.join(full_text)
    return return_full_text, return_headings

def make_smaller_text_original(source_data: tuple, dir_name:str, source_headings:dict, smaller_than:int =512, larger_than:int=1000):
    """
    Creating smaller texts for the reader and retriever

    :param source_data: the text we read
    :param source_headings: every heading by files
    :param smaller_than: A custom number where we set a random number to approximate the max length of the texts
    :param larger_than: A custom number to determine when to cut the docs into heading 3 snippets
    :return: data_dict, file_names: returns the smaller snippets in dict and the filenames which are the keys for the dict
    """
    data_dict = dict()
    data_split, file_names = zip(
        *[(x.split("Heading 1"), f_name) if "Heading 1" in x else (x.split("\n\n"), f_name) for x, f_name in
          zip(source_data, os.listdir(dir_name))])
    # data_split, file_names = zip(*[(x.split("Heading 2"), f_name) if "Heading 2" in x else (x.split("Heading 3"), f_name) if len(x) > 1000 and "Heading 3" in x else (x.split("\n\n"), f_name) for x, f_name in zip(data, os.listdir("data")) ])

    for data_s, file_name, heading in tqdm(zip(data_split, file_names, source_headings)):
        data_dict[file_name] = list()
        for d in data_s:
            #If the length of the current list element is greater than the larger_than, than we splti the text by the "Heading 3"
            if len(d) > larger_than and "Heading 2" in d:
                d_split_h2 = d.split("Heading 2")
                for d_s in d_split_h2:

                    if len(d_s) > larger_than and "Heading 3" in d_s:
                        d_split_h3 = d.split("Heading 3")
                        for d_s_h3 in d_split_h3:
                            if      len(d_s_h3) > 200 \
                                    or not data_dict[file_name] \
                                    or d_s_h3 not in heading["Heading 1"] \
                                    or d_s_h3 not in heading["Heading 2"] \
                                    or d_s_h3 not in heading["Heading 3"]:

                                data_dict[file_name].append(d_s_h3)
                            else:
                                data_dict[file_name][-1] += f"\n{d_s_h3}"
                    elif      len(d_s) > 200 \
                            or not data_dict[file_name] \
                            or d_s not in heading["Heading 1"] \
                            or d_s not in heading["Heading 2"] \
                            or d_s not in heading["Heading 3"]:

                        data_dict[file_name].append(d_s)
                    else:
                        data_dict[file_name][-1] += f"\n{d_s}"

            elif not data_dict[file_name] or len(data_dict[file_name][-1]) >= smaller_than and len(d) >= 100:

                data_dict[file_name].append(d)

            else:
                data_dict[file_name][-1] += f"\n{d}"

    return data_dict, file_names


def insert_headings(source_data, source_headings):
    """
    inserts the headings into every sub snippet
    :param source_data: dict with filenames as keys and the list of snippets
    :param source_headings: previous headings to put into every snippet
    :return: the data with headings in it and headings in order, to append them at then and of the paragraph separator line
    """
    heading_return = dict()
    for (fn, data_snippet) , heading in zip(source_data.items(), source_headings):
        one_i = 0
        two_i = 0
        three_i = 0
        current_heading_one = str()
        current_heading_two = str()
        current_heading_three = str()
        heading_return[fn] = list()
        for i, d in enumerate(data_snippet):

            for h in heading["Heading 1"]:
                if h in d:
                    one_i += 1
                    current_heading_one = h

            for h in heading["Heading 2"]:
                if h in d:
                    two_i += 1
                    current_heading_two = h

            for h in heading["Heading 3"]:
                if h in d:
                    three_i += 1
                    current_heading_three = h

            if current_heading_three not in d:
                source_data[fn][i] = f"{current_heading_three}\n" + source_data[fn][i]

            if current_heading_two not in d:
                source_data[fn][i] = f"{current_heading_two}\n" + source_data[fn][i]

            if current_heading_one not in d:
                source_data[fn][i] = f"{current_heading_one}\n" + source_data[fn][i]
            heading_return[fn].append(
                f"h1<{current_heading_one}>h2<{current_heading_two}>h3<{current_heading_three}>\n")
    return source_data, heading_return


def write_paragraphs_to_txt(source_data, source_headings, txt_name="data_paragraphs.txt"):
    """
    Writes the text into a txt file

    :param source_data: text with headings in it
    :param source_headings: headings in order, to append them at then and of the paragraph separator line
    :param txt_name: preferred name for the txt
    """
    with open(txt_name, "w", encoding="utf-8") as f:
        for (file_name, text), heading_ordered in zip(source_data.items(), source_headings.values()):
            val = list(
                map("\nparagraphs------------------------------------------------------------------------------------------------------------------------- headings".join,
                    zip(text, heading_ordered)))
            val = "".join(val)
            val = val.replace("Heading 3", "")
            val = val.replace("Heading 2", "")
            val = val.replace("Heading 1", "")
            f.write(val + "\n")
            f.write(
                f"file------------------------------------------------------------------------------------------------------------------------- file_name<{file_name}>\n")


def read_txt_paragraphs(txt_name:str="data_paragraphs.txt" ):
    """
    Reads the txt file, and sorts the data
    :param txt_name: preferred name for the txt file
    :return: splitted texts, headers and the file names
    """
    with open(txt_name, "r", encoding="utf-8") as f:
        text_read = f.read()
        # get all file names which are inside <filename>
        file_names = re.findall(r"file_name<([^>]+)", text_read)
        # replace the file names with empty string, so we can split by the file separator line
        text_read = re.sub(r"file_name<([^>]+)>", "", text_read)

        splitted_texts_by_file = text_read.split(
            "file------------------------------------------------------------------------------------------------------------------------- ")
        splitted_texts_by_paragraph = dict()

        for (fn, splitted_text) in zip(file_names, splitted_texts_by_file):
            splitted_texts_by_paragraph[fn] = dict()
            # splitting the file by the paragraph separator, because there is \n inbetween last paragraph and the file separator we don't include that
            splitted_texts_by_paragraph[fn]["text"] = splitted_text.split(
                "paragraphs------------------------------------------------------------------------------------------------------------------------- ")[:-1]
            splitted_texts_by_paragraph[fn]["headers"] = list()

            for i, paragraph in enumerate(splitted_texts_by_paragraph[fn]["text"]):
                # get all the headers which are inside "headersh1<headername>h2<headername>h3<headername>"
                splitted_texts_by_paragraph[fn]["headers"].append(re.findall(r"<([^>]+)>", paragraph))
                # replace the headers with empty string, it is not needed in the file
                splitted_texts_by_paragraph[fn]["text"][i] = re.sub(r"headingsh1<.*?>h2<.*?>h3<.*?>\n", "", paragraph)

    return splitted_texts_by_paragraph, file_names

def preprocess_data(dataframe):
    regex_ = re.compile("^[.:,;!?]")
    
    context_lemmatized_list = list()
    per_n_line = False
    for index, record in dataframe.iterrows():
        doc = nlp(record["text"])

        context_lemmatized = ""

        for token in doc:
            if per_n_line:
                if token.text.startswith("\n"):
                    continue
                else:
                    per_n_line = False
                    context_lemmatized += '\n'
            if token.text.startswith("\n"):
                per_n_line = True
                continue

            if regex_.match(token.text):
                context_lemmatized += token.lemma_
            else:
                if context_lemmatized[-1:] == '\n':
                    context_lemmatized += token.lemma_
                else:
                    context_lemmatized += " " + token.lemma_

        context_lemmatized_list.append(context_lemmatized)
        
    df_preprocessed = df.copy(df)
    
    df_preprocessed["lemmatized_text"] = context_lemmatized_list
    
    return df_preprocessed

def upload_to_elastic(df_preprocessed, es):
    for i, record in df_preprocessed.iterrows():
        headers = dict()
        for j in range(3):
            try:
                headers[j] = record["headers"][j]
            except:
                headers[j] = "-"

        doc = {
            "document": record["lemmatized_text"],
            "official_document": record["text"],
            "file_name": record["file_names"],
            "h1": headers[0],
            "h2": headers[1],
            "h3": headers[2]
        }

        resp = es.index(index="forig_extend_headers", id=str(i), document=doc)


    print("OK")

if __name__ == "__main__":
    dir_name = "raw_data"
    
    try:
        data, headings = zip(*[get_text(os.path.join("raw_data", x)) for x in os.listdir("raw_data")])
    except:
        raise Exception("Use: mkdir" + dir_name + "command and move here the ONLY .docx files!")

    smaller_data_snipets, fname = make_smaller_text_original(data, dir_name, source_headings=headings)

    smaller_data_snipets_with_headings, headings_ordered = insert_headings(smaller_data_snipets, headings)

    write_paragraphs_to_txt(smaller_data_snipets_with_headings, headings_ordered)

    para, _ = read_txt_paragraphs(txt_name="data_paragraphs.txt")
    df = pd.DataFrame(para).T.reset_index(names=["file_names", "text", "headers"])
    df = df.explode(['text', 'headers']).reset_index(drop=True)
    
    df_preprocessed = preprocess_data(df)

    upload_to_elastic(df_preprocessed, ES)