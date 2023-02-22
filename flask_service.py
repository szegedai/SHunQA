from flask import Flask, request, render_template, jsonify, send_file
from elasticsearch import Elasticsearch
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import spacy
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

with open('config.json', 'r') as config:
    config_variables = json.load(config)


print("asuifhasiofhsduiorghsduioghsduopfiopghpdofhgpsodip")

all_models = dict()
for model in config_variables["models"]:
    all_models[model["visible_name"]] = pipeline(model["pipeline"],
                                                 tokenizer=model["tokenizer"],
                                                 model=model["model"],
                                                 device=model["device"],
                                                 handle_impossible_answer=bool(model["handle_impossible_answer"]),
                                                 max_answer_len=model["max_answer_len"])


nlp_hu = spacy.load("hu_core_news_trf")


@app.route('/query/<query>')
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

    s = es.search(index=elastic, body=body)

    # The query only returns the text before the question mark, so we add it here.
    official_question = query if query[-1:] == '?' else query + '?'
    # We use the highest ranked document by the elasticsearch.
    contexts = list(s['hits']['hits'])
    return_value = list()
    id = 0

    print(all_models[model_type])

    for context_raw in contexts:
        lemmatized_context = context_raw["_source"]["document"]
        official_context = context_raw["_source"]["official_document"]
        elastic_score = context_raw["_score"]

        qa_pipeline = all_models[model_type]

        print(qa_pipeline)

        prediction = qa_pipeline({
            'context': official_context,
            'question': official_question
        })

        return_value.append({"lemmatized_context": lemmatized_context,
                             "official_question": official_question,
                             "official_context": official_context,
                             "answer": prediction['answer'],
                             "start": prediction['start'],
                             "end": prediction['end'],
                             "model_score": prediction['score'],
                             "elastic_score": elastic_score,
                             "id": id})
        id += 1



    return return_value


# @app.route('/qa/<query>')
@app.route('/qa/', methods=['GET', 'POST'])
def predict_from_question_gui():
    if request.method == 'POST':
        query = request.form["query"]
        size = request.form["size"]
        elastic = request.form["elastic"]
        model_type = request.form["model_type"]

        return render_template('index.html',
                               data=predict_from_question(query, size, elastic, model_type),
                               query=query,
                               size=size,
                               elastic=elastic,
                               model_type=model_type,
                               config_variables=config_variables["models"])

    return render_template('index.html',
                           data=None,
                           query=None,
                           model_type=config_variables["models"][0]["visible_name"],
                           config_variables=config_variables["models"])


@app.route('/qa/api/', methods=['GET', 'POST'])
def rest_api():
    try:
        record = json.loads(request.data)
        query = predict_from_question(record["query"], record["size"], record["elastic"], record["model_type"])

        app.logger.info(record)
        return jsonify(query)
    except:
        return jsonify({}), 418


# curl -X POST https://chatbot-rgai3.inf.u-szeged.hu/qa/api/ -H 'Content-Type: application/json' -d @./rest_api_example_files/data.json


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
