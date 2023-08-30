import pickle
from flask import Flask, request, render_template, jsonify, send_file
from elasticsearch import Elasticsearch
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering, AutoModel
import spacy
import json
import time
from pymongo import MongoClient
import os
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

with open("config.json", "r") as config:
    config_variables = json.load(config)

all_models = dict()
all_elastics = dict()
all_ood_classes = dict()

for model in config_variables["models"]:
    all_models[model["model"]] = pipeline(
        model["pipeline"],
        tokenizer=model["tokenizer"],
        model=model["model"],
        device=model["device"],
        handle_impossible_answer=bool(model["handle_impossible_answer"]),
        max_answer_len=model["max_answer_len"],
    )

for elastic_table in config_variables["elastics"]:
    all_elastics[elastic_table["elastic_table_name"]] = elastic_table[
        "elastic_table_name"
    ]
    all_ood_classes[elastic_table["elastic_table_name"]] = elastic_table["ood_class"]

contriever_tokenizer = AutoTokenizer.from_pretrained("facebook/mcontriever-msmarco")
contriever_model = AutoModel.from_pretrained("facebook/mcontriever-msmarco")
ood_model = pickle.load(open("models/ood_model.pkl", "rb"))

nlp_hu = spacy.load("hu_core_news_trf")

MONGO_URL = os.environ.get("MONGO_URL")
ELASTIC_URL = os.environ.get("ELASTIC_URL")
ELASTIC_USER = os.environ.get("ELASTIC_USER")
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD")
ELASTIC_PASSWORD = "lFqLIrbCQfI84P6v_ue0"
DEBUG = os.environ.get("DEBUG", "").lower() == "true"


@app.route("/test")
def test():
    return jsonify({"Hello": "world!"}), 200


# @app.route('/query/<query>')
def predict_from_question(query, size, elastic, model_type):
    doc_q = nlp_hu(query)
    clean_tokens = list()

    for token in doc_q:
        # print(token.text, token.pos_, token.dep_)
        if token.pos_ not in ["DET", "ADV", "PRON", "PUNCT"]:
            clean_tokens.append(token.lemma_)

    clean_question = " ".join(clean_tokens)

    body = {"size": size, "query": {"match": {"document": clean_question}}}

    es = Elasticsearch(
        ELASTIC_URL, http_auth=(ELASTIC_USER, ELASTIC_PASSWORD), verify_certs=False
    )

    s = es.search(index=all_elastics[elastic], body=body)

    # The query only returns the text before the question mark, so we add it here.
    official_question = query if query[-1:] == "?" else query + "?"
    # We use the highest ranked document by the elasticsearch.
    contexts = list(s["hits"]["hits"])
    return_value = list()

    official_all_context = "\n-\n\n".join(
        context["_source"]["official_document"] for context in contexts
    )
    lemmatized_all_context = "\n-\n\n".join(
        context["_source"]["document"] for context in contexts
    )

    app.logger.info(contexts)

    qa_pipeline = all_models[model_type]

    if official_all_context != "":
        prediction = qa_pipeline(
            {"context": official_all_context, "question": official_question}
        )
    else:
        prediction = {"answer": "", "start": 0, "end": 0, "score": -1}

    
    if "\n-\n\n" in prediction["answer"]:
        model_answer = prediction["answer"].split("\n-\n\n")[0]
    else:
        model_answer = prediction["answer"]
        
    relevant_context = ""
    elastic_score = 0
    file_name, h1, h2, h3 = "", "", "", ""
    for context_raw in contexts:
        if context_raw["_source"]["official_document"].__contains__(model_answer):
            relevant_context = context_raw["_source"]["official_document"]
            elastic_score = context_raw["_score"]
            file_name = context_raw["_source"]["file_name"]
            h1 = context_raw["_source"]["h1"]
            h2 = context_raw["_source"]["h2"]
            h3 = context_raw["_source"]["h3"]
            break

    return_value.append(
        {
            "lemmatized_context": lemmatized_all_context,
            "official_question": official_question,
            "official_context": official_all_context,
            "relevant_context": relevant_context,
            "answer": prediction["answer"],
            "start": prediction["start"],
            "end": prediction["end"],
            "model_score": prediction["score"],
            "elastic_score": elastic_score,
            "metadata": [
                {"section": h2 + " > " + h3, "filename": file_name, "source": h1}
            ]
        }
    )

    return return_value


@app.route("/qa", methods=["POST"])
def rest_api():
    try:
        record = json.loads(request.data)
        if record["query"] == "":
            return jsonify({"answers": [], "system": {}})

        record["elapsed_time"] = time.time()
        ood_class = ood_model.predict(get_contriever_vector([record["query"]]).detach().numpy())[0].item()
        if (ood_class == all_ood_classes[record["elastic"]]):
            query = predict_from_question(
                record["query"], record["size"], record["elastic"], record["model_type"]
            )
            query[0]["ood_class"] = ood_class
        else:
            query = list([{"ood_class": ood_class}])
        record["elapsed_time"] = time.time() - record["elapsed_time"]

        record["time"] = time.time()
        mongo_id = str(
            db["qa"].insert_one({"answers": query, "system": record}).inserted_id
        )

        try:
            if not DEBUG:
                for answer in query:
                    del answer["lemmatized_context"]
                    del answer["official_question"]
                    del answer["official_context"]
                    del answer["model_score"]
                    del answer["elastic_score"]
                    del answer["ood_class"]
        except Exception as e:
            app.logger.error(e)
            db["errors"].insert_one(
                {"error": str(e), "time": time.time(), "type": "qa_delete_ood"}
            )

        return jsonify({"answers": query, "system": {"id": mongo_id}})
    except Exception as e:
        app.logger.error(e)
        db["errors"].insert_one({"error": str(e), "time": time.time(), "type": "qa"})
        return jsonify({}), 418


@app.route("/feedback/like", methods=["POST"])
def feedback_like():
    try:
        record = json.loads(request.data)
        db["likes"].insert_one({"id": record["id"], "time": time.time()})
        return jsonify({}), 200
    except Exception as e:
        app.logger.error(e)
        db["errors"].insert_one({"error": str(e), "time": time.time(), "type": "like"})
        return jsonify({}), 400


@app.route("/feedback/dislike", methods=["POST"])
def feedback_dislike():
    try:
        record = json.loads(request.data)
        db["dislikes"].insert_one(
            {
                "id": record["id"],
                "what_should_be": record["what_should_be"],
                "whats_wrong": record["whats_wrong"],
                "anything_else": record["anything_else"],
                "was_this_in_the_context": record["was_this_in_the_context"],
                "time": time.time(),
            }
        )
        return jsonify({}), 200
    except Exception as e:
        app.logger.error(e)
        db["errors"].insert_one(
            {"error": str(e), "time": time.time(), "type": "dislike"}
        )
        return jsonify({}), 400


def get_contriever_vector(sentences):
    inputs = contriever_tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

    outputs = contriever_model(**inputs)

    def mean_pooling(token_embeddings, mask):
        token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.0)
        sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
        return sentence_embeddings

    return mean_pooling(outputs[0], inputs["attention_mask"])


if __name__ == "__main__":
    client = MongoClient(MONGO_URL)
    db = client["shunqa"]
    app.run(host="0.0.0.0", port=5000, debug=True)
