import re
import os

import pandas as pd

from typing import Generator, Any

from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph

from tqdm import tqdm


def iter_block_items(parent: Any) -> Generator[Paragraph | Table, None, None]:
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.

    Args:
        parent (Any): The loaded document object.

    Yields:
        Paragraph | Table: The next Paragraph or Table from the loaded document.

    Raises:
        ValueError: If the parent is not a Document, _Cell or _Row object.
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


def get_text(filename: str) -> tuple[str, dict[str, list[str]]]:
    """
    Extracts the text and headings from a given Microsoft Word document.

    Args:
        filename (str): The name of the file.

    Returns:
        return_full_text (str): The full text of the document, including inserted headings for later splits (like: Heading 1, Heading 2, Heading 3)

        return_headings (dict[str, list[str]]): dictionary with three keys ('Heading 1', 'Heading 2', 'Heading 3')representing the extracted headings.
            The values are lists of the corresponding heading texts.
    """
    # Reading the docx file
    doc = Document(filename)
    full_text = []
    return_headings = {
        "Heading 1": list(),
        "Heading 2": list(),
        "Heading 3": list(),
    }
    # block is the yielded object from iter_block_items
    for block in iter_block_items(doc):
        # We check if what instance is the block if it is paragraph, we append the "Heading 1", "Heading 2", "Heading 3"
        # strings, so later we can split by that. For every run we gather the name of the headings, so we can put them into the full_text later

        if isinstance(block, Paragraph):
            if block.style.name == "Heading 1" and block.text != "":
                full_text.append(" Heading 1 " + block.text)
                return_headings["Heading 1"].append(" Heading 1 " + block.text)
            elif block.style.name == "Heading 2" and block.text != "":
                full_text.append(" Heading 2 " + block.text)
                return_headings["Heading 2"].append(" Heading 2 " + block.text)
            elif block.style.name == "Heading 3" and block.text != "":
                full_text.append(" Heading 3 " + block.text)
                return_headings["Heading 3"].append(" Heading 3 " + block.text)
            else:
                full_text.append(block.text)
        elif isinstance(block, Table):
            for row in block.rows:
                row_data = []
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        row_data.append(paragraph.text)
                full_text.append("\t".join(row_data))

    return_full_text = "\n".join(full_text)
    return return_full_text, return_headings


