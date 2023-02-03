import pandas as pd
from elasticsearch import Elasticsearch
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import tqdm


tokenizer = AutoTokenizer.from_pretrained("ZTamas/hubert-qa-milqa")
model = AutoModelForQuestionAnswering.from_pretrained("ZTamas/hubert-qa-milqa")
qa_pipeline = pipeline(
    "question-answering",
    model=model,
    tokenizer=tokenizer
)


def predict_from_questions_k(k_numbers: list[int], file_name):
    df = pd.read_csv(file_name, delimiter=";")
    questions = df["question"]
    es = Elasticsearch(
        "http://rgai3.inf.u-szeged.hu:3427/",  # localhostra átírni tesztelésre
        http_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
        verify_certs=False
    )
    match_scores = dict()
    for k in k_numbers:
        match_scores[k] = []
        return_value = list()
        for index, question in tqdm.tqdm(enumerate(questions)):

            body = {
                "size": k,
                "query": {
                    "match": {
                        "document": question
                    }
                }
            }
            s = es.search(index='milqa', body=body)
            contexts = list(s['hits']['hits'])
            context = ""
            for context_raw in contexts:
                context += " " + context_raw["_source"]["document"]

            prediction = qa_pipeline({
                'context': context,
                'question': question
            })

            return_value.append({"context": context,
                                 "question": question,
                                 "answer": prediction['answer'],
                                 "start": prediction['start'],
                                 "end": prediction['end'],
                                 "score": prediction['score']
                                 })

        match_scores[k].append(get_matches(df["gold_answer"], df["prediction"], return_value, k_number=k))

        f1 = 0
        compute = 0
        for i, pred in enumerate(return_value):
            f1 += compute_f1(pred['answer'], df.iloc[i]['gold_answer'])
            compute += compute_exact_match(pred['answer'], df.iloc[i]['gold_answer'])

        f1 = (f1 / len(return_value))
        compute = (compute / len(return_value))
        print(k, "\n", f'f1 score:   ', f1, '\nexact match:', compute)

    return match_scores


def get_matches(gold_answer, predicted, elastic_predicted, k_number):
    match_scores = {"z_same_as_gold_count": 0,
                    "z_same_as_predicted_count": 0,
                    "z_entirely_different_count": 0,
                    "same_as_gold": [],
                    "same_as_predicted": [],
                    "entirely_different": [],
                    "k_number": k_number}

    for i, e_pred in enumerate(elastic_predicted):
        elastic_predicted_i = dict()
        elastic_predicted_i["question"] = e_pred["question"]
        elastic_predicted_i["answer"] = e_pred["answer"]
        elastic_predicted_i["score"] = e_pred["score"]
        if elastic_predicted_i["answer"] == gold_answer[i]:
            match_scores["same_as_gold"].append(elastic_predicted_i)
            match_scores["z_same_as_gold_count"] += 1

        elif elastic_predicted_i["answer"] == predicted[i]:
            match_scores["same_as_predicted"].append(elastic_predicted_i)
            match_scores["z_same_as_predicted_count"] += 1

        else:
            match_scores["entirely_different"].append(elastic_predicted_i)
            match_scores["z_entirely_different_count"] += 1

    return match_scores


def normalize_text(s):
    """Removing articles and punctuation, and standardizing whitespace are all typical text processing steps."""
    import string, re

    def remove_articles(text):
        regex = re.compile(r"\b(a|an|the)\b", re.UNICODE)
        return re.sub(regex, " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def compute_exact_match(prediction, truth):
    return int(normalize_text(prediction) == normalize_text(truth))


def compute_f1(prediction, truth):
    pred_tokens = normalize_text(prediction).split()
    truth_tokens = normalize_text(truth).split()

    # if either the prediction or the truth is no-answer then f1 = 1 if they agree, 0 otherwise
    if len(pred_tokens) == 0 or len(truth_tokens) == 0:
        return int(pred_tokens == truth_tokens)

    common_tokens = set(pred_tokens) & set(truth_tokens)

    # if there are no common tokens then f1 = 0
    if len(common_tokens) == 0:
        return 0

    prec = len(common_tokens) / len(pred_tokens)
    rec = len(common_tokens) / len(truth_tokens)

    return 2 * (prec * rec) / (prec + rec)


if __name__ == '__main__':
    print(predict_from_questions_k([1], "../pred_test.csv"))