import re
import pandas as pd

from typing import Any


def preprocess_data(dataframe: pd.DataFrame, nlp: Any, input_column: str = "text", output_column: str = "lemmatized_text") -> pd.DataFrame:
    """Lemmatize the given data.

    Args:
        dataframe (pd.DataFrame): The dataframe with data.
        nlp (Any): The spacy model.
        input_column (str, optional): The name of the input column. Defaults to "text".
        output_column (str, optional): The name of the output column. Defaults to "lemmatized_text".

    Returns:
        pd.DataFrame: The dataframe with the lemmatized data in a new column.
    """
    regex_ = re.compile("^[.:,;!?]")

    context_lemmatized_list = list()
    per_n_line = False
    for _, record in dataframe.iterrows():
        doc = nlp(record[input_column])

        context_lemmatized = ""

        for token in doc:
            if per_n_line:
                if token.text.startswith("\n"):
                    continue
                else:
                    per_n_line = False
                    context_lemmatized += "\n"
            if token.text.startswith("\n"):
                per_n_line = True
                continue

            if regex_.match(token.text):
                context_lemmatized += token.lemma_
            else:
                if context_lemmatized[-1:] == "\n":
                    context_lemmatized += token.lemma_
                else:
                    context_lemmatized += " " + token.lemma_

        context_lemmatized_list.append(context_lemmatized)

    df_preprocessed = dataframe.copy(True)

    df_preprocessed[output_column] = context_lemmatized_list

    return df_preprocessed
