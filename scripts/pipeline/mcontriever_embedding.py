import pandas as pd
from alive_progress import alive_bar
from transformers import AutoTokenizer, AutoModel
import torch

from typing import Any

tokenizer = AutoTokenizer.from_pretrained("facebook/mcontriever-msmarco")
model = AutoModel.from_pretrained("facebook/mcontriever-msmarco")


def mean_pooling(token_embeddings: torch.Tensor, mask: Any) -> torch.Tensor:
    """Mean Pooling - Take attention mask into account for correct averaging

    Args:
        token_embeddings (torch.Tensor): The embeddings for each token.
        mask (Any): The attention mask.

    Returns:
        The sentence embedding.
    """
    token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.0)
    sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
    return sentence_embeddings


def embed_contexts(data: str | pd.DataFrame, column: str = "text") -> pd.DataFrame:
    """Embeds the contexts from a csv file.

    Args:
        data (str | DataFrame): The path to a csv file or a pandas DataFrame.
        column (str, optional): The column name. Defaults to "text".

    Returns:
        A dictionary with the embeddings. Keys are the row indices and values are the embeddings.
    """

    if isinstance(data, str):
        df = pd.read_csv(data)[[column]]
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise TypeError("Data must be a path to a csv file or a pandas DataFrame")

    embeddings = dict()
    with alive_bar(len(df), title="Context Embedding") as bar:
        for index, row in df.iterrows():
            embeddings[index] = embed_text(row[column])[0]
            bar()
    df["embedding"] = df.index.map(embeddings)
    return df


def embed_text(sentence: str) -> list:
    """Embeds a question.

    Args:
        sentence (str): The sentence to be embedded.

    Returns:
        The embedding.
    """
    tokenized = tokenizer(sentence, padding=True, truncation=True, return_tensors="pt")
    outputs = model(**tokenized)
    embedding = mean_pooling(outputs[0], tokenized["attention_mask"]).tolist()
    return embedding
