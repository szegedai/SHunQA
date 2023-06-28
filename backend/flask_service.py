from flask import Flask, request, render_template, jsonify, send_file
from elasticsearch import Elasticsearch
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import spacy
import json
import time
from pymongo import MongoClient
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

with open('config.json', 'r') as config:
    config_variables = json.load(config)

all_models = dict()
all_elastics = dict()

for model in config_variables["models"]:
    all_models[model["model"]] = pipeline(model["pipeline"],
                                          tokenizer=model["tokenizer"],
                                          model=model["model"],
                                          device=model["device"],
                                          handle_impossible_answer=bool(model["handle_impossible_answer"]),
                                          max_answer_len=model["max_answer_len"])


for elastic_table in config_variables["elastics"]:
    all_elastics[elastic_table["elastic_table_name"]] = elastic_table["elastic_table_name"]

nlp_hu = spacy.load("hu_core_news_trf")

MONGO_URL = os.environ.get('MONGO_URL')

@app.route('/test')
def test():
    return jsonify({"Hello": "world!"}), 200

# @app.route('/query/<query>')
def predict_from_question(query, size, elastic, model_type):
    doc_q = nlp_hu(query)
    clean_tokens = list()

    for token in doc_q:
        # print(token.text, token.pos_, token.dep_)
        if token.pos_ not in ['DET', 'ADV', 'PRON', 'PUNCT']:
            clean_tokens.append(token.lemma_)

    clean_question = " ".join(clean_tokens)

    body = {
        "size": size,
        "query": {
            "match": {
                "document": clean_question
            }
        }
    }

    es = Elasticsearch(
        "http://rgai3.inf.u-szeged.hu:3427/",  # localhostra átírni tesztelésre
        http_auth=("elastic", "V7uek_ey6EdQbGBz_XHX"),
        verify_certs=False
    )

    s = es.search(index=all_elastics[elastic], body=body)

    # The query only returns the text before the question mark, so we add it here.
    official_question = query if query[-1:] == '?' else query + '?'
    # We use the highest ranked document by the elasticsearch.
    contexts = list(s['hits']['hits'])
    return_value = list()
    id = 0
    
    official_all_context = "\n-\n\n".join(context["_source"]["official_document"] for context in contexts)
    lemmatized_all_context = "\n-\n\n".join(context["_source"]["document"] for context in contexts)

    qa_pipeline = all_models[model_type]
    prediction = qa_pipeline({
        'context': official_all_context,
        'question': official_question
    })
    
    model_answer = prediction["answer"]
    
    relevant_context = ""
    elastic_score = 0
    for context_raw in contexts:
        if context_raw["_source"]["official_document"].__contains__(model_answer):
            relevant_context = context_raw["_source"]["official_document"]
            elastic_score = context_raw["_score"]
            break

    return_value.append({"lemmatized_context": lemmatized_all_context,
                            "official_question": official_question,
                            "official_context": official_all_context,
                            "relevant_context": relevant_context,
                            "answer": prediction['answer'],
                            "start": prediction['start'],
                            "end": prediction['end'],
                            "model_score": prediction['score'],
                            "elastic_score": elastic_score,
                            "id": id})

    return return_value


# @app.route('/qa/<query>')
# @app.route('/qa/', methods=['GET', 'POST'])
# def predict_from_question_gui():
#     if request.method == 'POST':
#         query = request.form["query"]
#         size = request.form["size"]
#         elastic = request.form["elastic"]
#         model_type = request.form["model_type"]

#         return render_template('index.html',
#                                data=predict_from_question(query, size, elastic, model_type),
#                                query=query,
#                                size=size,
#                                elastic=elastic,
#                                config_variables_elastics=config_variables["elastics"],
#                                model_type=model_type,
#                                config_variables_models=config_variables["models"])

#     return render_template('index.html',
#                            data=None,
#                            query=None,
#                            elastic=config_variables["elastics"][0]["elastic_table_name"],
#                            config_variables_elastics=config_variables["elastics"],
#                            model_type=config_variables["models"][0]["model"],
#                            config_variables_models=config_variables["models"])


@app.route('/qa', methods=['POST'])
def rest_api():
    try:
        record = json.loads(request.data)
        if (record["query"] == ""):
            return jsonify({"answers": [], "system": record})

        record["time"] = time.time()
        query = predict_from_question(record["query"], record["size"], record["elastic"], record["model_type"])
        record["time"] = time.time() - record["time"]

        record["id"] = str(db["qa"].insert_one({"answers": query, "system": record}).inserted_id)

        return jsonify({"answers": query, "system": record})
    except:
        return jsonify({}), 418


@app.route('/feedback/like', methods=['POST'])
def feedback_like():
    try:
        record = json.loads(request.data)
        db["likes"].insert_one({"id": record["id"], "time": time.time()})
        return jsonify({}), 200
    except:
        return jsonify({}), 400


@app.route('/feedback/dislike', methods=['POST'])
def feedback_dislike():
    try:
        record = json.loads(request.data)
        db["dislikes"].insert_one({
            "id": record["id"], 
            "what_should_be": record["what_should_be"],
            "whats_wrong": record["whats_wrong"],
            "anything_else": record["anything_else"],
            "was_this_in_the_context": record["was_this_in_the_context"],
            "time": time.time()
            })
        return jsonify({}), 200
    except:
        return jsonify({}), 400


# curl -X POST https://chatbot-rgai3.inf.u-szeged.hu/qa/api/ -H 'Content-Type: application/json' -d @./rest_api_example_files/data.json


if __name__ == '__main__':
    client = MongoClient(MONGO_URL)
    db = client["shunqa"]
    app.run(host='0.0.0.0', port=5000)
