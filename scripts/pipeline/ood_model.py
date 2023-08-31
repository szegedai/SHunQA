import pickle
from typing import List

import fire
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer


print("Loading model...")
TOKENIZER = AutoTokenizer.from_pretrained("facebook/mcontriever-msmarco")
MODEL = AutoModel.from_pretrained("facebook/mcontriever-msmarco")


def get_contriever_vector(sentences: List[str]) -> torch.Tensor:
    inputs = TOKENIZER(sentences, padding=True, truncation=True, return_tensors="pt")

    outputs = MODEL(**inputs)

    def mean_pooling(
        token_embeddings: torch.Tensor, mask: torch.Tensor
    ) -> torch.Tensor:
        token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.0)
        sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
        return sentence_embeddings

    return mean_pooling(outputs[0], inputs["attention_mask"])


def get_contriever_vector_split(sentences: List[str]) -> np.ndarray:
    all_vectors = np.concatenate(
        [
            get_contriever_vector(split.tolist()).detach().numpy()
            for split in tqdm(
                np.array_split(sentences, 100 if len(sentences) > 200 else 1)
            )
        ]
    )
    return all_vectors


class OOD:
    def train(self) -> None:
        good_examples = (
            pd.read_csv("data/4ig_smaller_snippets.csv")["Kérdések"].unique().tolist()
        )
        wrong_examples = pd.read_csv("data/merged.csv")["question"].unique().tolist()

        X = (
            good_examples
            + pd.DataFrame(wrong_examples)
            .sample(frac=1, random_state=42)[: len(good_examples)][0]
            .tolist()
        )
        y = [1] * len(good_examples) + [0] * len(good_examples)

        X_contriever = get_contriever_vector_split(X)
        (
            X_train_contriever,
            X_test_contriever,
            y_train_contriever,
            y_test_contriever,
        ) = train_test_split(X_contriever, y, test_size=0.20, random_state=42)

        X2 = (
            pd.DataFrame(wrong_examples)
            .sample(frac=1, random_state=42)[len(good_examples) :][0]
            .tolist()
        )
        X2_contriever = get_contriever_vector_split(X2)

        X3_train = (
            X_train_contriever.tolist()
            + X2_contriever[int(len(X2_contriever) * 0.2) :].tolist()
        )
        X3_test = (
            X_test_contriever.tolist()
            + X2_contriever[: int(len(X2_contriever) * 0.2)].tolist()
        )

        y3_train = y_train_contriever + [0] * len(
            X2_contriever[int(len(X2_contriever) * 0.2) :]
        )
        y3_test = y_test_contriever + [0] * len(
            X2_contriever[: int(len(X2_contriever) * 0.2)]
        )

        clf = LogisticRegression(class_weight="balanced")
        clf.fit(X3_train, y3_train)

        y_pred2 = clf.predict(X3_test)
        print(classification_report(y3_test, y_pred2))
        print(confusion_matrix(y3_test, y_pred2))

        with open("../../backend/models/good_model.pkl", "wb") as f:
            pickle.dump(clf, f)

    def predict(self) -> None:
        try:
            with open("../../backend/models/good_model.pkl", "rb") as f:
                clf = pickle.load(f)
        except:
            print("Train the model first!")
            return

        while True:
            sentence = input("Enter a sentence (type 'exit' to quit): ")
            if sentence == "exit":
                break

            print(clf.predict(get_contriever_vector([sentence]).tolist())[0])


if __name__ == "__main__":
    fire.Fire(OOD)
