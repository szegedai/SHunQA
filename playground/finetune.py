from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import pandas as pd
import random as rd

# model = SentenceTransformer("facebook/mcontriever-msmarco")
model = SentenceTransformer("sentence-transformers/LaBSE")
rd.seed(42)


def load_data(path):
    df = pd.read_csv(path)[["context", "question"]]
    data = list()
    for _, row in df.iterrows():
        temp = df.drop_duplicates(subset="context", inplace=False)
        temp = temp.loc[temp["context"] != row["context"]]
        neg = rd.sample(list(temp["context"]), 1)[0]
        data.append({"query": row["question"], "pos": row["context"], "neg": neg})
    return data


def load_telekom_hr(path):
    data = list()
    df = pd.read_json(path, lines=True)
    for index, row in df.iterrows():
        for _, pos_row in df[
            (df.loc[index:,"answer"] == row["answer"]) & (df["question"] != row["question"])
        ].iterrows():
            temp = df[df["answer"] != row["answer"]]
            neg = rd.sample(list(temp["question"]), 1)[0]
            data.append(
                {"query": row["question"], "pos": pos_row["question"], "neg": neg}
            )
            
    return data

if __name__ == "__main__":
    # train, eval = train_test_split(
    #     load_data("train_short.csv"), test_size=0.2, random_state=42, shuffle=True
    # )
    train, eval = train_test_split(
        load_telekom_hr("data/hr_adatszett.jsonl"),
        test_size=0.2,
        random_state=42,
        shuffle=True,
    )

    train_examples = list()

    for i in range(len(train)):
        train_examples.append(
            InputExample(texts=[train[i]["query"], train[i]["pos"], train[i]["neg"]])
        )

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=1)
    train_loss = losses.TripletLoss(model=model)

    eval_examples = list()
    eval_examples.append(list())
    eval_examples.append(list())
    eval_examples.append(list())

    for i in range(len(eval)):
        eval_examples[0].append(eval[i]["query"])
        eval_examples[1].append(eval[i]["pos"])
        eval_examples[2].append(eval[i]["neg"])

    evaluator = evaluation.TripletEvaluator(    
        eval_examples[0],
        eval_examples[1],
        eval_examples[2],
        batch_size=1,
        show_progress_bar=True,
    )

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=10,
        output_path="model/labse",
    )

    # model.save("models/")