def make_smaller_text(
    source_data: tuple,
    source_headings: tuple,
    nlp: Any,
    smaller_than: int = 128,
    larger_than: int = 384,
    path: str = "../data",
) -> tuple[dict[str, list[str]], tuple[str]]:
    """
    Creating smaller texts for the reader and retriever

    Args:
        source_data (tuple[str]): The text we read
        source_headings (tuple): The headings of the text
        nlp (Any): The language model
        smaller_than (int, optional): A custom number where we set a random number to approximate the max length of the texts. Defaults to 128.
        larger_than (int, optional): A custom number to determine when to cut the docs into heading 3 snippets. Defaults to 384.
        path (str, optional): Path of the data. Defaults to "../data".

    Returns:
        data_dict (dict[str, list[str]]): The smaller snippets in dict
        file_names (tuple[str]): The filenames which are the keys for the dict
    """
    data_dict = dict()
    data_split, file_names = zip(
        *[
            ([" Heading 1 " + y.lstrip() for y in x.split("Heading 1")], f_name)
            if "Heading 1" in x
            else (x.split("\n\n"), f_name)
            for x, f_name in zip(source_data, os.listdir(path))
        ]
    )
    # data_split, file_names = zip(*[(x.split("Heading 2"), f_name) if "Heading 2" in x else (x.split("Heading 3"), f_name) if len(x) > 1000 and "Heading 3" in x else (x.split("\n\n"), f_name) for x, f_name in zip(data, os.listdir("data")) ])

    for data_s, file_name, heading in tqdm(
        zip(data_split, file_names, source_headings)
    ):
        data_dict[file_name] = list()

        for d in data_s:
            # If the length of the current list element is greater than the larger_than, than we split the text by the "Heading 2"
            if len(d) > larger_than and "Heading 2" in d:
                d_split_h2 = d.split(" Heading 2 ")
                d_split_h2 = [" Heading 2 " + x for x in d_split_h2 if x]
                d_split_h2[0] = d_split_h2[0].replace(" Heading 2 ", "")

                for d_s in d_split_h2:
                    # If the length of the current list element is greater than the larger_than and there is Heading 3 substring in the split, than we split the text by the "Heading 3"
                    if len(d_s) > larger_than and "Heading 3" in d_s:
                        d_split_h3 = d_s.split(" Heading 3 ")
                        d_split_h3 = [" Heading 3 " + x for x in d_split_h3 if x]
                        d_split_h3[0] = d_split_h3[0].replace(" Heading 3 ", "")

                        for d_s_h3 in d_split_h3:
                            # If the length of the current list element is greater than the larger_than, than we split the text with huspacy
                            if len(d_s_h3) > larger_than:
                                d_sentences = nlp(d_s_h3)

                                for d_sentence in d_sentences.sents:
                                    if (
                                        not data_dict[file_name]
                                        or len(d_sentence)
                                        + len(data_dict[file_name][-1])
                                        > larger_than
                                    ):
                                        data_dict[file_name].append(d_sentence.text)
                                        continue
                                    data_dict[file_name][-1] += f"\n{d_sentence.text}"
                                continue

                            # If the length of the current list element is greater than the lists last element length + the current element, than we split the text with huspacy
                            elif (
                                len(d_s_h3) + len(data_dict[file_name][-1])
                                > larger_than
                                or not data_dict[file_name]
                            ):
                                d_sentences = nlp(d_s_h3)

                                for d_sentence in d_sentences.sents:
                                    if (
                                        not data_dict[file_name]
                                        or len(d_sentence)
                                        + len(data_dict[file_name][-1])
                                        > larger_than
                                    ):
                                        data_dict[file_name].append(d_sentence.text)

                                        continue
                                    data_dict[file_name][-1] += f"\n{d_sentence.text}"
                                continue

                            data_dict[file_name][-1] += f"\n{d_s_h3}"
                        continue

                    # If the length of the current list element is greater than the larger_than, than we split the text with huspacy
                    elif len(d_s) > larger_than or not data_dict[file_name]:
                        d_sentences = nlp(d_s)

                        for d_sentence in d_sentences.sents:
                            if (
                                not data_dict[file_name]
                                or len(d_sentence) + len(data_dict[file_name][-1])
                                > larger_than
                            ):
                                data_dict[file_name].append(d_sentence.text)
                                continue
                            data_dict[file_name][-1] += f"\n{d_sentence.text}"
                        continue

                    data_dict[file_name][-1] += f"\n{d_s}"
                continue

            # If the length of the current list element is greater than the larger_than, than we split the text with huspacy
            elif len(d) > larger_than:
                d_sentences = nlp(d)

                for d_sentence in d_sentences.sents:
                    if (
                        not data_dict[file_name]
                        or len(d_sentence) + len(data_dict[file_name][-1]) > larger_than
                    ):
                        data_dict[file_name].append(d_sentence.text)
                        continue
                    data_dict[file_name][-1] += f"\n{d_sentence.text}"
                continue

            elif (
                not data_dict[file_name]
                or len(data_dict[file_name][-1]) >= smaller_than
                and len(d) >= 100
            ):
                data_dict[file_name].append(d)
                continue

            data_dict[file_name][-1] += f"\n{d}"

    return data_dict, file_names


def insert_headings(
    source_data: dict[str, list[str]], source_headings: tuple
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """
    Inserts the headings into every sub snippet

    Args:
        source_data (dict[str, list[str]]): Dict with filenames as keys and the list of snippets
        source_headings (tuple): Previous headings to put into every snippet

    Returns:
        The data with headings in it and headings in order, to append them at the and of the paragraph separator line
    """
    heading_return = dict()

    for (fn, data_snippet), heading in zip(source_data.items(), source_headings):
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
                    if h != current_heading_one:
                        current_heading_one = h
                        current_heading_two = ""
                        current_heading_three = ""
                    else:
                        current_heading_one = h

            for h in heading["Heading 2"]:
                if h in d:
                    two_i += 1
                    if h != current_heading_two:
                        current_heading_two = h
                        current_heading_three = ""
                    else:
                        current_heading_two = h

            for h in heading["Heading 3"]:
                if h in d:
                    three_i += 1
                    current_heading_three = h
            # Here you will see the problem, its probably
            # print("=" * 50)
            # print(fn)
            # print(current_heading_one)
            # print(current_heading_two)
            # print(current_heading_three)
            # print("=" * 50)
            if current_heading_three not in d:
                source_data[fn][i] = f"{current_heading_three}\n" + source_data[fn][i]

            if current_heading_two not in d:
                source_data[fn][i] = f"{current_heading_two}\n" + source_data[fn][i]

            if current_heading_one not in d:
                source_data[fn][i] = f"{current_heading_one}\n" + source_data[fn][i]
            heading_return[fn].append(
                f"h1<{current_heading_one}>h2<{current_heading_two}>h3<{current_heading_three}>\n"
            )
            # print(fn, f"h1<{current_heading_one}>h2<{current_heading_two}>h3<{current_heading_three}>\n")
    return source_data, heading_return


def write_paragraphs_to_txt(
    source_data: dict[str, list[str]],
    source_headings: dict[str, list[str]],
    txt_name: str = "data_paragraphs.txt",
) -> None:
    """
    Writes the text into a txt file

    Args:
        source_data (dict[str, list[str]]): Text with headings in it
        source_headings (dict[str, list[str]]): Headings in order, to append them at then and of the paragraph separator line
        txt_name (str, optional): Preferred name of the txt file. Defaults to "data_paragraphs.txt".
    """
    with open(txt_name, "w", encoding="utf-8") as f:
        for (file_name, text), heading_ordered in zip(
            source_data.items(), source_headings.values()
        ):
            val = list(
                map(
                    "\nparagraphs------------------------------------------------------------------------------------------------------------------------- headings".join,
                    zip(text, heading_ordered),
                )
            )
            val = "".join(val)
            val = val.replace(" Heading 3 ", "")
            val = val.replace(" Heading 2 ", "")
            val = val.replace(" Heading 1 ", "")
            val = val.replace(" Heading 1", "")
            f.write(val + "\n")
            f.write(
                f"file------------------------------------------------------------------------------------------------------------------------- file_name<{file_name}>\n"
            )


def read_txt_paragraphs(
    txt_name: str = "data_paragraphs.txt",
) -> tuple[pd.DataFrame, list[str]]:
    """
    Reads the txt file, and sorts the data

    Args:
        txt_name (str, optional): Preferred name of the txt file. Defaults to "data_paragraphs.txt".

    Returns:
        Splitted texts, headers and the file names.
    """
    with open(txt_name, "r", encoding="utf-8") as f:
        text_read = f.read()
        # get all file names which are inside <filename>
        file_names = re.findall(r"file_name<([^>]+)", text_read)
        # replace the file names with empty string, so we can split by the file separator line
        text_read = re.sub(r"file_name<([^>]+)>", "", text_read)

        splitted_texts_by_file = text_read.split(
            "file------------------------------------------------------------------------------------------------------------------------- "
        )
        splitted_texts_by_paragraph = dict()

        for fn, splitted_text in zip(file_names, splitted_texts_by_file):
            splitted_texts_by_paragraph[fn] = dict()
            # splitting the file by the paragraph separator, because there is \n inbetween last paragraph and the file separator we don't include that
            splitted_texts_by_paragraph[fn]["text"] = splitted_text.split(
                "paragraphs------------------------------------------------------------------------------------------------------------------------- "
            )[:-1]
            splitted_texts_by_paragraph[fn]["headers"] = list()

            for i, paragraph in enumerate(splitted_texts_by_paragraph[fn]["text"]):
                # get all the headers which are inside "headersh1<headername>h2<headername>h3<headername>"
                splitted_texts_by_paragraph[fn]["headers"].append(
                    re.findall(r"<([^>]+)>", paragraph)
                )
                # replace the headers with empty string, it is not needed in the file
                splitted_texts_by_paragraph[fn]["text"][i] = re.sub(
                    r"headingsh1<.*?>h2<.*?>h3<.*?>\n", "", paragraph
                )

    df = pd.DataFrame(splitted_texts_by_paragraph).T.reset_index(
        names=["file_names", "text", "headers"]
    )
    df = df.explode(["text", "headers"]).reset_index(drop=True)

    return df, file_names


def split_docx(
    nlp: Any, data_path: str = "data", txt_name: str = "data_paragraphs.txt"
) -> tuple[pd.DataFrame, list[str]]:
    """
    Reads the docx files, and parses them into smaller texts with headings.

    Args:
        data_path (str, optional): Path of the data folder. Defaults to "data".
        txt_name (str, optional): Preferred name of the txt file. Defaults to "data_paragraphs.txt".

    Returns:
        Splitted texts, headers and the file names.
    """

    data, headings = zip(
        *[get_text(os.path.join(data_path, x)) for x in os.listdir(data_path)]
    )

    smaller_data_snipets, fname = make_smaller_text(data, headings, nlp, path=data_path)

    smaller_data_snipets_with_headings, headings_ordered = insert_headings(
        smaller_data_snipets, headings
    )

    write_paragraphs_to_txt(smaller_data_snipets_with_headings, headings_ordered)

    return read_txt_paragraphs(txt_name)
